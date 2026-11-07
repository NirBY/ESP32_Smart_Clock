"""Verify portable macOS installer packaging without pretending to execute macOS."""
from pathlib import Path
import hashlib
import io
import json
import plistlib
import re
import unittest
import zipfile

ROOT = Path(__file__).resolve().parents[1]


class MacInstallerTests(unittest.TestCase):
    def test_both_installers_preserve_executability_and_pinned_client(self):
        for arch, platform in [('arm64', 'macOS-AppleSilicon'), ('x86_64', 'macOS-Intel')]:
            with self.subTest(arch=arch):
                file = ROOT / f'outputs/macos-dmg-build/internal-zips/SmartClock-{platform}.zip'
                with zipfile.ZipFile(file) as archive:
                    self.assertIsNone(archive.testzip())
                    prefix = 'Smart Clock Setup.app/Contents/'
                    info = plistlib.loads(archive.read(prefix + 'Info.plist'))
                    self.assertEqual(info['CFBundleExecutable'], 'SmartClock')
                    for name in ('MacOS/SmartClock', 'Resources/setup.command'):
                        entry = archive.getinfo(prefix + name)
                        self.assertEqual(entry.create_system, 3)
                        self.assertTrue((entry.external_attr >> 16) & 0o111)
                        self.assertNotIn(b'\r\n', archive.read(entry))
                    script = archive.read(prefix + 'Resources/setup.command').decode()
                    self.assertIn("ARCH='" + arch + "'", script)
                    self.assertFalse(re.search(r'@[A-Z_]+@', script))
                    client = archive.read(prefix + 'Resources/client.zip')
                    self.assertIn(hashlib.sha256(client).hexdigest(), script)
                    with zipfile.ZipFile(io.BytesIO(client)) as source:
                        self.assertIsNone(source.testzip())
                        self.assertIn('app.py', source.namelist())
                        self.assertIn('firmware/esphome-smart-clock.yaml', source.namelist())
                        self.assertNotIn('firmware/secrets.yaml', source.namelist())

    def test_bootstrap_pins_are_arch_specific_https_and_complete(self):
        pins = json.loads((ROOT / 'desktop/micromamba.json').read_text())
        self.assertNotEqual(pins['arm64']['binary_sha256'], pins['x86_64']['binary_sha256'])
        for arch in ('arm64', 'x86_64'):
            pin = pins[arch]
            self.assertTrue(pin['url'].startswith('https://github.com/mamba-org/micromamba-releases/releases/download/'))
            self.assertRegex(pin['sha256'], r'^[0-9a-f]{64}$')
            self.assertRegex(pin['binary_sha256'], r'^[0-9a-f]{64}$')
            self.assertGreater(pin['size'], 0)


if __name__ == '__main__':
    unittest.main(verbosity=2)
