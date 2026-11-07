"""Build small executable macOS .app installers without requiring a Mac to package."""
from pathlib import Path
import argparse
import hashlib
import io
import json
import plistlib
import zipfile

ROOT = Path(__file__).resolve().parents[1]
RELEASE = ROOT / 'outputs/desktop-release'


def build(arch, output_dir=None):
    pins = json.loads((ROOT / 'desktop/micromamba.json').read_text(encoding='utf-8'))
    pin = pins[arch]
    platform = 'macOS-AppleSilicon' if arch == 'arm64' else 'macOS-Intel'
    client = io.BytesIO()
    with zipfile.ZipFile(client, 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        archive.write(ROOT / 'desktop/app.py', 'app.py')
        archive.write(ROOT / 'desktop/mac_smoke_test.py', 'mac_smoke_test.py')
        archive.write(ROOT / 'esphome-smart-clock.yaml', 'firmware/esphome-smart-clock.yaml')
        for name in ('src', 'media', 'components'):
            for file in sorted((ROOT / name).rglob('*')):
                if file.is_file() and '__pycache__' not in file.parts and file.suffix != '.pyc':
                    archive.write(file, 'firmware/' + file.relative_to(ROOT).as_posix())
    content = client.getvalue()
    client_hash = hashlib.sha256(content).hexdigest()
    template = (ROOT / 'desktop/macos_setup.command').read_text(encoding='utf-8')
    esphome_pin = (ROOT / 'ESPHOME_VERSION').read_text(encoding='utf-8').strip()
    identity = hashlib.sha256((client_hash + arch + template + json.dumps(pin, sort_keys=True) + esphome_pin).encode()).hexdigest()[:20]
    config = {'ARCH': arch, 'BUILD_ID': identity, 'CLIENT_SHA': client_hash, 'MAMBA_URL': pin['url'],
              'MAMBA_SHA': pin['sha256'], 'MAMBA_SIZE': str(pin['size']), 'MAMBA_BINARY_SHA': pin['binary_sha256'],
              'ESPHOME_PIN': esphome_pin}
    script = template
    for key, value in config.items():
        script = script.replace('@' + key + '@', value)
    launcher = '''#!/bin/bash
set -eu
RESOURCES="$(CDPATH='' cd -- "$(dirname -- "$0")/../Resources" && pwd -P)"
if [ -f "$HOME/.local/share/smartclock/runtime/@BUILD_ID@/.complete" ]; then
  if /bin/bash "$RESOURCES/setup.command" --launch-only; then exit 0; fi
fi
exec /usr/bin/open -a Terminal "$RESOURCES/setup.command"
'''.replace('@BUILD_ID@', identity)
    bundle = 'Smart Clock Setup.app/Contents/'
    files = {
        bundle + 'Info.plist': (plistlib.dumps(dict(CFBundleName='Smart Clock Setup', CFBundleExecutable='SmartClock',
            CFBundleIdentifier='com.nirby.smartclock.setup', CFBundlePackageType='APPL', CFBundleVersion='1',
            LSMinimumSystemVersion='12.0', NSHighResolutionCapable=True)), 0o644),
        bundle + 'MacOS/SmartClock': (launcher.encode(), 0o755),
        bundle + 'Resources/setup.command': (script.encode(), 0o755),
        bundle + 'Resources/client.zip': (content, 0o644),
        'READ ME.txt': (b'Extract and open Smart Clock Setup.app. First setup opens Terminal automatically; no commands need typing. Keep Internet connected. Later launches open the clock GUI directly. Unsigned preview: if blocked, use macOS Privacy & Security > Open Anyway for this app. No Python, Java, Homebrew or Xcode installation is needed. Setup details: ~/Library/Logs/SmartClock/setup.log.\n', 0o644)
    }
    destination = Path(output_dir) if output_dir is not None else RELEASE
    destination.mkdir(parents=True, exist_ok=True)
    output = destination / f'SmartClock-{platform}.zip'
    with zipfile.ZipFile(output, 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for name, (data, mode) in files.items():
            info = zipfile.ZipInfo(name)
            info.create_system = 3
            info.external_attr = (0o100000 | mode) << 16
            info.compress_type = zipfile.ZIP_DEFLATED
            archive.writestr(info, data)
    digest = hashlib.sha256(output.read_bytes()).hexdigest()
    output.with_suffix('.sha256').write_text(f'{digest}  {output.name}\n', encoding='ascii')
    (ROOT / 'outputs' / f'{platform}-installer.json').write_text(json.dumps(dict(identity=identity, arch=arch, asset=str(output)), indent=2))
    print(f'{output}: {output.stat().st_size:,} bytes', flush=True)
    return output


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--arch', choices=['arm64', 'x86_64', 'all'], default='all')
    selected = parser.parse_args().arch
    for arch in (['arm64', 'x86_64'] if selected == 'all' else [selected]):
        build(arch)
