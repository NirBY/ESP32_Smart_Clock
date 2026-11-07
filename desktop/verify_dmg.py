"""Independent Windows-side UDIF, HFS catalog and byte-for-byte bundle checks."""
from pathlib import Path
import hashlib
import json
import plistlib
import shutil
import struct
import subprocess
import tempfile
import zlib

ROOT = Path(__file__).resolve().parents[1]
image = ROOT / 'outputs/desktop-release/SmartClock-macOS.dmg'
raw = image.read_bytes()
footer = raw[-512:]
assert footer[:4] == b'koly' and struct.unpack_from('>II', footer, 4) == (4, 512)
offset, length = struct.unpack_from('>QQ', footer, 24)
assert offset + length <= len(raw) - 512
assert zlib.crc32(raw[offset:offset+length]) == struct.unpack_from('>I', footer, 88)[0]
xml_offset, xml_length = struct.unpack_from('>QQ', footer, 216)
assert xml_offset + xml_length <= len(raw) - 512
metadata = plistlib.loads(raw[xml_offset:xml_offset+xml_length])
tables = metadata['resource-fork']['blkx']
table_crcs = b''.join(table['Data'][72:76] for table in tables)
assert zlib.crc32(table_crcs) == struct.unpack_from('>I', footer, 360)[0]
assert image.with_suffix('.sha256').read_text(encoding='utf-8').startswith(hashlib.sha256(raw).hexdigest() + ' ')
sevenzip = shutil.which('7z') or 'C:/Program Files/7-Zip/7z.exe'
checked = subprocess.check_output([sevenzip, 't', str(image)], text=True)
assert 'Everything is Ok' in checked and 'WARNINGS' not in checked and 'CRC Error' not in checked, checked
listing = subprocess.check_output([sevenzip, 'l', '-slt', str(image)], text=True)
assert 'Type = Dmg' in listing and 'Type = HFS' in listing
manifest = json.loads((ROOT / 'outputs/macos-dmg-build/image-manifest.json').read_text(encoding='utf-8'))
with tempfile.TemporaryDirectory(prefix='dmg-check-', dir=ROOT / 'outputs') as temp:
    subprocess.run([sevenzip, 'x', '-y', '-o' + temp, str(image)], check=True, stdout=subprocess.DEVNULL)
    volume = Path(temp) / 'Smart Clock Setup'
    for name, expected in manifest['files'].items():
        file = volume / name
        assert file.is_file(), name
        assert hashlib.sha256(file.read_bytes()).hexdigest() == expected['sha256'], name
        native_path = 'Smart Clock Setup\\' + name.replace('/', '\\')
        section = next(part for part in listing.split('\n\n') if 'Path = ' + native_path + '\n' in part)
        permission = '-rwxr-xr-x' if expected['mode'] == 0o755 else '-rw-r--r--'
        assert 'Mode = ' + permission in section, (name, section)
        bash = Path('C:/Program Files/Git/bin/bash.exe')
        if expected['mode'] == 0o755 and bash.exists():
            subprocess.run([str(bash), '-n', str(file)], check=True)
    dispatcher = volume / 'Smart Clock Setup.app/Contents/Resources/setup.command'
    text = dispatcher.read_text(encoding='utf-8')
    assert 'hw.optional.arm64' in text and 'arch -arm64' in text
print('UDIF/data/master checksums, independent HFS extraction, every bundle file hash, Mac execute permissions and universal dispatcher OK')
