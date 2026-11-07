"""Run on macOS with a relocatable python-build-standalone runtime (Tk included).

Usage: python build_macos.py /path/to/python-runtime
The runtime must already contain the ESPHome version pinned by ESPHOME_VERSION.
Build separately for Apple Silicon and Intel. Signing is a release step.
"""
from pathlib import Path
import plistlib
import shutil
import subprocess
import sys
from bundle_macos_git import bundle_git

if sys.platform != 'darwin':
    raise SystemExit('Build and test the macOS application on a Mac.')
runtime_source = Path(sys.argv[1]).resolve()
python = runtime_source / 'bin/python3'
subprocess.run([str(python), '-c', 'import tkinter, esphome, serial; r=tkinter.Tk(); r.destroy()'], check=True)
root = Path(__file__).resolve().parents[1]
app = root / 'outputs/SmartClock.app/Contents'
resources = app / 'Resources'
resources.mkdir(parents=True, exist_ok=True)
shutil.copytree(runtime_source, resources / 'runtime', dirs_exist_ok=True, symlinks=False)
bundle_git(resources / 'git')
shutil.copy2(root / 'desktop/app.py', resources / 'app.py')
shutil.copy2(root / 'docs/wiki/Desktop-App.md', resources / 'USER-GUIDE.txt')
firmware = resources / 'firmware'
firmware.mkdir(exist_ok=True)
shutil.copy2(root / 'esphome-smart-clock.yaml', firmware)
for name in ('src', 'media', 'components'):
    shutil.copytree(root / name, firmware / name, dirs_exist_ok=True)
launcher = app / 'MacOS/SmartClock'
launcher.parent.mkdir(exist_ok=True)
launcher.write_text('#!/bin/sh\nHERE="$(CDPATH= cd -- "$(dirname -- "$0")/../Resources" && pwd)"\nunset PYTHONHOME PYTHONPATH\nexec "$HERE/runtime/bin/python3" -I "$HERE/app.py"\n')
launcher.chmod(0o755)
(app / 'Info.plist').write_bytes(plistlib.dumps(dict(CFBundleName='SmartClock', CFBundleExecutable='SmartClock',
    CFBundleIdentifier='com.nirby.smartclock', CFBundlePackageType='APPL', CFBundleVersion='0.1.0',
    NSHighResolutionCapable=True)))
print(app.parent)
