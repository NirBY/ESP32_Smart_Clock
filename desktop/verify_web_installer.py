"""Cold HTTP install, atomic recovery and offline warm startup of the real EXE."""
from pathlib import Path
import argparse
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import importlib.util
import json
import os
import shutil
import subprocess
import tempfile
import threading

ROOT = Path(__file__).resolve().parents[1]
RELEASE = ROOT / 'outputs/desktop-release'
spec = importlib.util.spec_from_file_location('web_builder', ROOT / 'desktop/build_web_installer.py')
builder = importlib.util.module_from_spec(spec)
spec.loader.exec_module(builder)


class Handler(SimpleHTTPRequestHandler):
    requests = 0
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(RELEASE), **kwargs)
    def log_message(self, *_):
        pass
    def do_GET(self):
        type(self).requests += 1
        super().do_GET()


def main(compile_firmware=False):
    metadata = json.loads((ROOT / 'outputs/onefile-build/web-installer.json').read_text())
    server = ThreadingHTTPServer(('127.0.0.1', 0), Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        url = f'http://127.0.0.1:{server.server_port}/{metadata["asset"]}'
        preview = builder.build(url=url, test=True)
        with tempfile.TemporaryDirectory(prefix='scw-') as temp:
            temp = Path(temp)
            empty = temp / 'Empty folder שלום'
            empty.mkdir()
            exe = empty / 'SmartClock Setup.exe'
            shutil.copy2(preview['installer'], exe)
            assert len(list(empty.iterdir())) == 1
            env = os.environ.copy()
            env.pop('PYTHONPATH', None)
            env.pop('PYTHONHOME', None)
            env['PATH'] = str(Path(os.environ.get('SystemRoot', 'C:/Windows')) / 'System32')
            env['SMARTCLOCK_TEST_DATA'] = str(temp / 'd')
            data = temp / 'd/SmartClock'
            # A failed new setup must not change existing runtime/settings.
            old = data / 'application/previous-version'
            old.mkdir(parents=True)
            (old / '.complete').write_text('previous-good-version')
            settings = data / 'device/secrets.yaml'
            settings.parent.mkdir()
            settings.write_text('wifi_ssid: "preserve-this-setting"\n')
            result = subprocess.run([str(exe), '--verify-compile' if compile_firmware else '--smoke-test'], env=env, cwd=empty)
            report = data / 'self-test.log'
            if report.exists():
                lines = report.read_text(encoding='utf-8').splitlines()
                print('\n'.join(lines[-30:] if result.returncode else [line for line in lines if line.endswith(' OK') or line.endswith('passed') or 'No broken requirements' in line]), flush=True)
            if result.returncode:
                error = data / 'startup-error.log'
                if error.exists():
                    print(error.read_text(), flush=True)
                raise SystemExit(result.returncode)
            assert Handler.requests >= 1, 'Cold installation did not download the package'
            assert settings.read_text() == 'wifi_ssid: "preserve-this-setting"\n'
            assert (old / '.complete').read_text() == 'previous-good-version'
            marker = data / 'application' / metadata['identity'] / '.complete'
            stamp = marker.stat().st_mtime_ns
            server.shutdown()
            server.server_close()
            thread.join()
            subprocess.run([str(exe), '--extract-only'], env=env, cwd=empty, timeout=20, check=True)
            assert marker.stat().st_mtime_ns == stamp
            # Force a fresh version check with no server: no installation may be activated.
            failed_data = temp / 'f'
            env['SMARTCLOCK_TEST_DATA'] = str(failed_data)
            failed = subprocess.run([str(exe), '--extract-only'], env=env, cwd=empty, timeout=80)
            assert failed.returncode != 0
            failed_marker = failed_data / 'SmartClock/application' / metadata['identity'] / '.complete'
            assert not failed_marker.exists()
            assert settings.read_text() == 'wifi_ssid: "preserve-this-setting"\n'
            print('Cold HTTP install, isolated EXE, preserved settings/runtime, offline warm launch and safe offline failure OK', flush=True)
    finally:
        if thread.is_alive():
            server.shutdown()
            server.server_close()
            thread.join()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--compile', action='store_true')
    main(parser.parse_args().compile)
