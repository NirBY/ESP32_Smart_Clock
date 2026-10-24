"""Updater safety and job handling, without a live clock or Home Assistant."""
import asyncio
import importlib.util
from pathlib import Path
import unittest

spec = importlib.util.spec_from_file_location('builder', Path(__file__).parents[1] / 'custom_components/esp32_smart_clock/builder.py')
b = importlib.util.module_from_spec(spec)
spec.loader.exec_module(b)
YAML = 'substitutions:\n  smart_clock_release: "v0.1.0-beta.18" # keep\n  wifi_password: !secret wifi_password\npackages:\n  clock:\n    ref: ${smart_clock_release}\n'

class Pins(unittest.TestCase):
    def test_only_pin_changes(self):
        self.assertEqual(b.pin_release(YAML, '0.1.0-beta.19'), YAML.replace('beta.18', 'beta.19'))

    def test_reject_unmanaged_or_invalid(self):
        for text, version in [(YAML, '../../main'), ('wifi: {}', '0.1.0-beta.19'), (YAML + YAML, '0.1.0-beta.19')]:
            with self.assertRaises(b.BuilderError):
                b.pin_release(text, version)

    def test_urls(self):
        for url in ['file:///etc/passwd', 'http://user:pass@host', 'https://host/?token=x']:
            with self.assertRaises(b.BuilderError):
                b.validate_url(url)
        self.assertEqual(b.validate_url('https://builder:6052/'), 'https://builder:6052')

class Fake(b.Builder):
    def __init__(self):
        self.content = YAML
        self.calls = []
        self.config = {'esphome': {'name': 'clock', 'project': {'name': 'nirby.esp32_smart_clock', 'version': '0.1.0-beta.19'}}, 'api': {'encryption': {'key': 'private-key'}}}
        self.jobs = [{'job_id': 'compile', 'status': 'completed', 'job_type': 'compile'}, {'job_id': 'upload', 'depends_on': 'compile', 'status': 'completed', 'job_type': 'upload'}]

    async def call(self, command, **args):
        self.calls.append(command)
        if command == 'devices/get_config':
            return self.content
        if command == 'devices/update_config':
            if self.content != args['expected']:
                raise b.BuilderError('Concurrent edit')
            self.content = args['content']
        if command == 'firmware/install':
            assert args['force_local'] is True
            assert args['port'] == 'OTA'
            return {'job_id': 'compile'}
        if command == 'firmware/get_jobs':
            return self.jobs

    async def resolved(self, configuration):
        return self.config

class Jobs(unittest.IsolatedAsyncioTestCase):
    async def test_existing_job_prevents_config_change(self):
        builder = Fake()
        builder.jobs[0]['status'] = 'running'
        with self.assertRaises(b.BuilderError):
            await builder.prepare('clock.yaml', '0.1.0-beta.19', 'clock', 'private-key')
        self.assertNotIn('devices/update_config', builder.calls)

    async def test_prepare_keeps_credentials(self):
        builder = Fake()
        await builder.prepare('clock.yaml', '0.1.0-beta.19', 'clock', 'private-key')
        self.assertIn('!secret wifi_password', builder.content)
        self.assertNotIn('firmware/install', builder.calls)

    async def test_identity_key_and_version_mismatch_restore_pin(self):
        for name, key, version in [('other-clock', 'private-key', '0.1.0-beta.19'), ('clock', 'wrong-key', '0.1.0-beta.19'), ('clock', 'private-key', '0.1.0-beta.20')]:
            builder = Fake()
            with self.assertRaises(b.BuilderError):
                await builder.prepare('clock.yaml', version, name, key)
            self.assertEqual(builder.content, YAML)
            self.assertNotIn('firmware/install', builder.calls)

    async def test_complete_upload(self):
        await Fake().install('clock.yaml', lambda phase: None)

    async def test_failed_compile_never_success(self):
        builder = Fake()
        builder.jobs[0]['status'] = 'failed'
        with self.assertRaises(b.BuilderError):
            await builder.install('clock.yaml', lambda phase: None)

    async def test_cancelled_upload_never_success(self):
        builder = Fake()
        builder.jobs[1]['status'] = 'cancelled'
        with self.assertRaises(b.BuilderError):
            await builder.install('clock.yaml', lambda phase: None)

if __name__ == '__main__':
    unittest.main()
