"""Exercise the native downloader against real HTTP failures, without internet."""
from pathlib import Path
import hashlib
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import socket
import subprocess
import tempfile
import threading
import time
import unittest

ROOT = Path(__file__).resolve().parents[1]
DATA = bytes(range(256)) * 4096
HASH = hashlib.sha256(DATA).hexdigest()


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *_):
        pass

    def do_GET(self):
        mode = self.path.strip('/')
        offset = int(self.headers.get('Range', 'bytes=0-').split('=')[1].split('-')[0])
        self.server.requests.append((mode, offset))
        attempt = len(self.server.requests)
        if mode == 'missing':
            self.send_error(404)
            return
        if mode == 'proxy':
            self.send_error(407)
            return
        if mode == 'rate-limit' and attempt == 1:
            self.send_response(429)
            self.send_header('Retry-After', '0')
            self.end_headers()
            return
        if mode == 'range416' and offset:
            self.send_error(416)
            return
        if mode == 'redirect':
            self.send_response(302)
            self.send_header('Location', 'http://example.com/not-allowed')
            self.end_headers()
            return
        if mode == 'ignore':
            offset = 0
        body = DATA[offset:]
        if mode == 'corrupt':
            body = b'x' * len(body)
        self.send_response(206 if offset else 200)
        if offset:
            start = offset + 1 if mode == 'bad-range' and attempt == 1 else offset
            self.send_header('Content-Range', f'bytes {start}-{len(DATA)-1}/{len(DATA)}')
        self.send_header('Content-Type', 'text/html' if mode == 'html' else 'application/octet-stream')
        self.send_header('Content-Length', len(body) - 1 if mode == 'wrong-size' else len(body))
        self.end_headers()
        try:
            if mode == 'cut' and attempt == 1:
                self.wfile.write(body[:75000])
                self.wfile.flush()
                self.connection.shutdown(socket.SHUT_RDWR)
                self.connection.close()
            elif mode == 'slow':
                for index in range(0, len(body), 8192):
                    self.wfile.write(body[index:index+8192])
                    self.wfile.flush()
                    time.sleep(0.025)
            else:
                self.wfile.write(body)
        except (BrokenPipeError, ConnectionError, OSError):
            pass


class DownloadTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.work = tempfile.TemporaryDirectory(prefix='download-tests-', dir=ROOT / 'outputs')
        cls.harness = Path(cls.work.name) / 'download.exe'
        compiler = Path('C:/Windows/Microsoft.NET/Framework64/v4.0.30319/csc.exe')
        subprocess.run([str(compiler), '/nologo', '/define:TEST_DOWNLOAD', '/out:' + str(cls.harness),
                        str(ROOT / 'tests/download_harness.cs'), str(ROOT / 'desktop/reliable_download.cs')], check=True)

    @classmethod
    def tearDownClass(cls):
        cls.work.cleanup()

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(dir=self.work.name)
        self.target = Path(self.temp.name) / 'package.zip'
        self.server = ThreadingHTTPServer(('127.0.0.1', 0), Handler)
        self.server.daemon_threads = True
        self.server.requests = []
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()

    def tearDown(self):
        self.server.shutdown()
        self.server.server_close()
        self.thread.join()
        self.temp.cleanup()

    def run_download(self, mode='good', cancel=None):
        url = f'http://127.0.0.1:{self.server.server_port}/{mode}'
        args = [str(self.harness), url, str(self.target), HASH, str(len(DATA))]
        if cancel:
            args.append(str(cancel))
        return subprocess.run(args, capture_output=True, text=True, timeout=35)

    def seed_partial(self):
        Path(str(self.target) + '.part').write_bytes(DATA[:40000])

    def assert_valid(self, result):
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(self.target.read_bytes(), DATA)
        self.assertFalse(Path(str(self.target) + '.part').exists())

    def test_validated_cache_needs_no_network(self):
        self.assert_valid(self.run_download())
        count = len(self.server.requests)
        self.assert_valid(self.run_download('missing'))
        self.assertEqual(len(self.server.requests), count)

    def test_interruption_is_resumed_automatically(self):
        self.assert_valid(self.run_download('cut'))
        self.assertGreater(self.server.requests[1][1], 0)

    def test_server_ignoring_range_restarts_without_appending(self):
        self.seed_partial()
        self.assert_valid(self.run_download('ignore'))

    def test_bad_resume_range_is_discarded_and_retried(self):
        self.seed_partial()
        self.assert_valid(self.run_download('bad-range'))
        self.assertEqual(self.server.requests[1][1], 0)

    def test_416_discards_stale_partial(self):
        self.seed_partial()
        self.assert_valid(self.run_download('range416'))
        self.assertEqual(self.server.requests[1][1], 0)

    def test_corruption_never_becomes_a_ready_package(self):
        result = self.run_download('corrupt')
        self.assertEqual(result.returncode, 1)
        self.assertIn('integrity check', result.stderr)
        self.assertEqual(len(self.server.requests), 3)
        self.assertFalse(self.target.exists())
        self.assertFalse(Path(str(self.target) + '.part').exists())

    def test_html_and_incorrect_lengths_are_rejected(self):
        for mode in ('html', 'wrong-size'):
            with self.subTest(mode=mode):
                result = self.run_download(mode)
                self.assertEqual(result.returncode, 1)
                self.assertFalse(self.target.exists())

    def test_cancel_keeps_partial_and_next_run_resumes(self):
        result = self.run_download('slow', cancel=600)
        self.assertEqual(result.returncode, 2, result.stderr)
        self.assertGreater(Path(str(self.target) + '.part').stat().st_size, 0)
        self.assert_valid(self.run_download())
        self.assertGreater(self.server.requests[-1][1], 0)

    def test_missing_release_fails_without_repeated_requests(self):
        result = self.run_download('missing')
        self.assertEqual(result.returncode, 1)
        self.assertIn('not available', result.stderr)
        self.assertEqual(len(self.server.requests), 1)

    def test_proxy_block_is_actionable_without_repeated_requests(self):
        result = self.run_download('proxy')
        self.assertEqual(result.returncode, 1)
        self.assertIn('proxy', result.stderr)
        self.assertEqual(len(self.server.requests), 1)

    def test_rate_limit_retries_after_server_delay(self):
        self.assert_valid(self.run_download('rate-limit'))
        self.assertEqual(len(self.server.requests), 2)

    def test_unwritable_partial_path_is_not_replaced(self):
        locked = Path(str(self.target) + '.part')
        locked.mkdir()
        result = self.run_download()
        self.assertEqual(result.returncode, 1)
        self.assertTrue(locked.is_dir())
        self.assertFalse(self.target.exists())

    def test_redirect_cannot_downgrade_to_external_http(self):
        result = self.run_download('redirect')
        self.assertEqual(result.returncode, 1)
        self.assertIn('secure HTTPS', result.stderr)
        self.assertFalse(self.target.exists())


if __name__ == '__main__':
    unittest.main(verbosity=2)
