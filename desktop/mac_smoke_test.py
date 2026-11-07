"""Native macOS check of the automatically provisioned app environment."""
import base64
import importlib.util
from pathlib import Path
import sys
import tempfile

root = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('clock_app', root / 'app.py')
app = importlib.util.module_from_spec(spec)
spec.loader.exec_module(app)
with tempfile.TemporaryDirectory(prefix='smartclock-mac-') as temp:
    app.DATA = Path(temp)
    window = app.tk.Tk()
    window.withdraw()
    ui = app.App(window)
    window.update()
    values = dict(wifi_ssid='Test Network', wifi_password='test-password', fallback_ap_password='recovery-test', api_encryption_key=base64.b64encode(bytes(range(32))).decode())
    app.prepare(root / 'firmware', ui.profile, values)
    try:
        ui.command('config', 'esphome-smart-clock.yaml')
        if '--verify-compile' in sys.argv:
            ui.command('compile', 'esphome-smart-clock.yaml')
    finally:
        while not ui.events.empty():
            print(ui.events.get()[1])
        window.destroy()
print('macOS provisioned environment, GUI, configuration and optional compilation OK')
