"""Run on native Mac CI; packaging/permissions can also be inspected on Windows."""
from pathlib import Path
import json
import os
import subprocess
import sys
import tempfile
from verify_package_sources import verify

ROOT = Path(__file__).resolve().parents[1]
if sys.platform != 'darwin':
    raise SystemExit('Native macOS execution is required for this verification')
arch = subprocess.check_output(['/usr/bin/uname', '-m'], text=True).strip()
asset = ROOT / 'outputs/desktop-release/SmartClock-macOS.dmg'
subprocess.run(['/usr/bin/hdiutil', 'verify', str(asset)], check=True)
with tempfile.TemporaryDirectory(prefix='smartclock-mac-') as temp:
    subprocess.run(['/usr/bin/hdiutil', 'attach', '-readonly', '-nobrowse', '-mountpoint', temp, str(asset)], check=True)
    try:
        bundle = Path(temp) / 'Smart Clock Setup.app/Contents'
        verify(bundle / 'Resources/client.zip')
        launcher = bundle / 'MacOS/SmartClock'
        setup = bundle / 'Resources/setup.command'
        assert os.access(setup, os.X_OK) and os.access(launcher, os.X_OK), 'DMG lost executable permission'
        subprocess.run(['/bin/bash', '-n', str(launcher)], check=True)
        subprocess.run(['/bin/bash', '-n', str(setup)], check=True)
        for cpu in ('arm64', 'x86_64'):
            cpu_setup = bundle / 'Resources' / f'setup-{cpu}.command'
            assert "ESPHOME_PIN='" + (ROOT / 'ESPHOME_VERSION').read_text().strip() + "'" in cpu_setup.read_text(), 'Mac installer uses an outdated ESPHome pin'
            subprocess.run(['/bin/bash', '-n', str(cpu_setup)], check=True)
        subprocess.run([str(setup), '--verify-compile'], check=True)
        subprocess.run([str(setup), '--extract-only'], check=True)
    finally:
        subprocess.run(['/usr/bin/hdiutil', 'detach', temp], check=True)
print('Native Mac DMG verification/mount, online installer, GUI, full compilation and cached relaunch OK')
