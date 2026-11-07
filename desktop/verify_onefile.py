"""Run the actual EXE from an otherwise empty folder, including warm startup."""
from pathlib import Path
import os
import shutil
import subprocess
import sys
import tempfile

root = Path(__file__).resolve().parents[1]
source = root / 'outputs/desktop-release/SmartClock-Windows-x64.exe'
identity = (root / 'outputs/onefile-build/payload-id.txt').read_text().strip()
app_data = Path(os.environ['LOCALAPPDATA']) / 'SmartClock'
cache = app_data / 'application' / identity
env = os.environ.copy()
env.pop('PYTHONHOME', None)
env.pop('PYTHONPATH', None)
env['PATH'] = str(Path(os.environ.get('SystemRoot', 'C:/Windows')) / 'System32')
with tempfile.TemporaryDirectory(prefix='Single EXE שלום ', dir=root / 'outputs') as temp:
    isolated = Path(temp) / 'Smart Clock.exe'
    shutil.copy2(source, isolated)
    assert len(list(Path(temp).iterdir())) == 1
    flag = '--verify-compile' if '--compile' in sys.argv else '--smoke-test'
    result = subprocess.run([str(isolated), flag], cwd=temp, env=env)
    report = app_data / 'self-test.log'
    if report.exists():
        lines = report.read_text(encoding='utf-8').splitlines()
        print('\n'.join(lines[-30:] if result.returncode else [line for line in lines if line.endswith(' OK') or line.endswith('passed') or 'No broken requirements' in line]), flush=True)
    if result.returncode:
        error = app_data / 'startup-error.log'
        if error.exists():
            print(error.read_text(), flush=True)
        raise SystemExit(result.returncode)
    marker = cache / '.complete'
    before = marker.stat().st_mtime_ns
    subprocess.run([str(isolated), '--extract-only'], cwd=temp, env=env, check=True)
    assert marker.stat().st_mtime_ns == before, 'Warm launch unexpectedly unpacked the runtime again'
    print('Single EXE from empty Unicode/spaced folder and cached relaunch OK', flush=True)
