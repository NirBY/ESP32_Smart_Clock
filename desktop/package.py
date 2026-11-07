"""Archive the tested application and provide a checksum for release downloads."""
from pathlib import Path
import hashlib
import os
import shutil
import subprocess
import sys

root = Path(__file__).resolve().parents[1]
output = root / 'outputs/desktop-release'
output.mkdir(parents=True, exist_ok=True)
platform = os.environ['DESKTOP_PLATFORM']
name = 'SmartClock-' + platform
if platform == 'Windows-x64':
    subprocess.run([sys.executable, '-I', str(root / 'desktop/build_onefile.py'), '--payload-only'], check=True)
    subprocess.run([sys.executable, '-I', str(root / 'desktop/build_web_installer.py')], check=True)
    archive = output / (name + '.exe')
    # Keep the release directory unambiguous when rebuilding an older preview.
    previous = output / (name + '.zip')
    if previous.exists():
        previous.unlink()
else:
    subprocess.run([sys.executable, '-I', str(root / 'desktop/build_macos_dmg.py')], check=True)
    archive = output / 'SmartClock-macOS.dmg'
    name = 'SmartClock-macOS'
with archive.open('rb') as stream:
    checksum = hashlib.file_digest(stream, 'sha256').hexdigest()
(output / (name + '.sha256')).write_text(f'{checksum}  {archive.name}\n', encoding='ascii')
print(archive)
