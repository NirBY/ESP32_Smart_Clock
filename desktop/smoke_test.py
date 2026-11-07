"""Exercise the actual extracted one-file runtime, without developer tools."""
import base64
import importlib.metadata
import importlib.util
from pathlib import Path
import subprocess
import sys
import tempfile
import traceback

root = Path(__file__).resolve().parent
log = Path(sys.argv[1])
log.parent.mkdir(parents=True, exist_ok=True)
with log.open('w', encoding='utf-8', buffering=1) as report:
    try:
        assert Path(sys.prefix).resolve() == (root / 'runtime').resolve()
        assert all(Path(p).resolve().is_relative_to(root / 'runtime') for p in sys.path)
        subprocess.run([sys.executable, '-I', '-m', 'pip', 'check'], stdout=report, stderr=report, check=True)
        subprocess.run([str(root / 'git/cmd/git.exe'), '--version'], stdout=report, stderr=report, check=True)
        spec = importlib.util.spec_from_file_location('clock_app', root / 'app.py')
        app = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(app)
        with tempfile.TemporaryDirectory(prefix='SmartClock-onefile-test-') as temp:
            app.DATA = Path(temp)
            window = app.tk.Tk()
            window.withdraw()
            ui = app.App(window)
            window.update()
            values = dict(wifi_ssid='Test Network', wifi_password='test-password', fallback_ap_password='recovery-test', api_encryption_key=base64.b64encode(bytes(range(32))).decode())
            app.prepare(root / 'firmware', ui.profile, values)
            report.write('GUI, USB enumeration, bundled imports and personal configuration OK\n')
            try:
                ui.command('config', 'esphome-smart-clock.yaml')
                report.write('ESPHome configuration validation OK\n')
                if '--compile' in sys.argv:
                    ui.command('compile', 'esphome-smart-clock.yaml')
                    report.write('Full firmware compilation OK\n')
            finally:
                while not ui.events.empty():
                    report.write(str(ui.events.get()[1]) + '\n')
                window.destroy()
        report.write('Single EXE smoke test passed\n')
    except Exception:
        traceback.print_exc(file=report)
        raise SystemExit(1)
