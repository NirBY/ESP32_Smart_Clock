import importlib.util
from pathlib import Path
import tempfile
import unittest
import base64
import io
from unittest.mock import patch
from types import SimpleNamespace

spec = importlib.util.spec_from_file_location('desktop_app', Path(__file__).resolve().parents[1] / 'desktop/app.py')
app = importlib.util.module_from_spec(spec)
spec.loader.exec_module(app)


class InstallerTests(unittest.TestCase):
    def test_isolated_worker_explicitly_enables_utf8(self):
        from unittest.mock import MagicMock
        import queue
        with tempfile.TemporaryDirectory() as temp:
            ui = app.App.__new__(app.App)
            ui.profile = Path(temp)
            ui.events = queue.Queue()
            (ui.profile / 'secrets.yaml').write_text('wifi_ssid: test\n')
            process = MagicMock()
            process.__enter__.return_value = process
            process.stdout = iter(['Unicode tools: ✓ שלום\n'])
            process.wait.return_value = 0
            with patch.object(app.subprocess, 'Popen', return_value=process) as launch:
                ui.command('config', 'esphome-smart-clock.yaml')
            arguments = launch.call_args.args[0]
            self.assertEqual(arguments[1:5], ['-I', '-X', 'utf8', '-m'])
            self.assertEqual(launch.call_args.kwargs['encoding'], 'utf-8')

    def test_new_installer_does_not_select_an_older_cached_beta(self):
        with tempfile.TemporaryDirectory() as temp:
            bundled = Path(temp) / 'bundled.yaml'
            cached = Path(temp) / 'cached.yaml'
            bundled.write_text('firmware_version: "0.1.0"')
            for value, expected in [('0.1.0-beta.22', False), ('0.1.0', True), ('0.1.1', True), ('broken', False)]:
                cached.write_text(f'firmware_version: "{value}"')
                self.assertEqual(app.cache_is_current(cached, bundled), expected)
            cached.write_text('incomplete download')
            self.assertFalse(app.cache_is_current(cached, bundled))

    def port(self, device, vid=0x10C4):
        return SimpleNamespace(device=device, vid=vid, description='ESP USB bridge')

    def test_usb_target_follows_replug_without_manually_clearing_the_field(self):
        selected = app.select_usb_target('', [self.port('COM4')])
        self.assertEqual(selected, 'COM4')
        self.assertEqual(app.select_usb_target(selected, []), '')
        self.assertEqual(app.select_usb_target(selected, [self.port('COM7')]), 'COM7')
        self.assertEqual(app.select_usb_target('/dev/cu.usbserial-old', [self.port('/dev/cu.usbserial-new')]), '/dev/cu.usbserial-new')
        self.assertEqual(app.select_usb_target('com7', [self.port('COM7')]), 'COM7')
        self.assertEqual(app.select_usb_target(r'\\.\COM7', [self.port('COM7')]), 'COM7')

    def test_usb_refresh_preserves_valid_targets_and_refuses_ambiguous_selection(self):
        ports = [self.port('COM4'), self.port('COM7')]
        self.assertEqual(app.select_usb_target('COM7', ports), 'COM7')
        self.assertEqual(app.select_usb_target('192.168.1.25', ports), '192.168.1.25')
        self.assertEqual(app.select_usb_target('esp32-smart-clock.local', ports), 'esp32-smart-clock.local')
        self.assertEqual(app.select_usb_target('COM3', ports), '')
        self.assertEqual(app.select_usb_target('', ports), '')
        self.assertEqual(app.select_usb_target('COM3', [self.port('COM1', 0)]), '')

    def test_find_usb_refreshes_stale_selection_but_does_not_retarget_active_upload(self):
        from unittest.mock import MagicMock
        ui = app.App.__new__(app.App)
        ui.busy = False
        ui.device = MagicMock()
        ui.device.get.return_value = 'COM4'
        ui.ports = MagicMock()
        ui.usb_info = MagicMock()
        with patch('serial.tools.list_ports.comports', return_value=[self.port('COM7')]):
            ui.scan()
        ui.device.set.assert_called_once_with('COM7')
        ui.device.set.reset_mock()
        ui.busy = True
        with patch('serial.tools.list_ports.comports', return_value=[self.port('COM9')]):
            ui.scan()
        ui.device.set.assert_not_called()

    def values(self):
        return dict(wifi_ssid='Home: #שלום', wifi_password='secret123',
                    fallback_ap_password='recovery123', api_encryption_key=base64.b64encode(bytes(range(32))).decode())

    def test_personalized_config_is_portable_and_roundtrips(self):
        import yaml
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            app.prepare(Path(__file__).resolve().parents[1], target, self.values())
            self.assertEqual(yaml.safe_load((target / 'secrets.yaml').read_text()), self.values())
            self.assertIn('build_path: build/${device_name}', (target / 'esphome-smart-clock.yaml').read_text(encoding='utf-8'))
            self.assertTrue((target / 'media/timer-finished.wav').exists())

    def test_invalid_credentials_rejected(self):
        for key, value in [('wifi_ssid', ''), ('wifi_password', 'short'),
                           ('fallback_ap_password', 'short'), ('api_encryption_key', 'bad'),
                           ('api_encryption_key', base64.b64encode(bytes(32)).decode())]:
            values = self.values()
            values[key] = value
            with self.assertRaises(ValueError):
                app.validate(values)

    def test_release_tag_overrides_source_version_like_ci(self):
        self.assertEqual(app.version(app.release_config('substitutions:\n  firmware_version: "0.1.0-beta.22"\n', 'v0.1.0-beta.23')), '0.1.0-beta.23')
        with self.assertRaises(ValueError):
            app.release_config('substitutions:\n', 'v0.1.0-beta.23')
        with self.assertRaises(ValueError):
            app.release_config('substitutions:\n', '../unsafe')

    def test_download_failures_are_not_reported_as_usb_problems(self):
        self.assertIn('Internet', app.command_failure('compile', ['ConnectionError: failed to establish a new connection']))
        self.assertIn('validation', app.command_failure('compile', ['SHA256 mismatch']))
        self.assertIn('Upload did not finish', app.command_failure('upload', ['ConnectionError']))

    def test_update_download_retries_and_rejects_truncation(self):
        good = io.BytesIO(b'valid-response')
        good.headers = {'Content-Length': '14'}
        with patch.object(app.urllib.request, 'urlopen', side_effect=[app.urllib.error.URLError('offline'), good]) as opened, patch.object(app.time, 'sleep'):
            self.assertEqual(app.fetch('https://example.invalid/update'), b'valid-response')
            self.assertEqual(opened.call_count, 2)
        def short(*args, **kwargs):
            response = io.BytesIO(b'short')
            response.headers = {'Content-Length': '100'}
            return response
        with patch.object(app.urllib.request, 'urlopen', side_effect=short), patch.object(app.time, 'sleep'):
            with self.assertRaisesRegex(RuntimeError, 'settings were kept'):
                app.fetch('https://example.invalid/update')

    def test_progress_uses_build_tasks_and_upload_frames_not_memory_usage(self):
        item = app.parse_progress('compile', '[543/1087] Building CXX object app.cpp.obj')
        self.assertAlmostEqual(item['percent'], 49.954, places=2)
        self.assertIn('543/1087 tasks', item['label'])
        self.assertEqual(app.parse_progress('upload', 'Writing at 0x0000745e  ----  1.7% 16.00kB/951.96kB [0s]')['percent'], 1.7)
        self.assertEqual(app.parse_progress('upload', 'Uploading: [========    ] 65%')['percent'], 65)
        self.assertIsNone(app.parse_progress('compile', 'RAM: [=== ] 32.0% (used 57909 bytes)'))
        self.assertIsNone(app.parse_progress('compile', 'Flash: [======== ] 80.3% (used 1473324 bytes)'))
        self.assertIsNone(app.parse_progress('compile', '[1/0] Invalid counter'))
        self.assertIsNone(app.parse_progress('compile', '[5/4] Invalid counter'))
        self.assertIsNone(app.parse_progress('upload', 'Writing at 0x1234 101%'))
        self.assertIsNone(app.parse_progress('upload', 'Verifying written data...')['percent'])

    def test_progress_bar_switches_phases_and_failure_does_not_show_success(self):
        from unittest.mock import MagicMock
        ui = app.App.__new__(app.App)
        ui.progress = MagicMock()
        ui.progress_text = MagicMock()
        ui._progress_mode = 'indeterminate'
        ui.show_progress('Compile — 42%', 42)
        self.assertEqual(ui._progress_mode, 'determinate')
        ui.progress.__setitem__.assert_called_with('value', 42)
        ui.show_progress('Verifying firmware…')
        self.assertEqual(ui._progress_mode, 'indeterminate')
        ui.progress.start.assert_called_once()
        ui.root = MagicMock()
        ui.status = MagicMock()
        ui.actions = []
        ui.busy = True
        ui.overall_progress = None
        ui.events = app.queue.Queue()
        ui.events.put(('failed', 'Network error'))
        ui.progress.__setitem__.reset_mock()
        ui.poll()
        self.assertFalse(ui.busy)
        ui.progress.__setitem__.assert_not_called()
        ui.progress_text.set.assert_called_with('Stopped — see details below and retry')

    def test_overall_progress_does_not_reset_or_finish_at_intermediate_100(self):
        progress = app.OverallProgress()
        events = [
            {'stage': 'download', 'percent': 100},
            app.parse_progress('compile', '[0/2] CMake probe'),
            app.parse_progress('compile', '[543/1087] Building app.cpp'),
            app.parse_progress('compile', '[118/118] Nested bootloader'),
            app.parse_progress('compile', '[1087/1087] Linking app'),
            {'stage': 'compiled', 'percent': 100},
            {'stage': 'connect', 'percent': None},
            app.parse_progress('upload', 'Writing at 0x0000745e ---- 1.7%'),
            app.parse_progress('upload', 'Writing at 0x00177ba0 ---- 100.0%'),
            app.parse_progress('upload', 'Verifying written data...'),
            app.parse_progress('upload', 'Hash of data verified.'),
            {'stage': 'uploaded', 'percent': 100},
        ]
        values = [progress.update(event)[0] for event in events]
        self.assertEqual(values, sorted(values))
        self.assertEqual(values[3], values[2], 'Nested tasks must not advance the primary build graph')
        self.assertEqual(values[5], 90)
        self.assertGreater(values[7], 90)
        self.assertLess(max(values), 100)
        progress.complete()
        self.assertEqual(progress.value, 100)

    def test_mac_escaped_and_actual_ansi_progress_frames_are_cleaned(self):
        line = r'\033[2KWriting at 0x0000745c \033[38;2;249;38;114m---\033[0m 1.7% 16.00kB/951.96kB [0s]'
        self.assertEqual(app.parse_progress('upload', line)['percent'], 1.7)
        self.assertNotIn('\\033', app.clean_log_line(line))
        live = '\x1b[1A\x1b[2K\x1b[32m[50/100] Building app\x1b[0m'
        self.assertEqual(app.parse_progress('compile', live)['percent'], 50)
        self.assertEqual(app.clean_log_line(r'\033[32mINFO Successfully uploaded program.\033[0m'), 'INFO Successfully uploaded program.')

    def test_failed_overall_progress_keeps_last_total(self):
        from unittest.mock import MagicMock
        ui = app.App.__new__(app.App)
        ui.progress = MagicMock()
        ui.progress_text = MagicMock()
        ui.status = MagicMock()
        ui.root = MagicMock()
        ui.actions = []
        ui.busy = True
        ui.overall_progress = app.OverallProgress()
        ui.overall_progress.update({'stage': 'transfer', 'percent': 50})
        ui.events = app.queue.Queue()
        ui.events.put(('failed', 'Upload interrupted'))
        ui.poll()
        self.assertEqual(ui.overall_progress.value, 94)
        ui.progress_text.set.assert_called_with('Stopped at about 94% — see details below and retry')


if __name__ == '__main__':
    unittest.main()
