"""Ensure release integrity checks reject stale firmware and app payloads."""
from pathlib import Path
import importlib.util
import tempfile
import unittest
import zipfile

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('package_sources', ROOT / 'desktop/verify_package_sources.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class PackageTests(unittest.TestCase):
    def test_current_sources_pass_but_stale_or_private_files_fail(self):
        files = {'app.py': (ROOT / 'desktop/app.py').read_bytes(),
                 'firmware/esphome-smart-clock.yaml': (ROOT / 'esphome-smart-clock.yaml').read_bytes()}
        for folder in ('src', 'media', 'components'):
            for path in (ROOT / folder).rglob('*'):
                if path.is_file() and '__pycache__' not in path.parts and path.suffix != '.pyc':
                    files['firmware/' + path.relative_to(ROOT).as_posix()] = path.read_bytes()
        with tempfile.TemporaryDirectory() as temp:
            archive = Path(temp) / 'client.zip'
            for changed in (None, 'app.py', 'firmware/esphome-smart-clock.yaml', 'firmware/secrets.yaml'):
                with self.subTest(changed=changed):
                    contents = dict(files)
                    if changed:
                        contents[changed] = b'stale or private'
                    with zipfile.ZipFile(archive, 'w') as output:
                        for name, data in contents.items():
                            output.writestr(name, data)
                    if changed:
                        with self.assertRaises(AssertionError):
                            module.verify(archive)
                    else:
                        module.verify(archive)


if __name__ == '__main__':
    unittest.main()
