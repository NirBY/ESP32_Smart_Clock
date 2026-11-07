"""Reject installers containing stale application or firmware source files."""
from pathlib import Path
import argparse
import hashlib
import json
import re
import zipfile

ROOT = Path(__file__).resolve().parents[1]


def verify(package):
    expected = {'app.py': ROOT / 'desktop/app.py',
                'firmware/esphome-smart-clock.yaml': ROOT / 'esphome-smart-clock.yaml'}
    for folder in ('src', 'media', 'components'):
        for file in (ROOT / folder).rglob('*'):
            if file.is_file() and '__pycache__' not in file.parts and file.suffix != '.pyc':
                expected['firmware/' + file.relative_to(ROOT).as_posix()] = file
    with zipfile.ZipFile(package) as archive:
        actual = {name for name in archive.namelist() if name.startswith('firmware/') and not name.endswith('/')}
        assert actual == {name for name in expected if name.startswith('firmware/')}, 'Unexpected or missing firmware files'
        for name, source in expected.items():
            assert archive.read(name) == source.read_bytes(), f'Stale packaged source: {name}'
        assert not any('secrets.yaml' in name for name in archive.namelist()), 'Private secrets packaged'
    print(f'Verified {len(expected)} packaged source files against release checkout: {package}')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('package', nargs='?')
    args = parser.parse_args()
    if args.package:
        verify(Path(args.package))
    else:
        metadata = json.loads((ROOT / 'outputs/onefile-build/web-installer.json').read_text())
        package = ROOT / 'outputs/desktop-release' / metadata['asset']
        assert hashlib.sha256(package.read_bytes()).hexdigest() == metadata['sha256']
        with zipfile.ZipFile(package) as archive:
            pins = [name for name in archive.namelist() if re.fullmatch(r'runtime/Lib/site-packages/esphome-[^/]+\.dist-info/METADATA', name)]
            assert len(pins) == 1, 'Expected exactly one installed ESPHome distribution'
            installed = re.search(r'^Version: (.+)$', archive.read(pins[0]).decode(), re.M).group(1).strip()
            assert installed == (ROOT / 'ESPHOME_VERSION').read_text().strip(), 'Packaged ESPHome differs from release pin'
        version = __import__('re').search(r'firmware_version:\s*"([^"]+)"', (ROOT / 'esphome-smart-clock.yaml').read_text()).group(1)
        assert f'/v{version}/' in metadata['url'], 'Installer URL targets a different release'
        installer = ROOT / 'outputs/desktop-release/SmartClock-Windows-x64.exe'
        binary = installer.read_bytes()
        for value in (metadata['sha256'], metadata['url']):
            assert value.encode('utf-16le') in binary, 'EXE does not reference the verified runtime'
        assert installer.with_suffix('.sha256').read_text().split()[0] == hashlib.sha256(binary).hexdigest()
        verify(package)
