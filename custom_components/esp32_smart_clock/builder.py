"""Small client for the documented ESPHome Device Builder WebSocket API.

Never sends device credentials to GitHub. Only the explicitly marked release
substitution is changed; the builder retains its local secrets and overrides.
"""
import asyncio
import re
from urllib.parse import urlsplit
import aiohttp

RELEASE = re.compile(r'^v?[0-9]+\.[0-9]+\.[0-9]+(?:-beta\.[0-9]+)?$')
PIN = re.compile(r'^(  smart_clock_release: )([\"\x27]?)(v[0-9]+\.[0-9]+\.[0-9]+(?:-beta\.[0-9]+)?)(\2)([ \t]*(?:#.*)?)$', re.M)

class BuilderError(Exception):
    """Safe message containing no config, credentials or build logs."""

def pin_release(content, version):
    if not RELEASE.fullmatch(version):
        raise BuilderError('Unsupported release version')
    if len(PIN.findall(content)) != 1 or 'ref: ${smart_clock_release}' not in content:
        raise BuilderError('Use the managed examples/clock.yaml package configuration first')
    return PIN.sub(lambda m: m[1] + m[2] + 'v' + version.removeprefix('v') + m[4] + m[5], content)

def validate_url(url):
    parsed = urlsplit(url)
    if parsed.scheme not in ('http', 'https') or not parsed.hostname or parsed.username or parsed.password or parsed.query or parsed.fragment:
        raise BuilderError('Enter the builder HTTP(S) URL without embedded credentials')
    return url.rstrip('/')

class Builder:
    def __init__(self, session, url, username='', password=''):
        self.session = session
        self.url = validate_url(url)
        self.username, self.password = username, password
        self.ws = None
        self.sequence = 0

    async def __aenter__(self):
        self.ws = await self.session.ws_connect(self.url + '/ws', heartbeat=30, max_msg_size=16*1024*1024)
        try:
            greeting = await self.ws.receive_json(timeout=20)
            if greeting.get('requires_auth'):
                await self.call('auth/login', username=self.username, password=self.password)
        except BaseException:
            await self.ws.close()
            raise
        return self

    async def __aexit__(self, *args):
        await self.ws.close()

    async def call(self, command, **args):
        self.sequence += 1
        message_id = str(self.sequence)
        await self.ws.send_json(dict(command=command, message_id=message_id, args=args))
        async with asyncio.timeout(120):
            while True:
                reply = await self.ws.receive_json()
                if reply.get('message_id') != message_id:
                    continue
                if 'error_code' in reply:
                    # Server error details may echo YAML secrets; never expose them.
                    raise BuilderError(f'Builder rejected {command}: {reply["error_code"]}')
                if 'result' in reply:
                    return reply['result']

    async def resolved(self, configuration):
        auth = aiohttp.BasicAuth(self.username, self.password) if self.username else None
        async with self.session.get(self.url + '/json-config', params={'configuration': configuration}, auth=auth, timeout=aiohttp.ClientTimeout(total=120), allow_redirects=False) as response:
            if response.status != 200:
                raise BuilderError('Builder could not resolve the personalized YAML')
            return await response.json()

    async def prepare(self, configuration, version, device_name, noise_psk):
        jobs = await self.call('firmware/get_jobs', configuration=configuration)
        if any(job['status'] in ('queued', 'running') for job in jobs):
            raise BuilderError('This clock already has an active builder job; wait for it to finish')
        original = await self.call('devices/get_config', configuration=configuration)
        replacement = pin_release(original, version)
        await self.call('devices/update_config', configuration=configuration, content=replacement, expected=original)
        try:
            config = await self.resolved(configuration)
            project = config.get('esphome', {}).get('project', {})
            if project.get('name') != 'nirby.esp32_smart_clock' or project.get('version') != version:
                raise BuilderError('Resolved package does not match the requested Smart Clock release')
            if config.get('esphome', {}).get('name') != device_name:
                raise BuilderError('Builder YAML belongs to a different clock')
            if not noise_psk or config.get('api', {}).get('encryption', {}).get('key') != noise_psk:
                raise BuilderError('Builder encryption key does not match the paired clock')
        except BaseException:
            # Compare-and-swap prevents overwriting a concurrent user edit.
            await self.call('devices/update_config', configuration=configuration, content=original, expected=replacement)
            raise

    async def install(self, configuration, progress):
        job = await self.call('firmware/install', configuration=configuration, port='OTA', force_local=True)
        job_id = job['job_id']
        async with asyncio.timeout(3600):
            while True:
                jobs = await self.call('firmware/get_jobs', configuration=configuration)
                chain = [j for j in jobs if j['job_id'] == job_id or j.get('depends_on') == job_id]
                if any(j['status'] in ('failed', 'cancelled') for j in chain):
                    raise BuilderError('Build or upload failed; inspect the local ESPHome builder logs')
                upload = next((j for j in chain if j['job_type'] == 'upload'), None)
                progress('Uploading' if upload and upload['status'] == 'running' else 'Building')
                if upload and upload['status'] == 'completed':
                    return
                await asyncio.sleep(3)
