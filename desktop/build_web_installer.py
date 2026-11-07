"""Build a tiny, checksum-pinned online installer and its release runtime asset."""
from pathlib import Path
import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import zipfile

ROOT = Path(__file__).resolve().parents[1]
WORK = ROOT / 'outputs/onefile-build'
RELEASE = ROOT / 'outputs/desktop-release'


def build(url=None, test=False, refresh=False):
    payload = WORK / 'payload.zip'
    if refresh:
        temporary = WORK / 'payload.updated.zip'
        replacements = {'prepare_runtime.py': ROOT / 'desktop/prepare_runtime.py', 'app.py': ROOT / 'desktop/app.py',
                        'USER-GUIDE.txt': ROOT / 'docs/wiki/Desktop-App.md', 'smoke_test.py': ROOT / 'desktop/smoke_test.py'}
        with zipfile.ZipFile(payload) as source, zipfile.ZipFile(temporary, 'w', compresslevel=6) as target:
            for entry in source.infolist():
                data = replacements[entry.filename].read_bytes() if entry.filename in replacements else source.read(entry)
                target.writestr(entry, data)
        temporary.replace(payload)
    with payload.open('rb') as stream:
        digest = hashlib.file_digest(stream, 'sha256').hexdigest()
    identity = digest[:24]
    asset = f'SmartClock-runtime-Windows-x64-{identity}.zip'
    RELEASE.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(payload, RELEASE / asset)
    version = re.search(r'firmware_version:\s*"([^"]+)"', (ROOT / 'outputs/SmartClock-Windows/firmware/esphome-smart-clock.yaml').read_text(encoding='utf-8')).group(1)
    tag = os.environ.get('DESKTOP_RELEASE_TAG', '')
    if not re.fullmatch(r'[vV]?\d+\.\d+\.\d+(?:-beta\.\d+)?', tag):
        tag = 'v' + version
    url = url or f'https://github.com/NirBY/ESP32_Smart_Clock/releases/download/{tag}/{asset}'
    if not test and not url.startswith('https://github.com/NirBY/ESP32_Smart_Clock/releases/download/'):
        raise ValueError('Production runtime must come from the official HTTPS release assets')
    source = (ROOT / 'desktop/onefile_launcher.cs').read_text(encoding='utf-8')
    for key, value in {'PAYLOAD_ID': identity, 'PAYLOAD_SHA256': digest, 'PAYLOAD_URL': url, 'PAYLOAD_SIZE': str(payload.stat().st_size)}.items():
        source = source.replace(key, value)
    generated = WORK / ('web-preview.cs' if test else 'web-installer.cs')
    generated.write_text(source, encoding='utf-8')
    output = (ROOT / 'outputs/web-preview/SmartClock-Local-Setup.exe') if test else RELEASE / 'SmartClock-Windows-x64.exe'
    output.parent.mkdir(parents=True, exist_ok=True)
    compiler = Path('C:/Windows/Microsoft.NET/Framework64/v4.0.30319/csc.exe')
    subprocess.run([str(compiler), '/nologo', '/target:winexe', '/optimize+',
                    '/define:WEB_INSTALLER' + (';TEST_DOWNLOAD' if test else ''),
                    '/reference:System.Windows.Forms.dll', '/reference:System.Drawing.dll',
                    '/reference:System.IO.Compression.dll', '/out:' + str(output),
                    str(generated), str(ROOT / 'desktop/reliable_download.cs')], check=True)
    with output.open('rb') as stream:
        exe_hash = hashlib.file_digest(stream, 'sha256').hexdigest()
    output.with_suffix('.sha256').write_text(f'{exe_hash}  {output.name}\n', encoding='ascii')
    (RELEASE / (asset + '.sha256')).write_text(f'{digest}  {asset}\n', encoding='ascii')
    metadata = dict(identity=identity, sha256=digest, size=payload.stat().st_size, asset=asset, url=url, installer=str(output))
    (WORK / ('web-preview.json' if test else 'web-installer.json')).write_text(json.dumps(metadata, indent=2), encoding='utf-8')
    print(f'{output}: {output.stat().st_size:,} bytes; runtime downloaded on first use', flush=True)
    return metadata


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--test-url')
    parser.add_argument('--refresh-payload', action='store_true')
    args = parser.parse_args()
    build(args.test_url, bool(args.test_url), args.refresh_payload)
