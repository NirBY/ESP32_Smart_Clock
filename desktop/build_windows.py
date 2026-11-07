"""Build a portable Windows folder with its own Python and ESPHome runtime."""
from pathlib import Path
import shutil
import subprocess
import sys
from bundle_git import bundle_git

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'outputs' / 'SmartClock-Windows'
OUT.mkdir(parents=True, exist_ok=True)
bundle_git(OUT / 'git')
runtime = OUT / 'runtime'
runtime.mkdir(exist_ok=True)
base = Path(sys.base_prefix)
for item in base.iterdir():
    if item.name in ('DLLs', 'Lib', 'tcl', 'libs', 'include'):
        shutil.copytree(item, runtime / item.name, dirs_exist_ok=True,
                        ignore=shutil.ignore_patterns('site-packages', '__pycache__', 'test', 'tests'))
    elif item.suffix in ('.exe', '.dll') or item.name == 'LICENSE.txt':
        shutil.copy2(item, runtime / item.name)
packages = (runtime / 'Lib/site-packages').resolve()
if not packages.is_relative_to((ROOT / 'outputs').resolve()):
    raise RuntimeError('Refusing to replace packages outside the output directory')
if packages.exists():
    shutil.rmtree(packages)
shutil.copytree(Path(sys.prefix) / 'Lib/site-packages', packages,
                dirs_exist_ok=True, ignore=shutil.ignore_patterns('__pycache__'))
shutil.copy2(ROOT / 'desktop/app.py', OUT / 'app.py')
shutil.copy2(ROOT / 'desktop/install_drivers.ps1', OUT / 'install_drivers.ps1')
shutil.copy2(ROOT / 'docs/wiki/Desktop-App.md', OUT / 'USER-GUIDE.txt')
firmware = OUT / 'firmware'
firmware.mkdir(exist_ok=True)
for name in ('src', 'media', 'components'):
    shutil.copytree(ROOT / name, firmware / name, dirs_exist_ok=True)
shutil.copy2(ROOT / 'esphome-smart-clock.yaml', firmware)
launcher = OUT / 'launcher.cs'
launcher.write_text('''using System;
using System.Diagnostics;
using System.IO;
using System.Windows.Forms;
class Launcher {
 [STAThread] static void Main() {
  string root = AppDomain.CurrentDomain.BaseDirectory;
  try {
   var p = new ProcessStartInfo(Path.Combine(root, "runtime", "pythonw.exe"), "-I \\\"" + Path.Combine(root, "app.py") + "\\\"");
   p.WorkingDirectory = root; p.UseShellExecute = false;
   p.EnvironmentVariables.Remove("PYTHONHOME"); p.EnvironmentVariables.Remove("PYTHONPATH");
   Process.Start(p);
  } catch(Exception e) { MessageBox.Show(e.Message, "Smart Clock"); }
 }
}''', encoding='utf-8')
compiler = Path('C:/Windows/Microsoft.NET/Framework64/v4.0.30319/csc.exe')
subprocess.run([str(compiler), '/nologo', '/target:winexe', '/reference:System.Windows.Forms.dll',
                '/out:' + str(OUT / 'SmartClock.exe'), str(launcher)], check=True)
launcher.unlink()
(OUT / 'READ-ME.txt').write_text('Extract the whole folder, then open SmartClock.exe. No Python installation needed.\nInternet required for firmware compilation. Settings: %LOCALAPPDATA%/SmartClock/device\nLocal preview, unsigned. Do not move the EXE away from its runtime folder.\n', encoding='utf-8')
print(OUT)
