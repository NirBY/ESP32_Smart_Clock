"""One universal online-setup DMG for both Apple Silicon and Intel Macs."""
from pathlib import Path
import hashlib
import importlib.util
import json
import os
import re
import subprocess
import sys
import tempfile
import zipfile

ROOT = Path(__file__).resolve().parents[1]
WORK = ROOT / 'outputs/macos-dmg-build'
RELEASE = ROOT / 'outputs/desktop-release'


def module(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / 'desktop' / (name + '.py'))
    loaded = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(loaded)
    return loaded


def build():
    WORK.mkdir(parents=True, exist_ok=True)
    RELEASE.mkdir(parents=True, exist_ok=True)
    builder = module('build_macos_online')
    archives = {arch: builder.build(arch, WORK / 'internal-zips') for arch in ('arm64', 'x86_64')}
    prefix = 'Smart Clock Setup.app/Contents/'
    scripts = {}
    identities = {}
    common = None
    for arch, path in archives.items():
        with zipfile.ZipFile(path) as archive:
            data = archive.read(prefix + 'Resources/client.zip')
            if common is None:
                common = data
                plist = archive.read(prefix + 'Info.plist')
            elif common != data:
                raise RuntimeError('Source changed while building the universal installer. Retry the build.')
            script = archive.read(prefix + 'Resources/setup.command')
            scripts[arch] = script
            identities[arch] = re.search(rb"BUILD_ID='([a-f0-9]+)'", script)[1].decode()
    dispatcher = '''#!/bin/bash
set -eu
RESOURCES="$(CDPATH='' cd -- "$(dirname -- "$0")" && pwd -P)"
if [ "$(/usr/sbin/sysctl -n hw.optional.arm64 2>/dev/null || printf 0)" = 1 ]; then
  exec /usr/bin/arch -arm64 /bin/bash "$RESOURCES/setup-arm64.command" "$@"
fi
exec /bin/bash "$RESOURCES/setup-x86_64.command" "$@"
'''
    launcher = '''#!/bin/bash
set -eu
RESOURCES="$(CDPATH='' cd -- "$(dirname -- "$0")/../Resources" && pwd -P)"
SCRIPT="$RESOURCES/setup.command"
if [ "$(/usr/sbin/sysctl -n hw.optional.arm64 2>/dev/null || printf 0)" = 1 ]; then
  BUILD_ID='@ARM_ID@'
else
  BUILD_ID='@INTEL_ID@'
fi
if [ -f "$HOME/.local/share/smartclock/runtime/$BUILD_ID/.complete" ]; then
  if /bin/bash "$SCRIPT" --launch-only; then exit 0; fi
fi
exec /usr/bin/open -a Terminal "$SCRIPT"
'''.replace('@ARM_ID@', identities['arm64']).replace('@INTEL_ID@', identities['x86_64'])
    files = {
        prefix + 'Info.plist': (plist, 0o644),
        prefix + 'MacOS/SmartClock': (launcher.encode(), 0o755),
        prefix + 'Resources/client.zip': (common, 0o644),
        prefix + 'Resources/setup.command': (dispatcher.encode(), 0o755),
        prefix + 'Resources/setup-arm64.command': (scripts['arm64'], 0o755),
        prefix + 'Resources/setup-x86_64.command': (scripts['x86_64'], 0o755),
        'READ ME.txt': (b'Open Smart Clock Setup.app in this window. Apple Silicon and Intel are detected automatically. Keep the disk image mounted until first setup finishes. Setup downloads components automatically; no Python, Java, Homebrew or Xcode installation is required. First setup opens an automated Terminal window; no commands need typing. Your clock settings are kept separately. Unsigned preview: use System Settings > Privacy & Security > Open Anyway for this app if macOS blocks it.\n', 0o644)
    }
    output = RELEASE / 'SmartClock-macOS.dmg'
    with tempfile.TemporaryDirectory(prefix='volume-', dir=WORK) as temp:
        staging = Path(temp)
        for name, (data, mode) in files.items():
            target = staging / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)
            target.chmod(mode)
        if sys.platform == 'darwin':
            subprocess.run(['/usr/bin/hdiutil', 'create', '-ov', '-volname', 'Smart Clock Setup', '-srcfolder', str(staging), '-fs', 'HFS+', '-format', 'UDZO', str(output)], check=True)
            subprocess.run(['/usr/bin/hdiutil', 'verify', str(output)], check=True)
        elif sys.platform == 'win32':
            writer = module('cross_dmg_writer').ensure_writer()
            subprocess.run([str(writer), str(staging), str(output)], check=True)
        else:
            raise RuntimeError('Use macOS hdiutil or the Windows cross-platform DMG writer')
    with output.open('rb') as stream:
        digest = hashlib.file_digest(stream, 'sha256').hexdigest()
    output.with_suffix('.sha256').write_text(f'{digest}  {output.name}\n', encoding='ascii')
    (WORK / 'image-manifest.json').write_text(json.dumps(dict(identities=identities, files={name: dict(sha256=hashlib.sha256(data).hexdigest(), mode=mode) for name, (data, mode) in files.items()}), indent=2))
    print(f'Universal Mac DMG: {output} ({output.stat().st_size:,} bytes)', flush=True)
    return output


if __name__ == '__main__':
    build()
