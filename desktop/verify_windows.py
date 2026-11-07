"""Exercise the shipped runtime with developer tools removed from PATH."""
from pathlib import Path
import os
import re
import subprocess
import sys

root = Path(__file__).resolve().parents[1]
bundle = root / ('outputs/SmartClock-Windows' if sys.platform == 'win32' else 'outputs/SmartClock.app/Contents/Resources')
env = os.environ.copy()
env['PATH'] = str(Path(os.environ.get('SystemRoot', 'C:/Windows')) / 'System32') if sys.platform == 'win32' else '/usr/bin:/bin:/usr/sbin:/sbin'
env.pop('PYTHONHOME', None)
env.pop('PYTHONPATH', None)
env['PYTHONNOUSERSITE'] = '1'
env['PYTHONUTF8'] = '1'
script = r'''
import importlib.util, pathlib, sys, tempfile, tkinter, base64, importlib.metadata
bundle=pathlib.Path(sys.argv[1])
assert pathlib.Path(sys.prefix).resolve() == (bundle/'runtime').resolve(), sys.prefix
assert all('.venv' not in p for p in sys.path), sys.path
assert all(pathlib.Path(p).resolve().is_relative_to((bundle/'runtime').resolve()) for p in sys.path), sys.path
import ssl, esphome, esptool, platformio, serial, ninja, pip
print('Bundled runtime and build modules OK; ESPHome '+importlib.metadata.version('esphome'))
spec=importlib.util.spec_from_file_location('clock_app',bundle/'app.py')
app=importlib.util.module_from_spec(spec);spec.loader.exec_module(app)
with tempfile.TemporaryDirectory(prefix='Smart Clock smoke ') as temp:
 app.DATA=pathlib.Path(temp)
 window=tkinter.Tk();window.withdraw();ui=app.App(window);window.update()
 values=dict(wifi_ssid='Test Network',wifi_password='test-password',fallback_ap_password='recovery-test',api_encryption_key=base64.b64encode(bytes(range(32))).decode())
 app.prepare(bundle/'firmware',ui.profile,values)
 print('GUI, USB enumeration, paths with spaces and private config generation OK')
 try:
  ui.command('config','esphome-smart-clock.yaml')
 except Exception:
  while not ui.events.empty():
   print(ui.events.get()[1])
  raise
 print('ESPHome configuration validation OK', flush=True)
 if '--compile' in sys.argv:
  try:
   ui.command('compile','esphome-smart-clock.yaml')
  except Exception:
   while not ui.events.empty():
    print(ui.events.get()[1])
   raise
  print('Full firmware compilation OK', flush=True)
 window.destroy()
'''
python = bundle / ('runtime/python.exe' if sys.platform == 'win32' else 'runtime/bin/python3')
subprocess.run([str(python), '-I', '-m', 'pip', 'check'], env=env, check=True)
git = bundle / ('git/cmd/git.exe' if sys.platform == 'win32' else 'git/bin/git')
subprocess.run([str(git), '--version'], env=env, check=True)
if sys.platform == 'darwin':
    for native in bundle.rglob('*'):
        if not native.is_file():
            continue
        with native.open('rb') as stream:
            magic = stream.read(4)
        if magic not in (b'\xcf\xfa\xed\xfe', b'\xce\xfa\xed\xfe', b'\xca\xfe\xba\xbe', b'\xbe\xba\xfe\xca'):
            continue
        dependencies = subprocess.check_output(['otool', '-L', str(native)], text=True).splitlines()[1:]
        for line in dependencies:
            dep = line.strip().split(' (', 1)[0]
            if dep.startswith('/') and not dep.startswith(('/usr/lib/', '/System/Library/')):
                raise RuntimeError(f'Non-portable native dependency: {native}: {dep}')
        commands = subprocess.check_output(['otool', '-l', str(native)], text=True)
        for rpath in re.findall(r'\bpath (.*?) \(offset', commands):
            if rpath.startswith('/') and not rpath.startswith(('/usr/lib/', '/System/Library/')):
                raise RuntimeError(f'Non-portable native search path: {native}: {rpath}')
result = subprocess.run([str(python), '-I', '-u', '-c', script, str(bundle), *sys.argv[1:]],
                        env=env, cwd=root / 'outputs', text=True)
sys.exit(result.returncode)
