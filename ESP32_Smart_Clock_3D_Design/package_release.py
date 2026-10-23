"""Build local publication packages, using only current design files."""
from pathlib import Path
import hashlib
import json
import zipfile

ROOT = Path(__file__).resolve().parent
OUT = ROOT / 'dist'
OUT.mkdir(exist_ok=True)


def package(name, paths, prefix=''):
    target = OUT / name
    with zipfile.ZipFile(target, 'w', compression=zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(set(paths)):
            assert path.is_file(), path
            archive.write(path, prefix + path.relative_to(ROOT).as_posix())
        if prefix:
            workflow = ROOT.parent / '.github/workflows/design.yml'
            if workflow.is_file(): archive.write(workflow, '.github/workflows/design.yml')
    with zipfile.ZipFile(target) as archive:
        assert archive.testzip() is None
        assert not any('rev17/' in n or 'secrets' in n or n.endswith('.bin') for n in archive.namelist())
    print(f'{target.name}: {target.stat().st_size:,} bytes')


if __name__ == '__main__':
    report = json.loads((ROOT / 'release_validation.json').read_text())
    for item in report['files']:
        assert hashlib.sha256((ROOT / item['file']).read_bytes()).hexdigest() == item['sha256'], item['file']
    models = sorted((ROOT / 'stl').glob('*.stl'))
    assert {p.name for p in models} == {'body.stl', 'lid.stl', 'sensor_cage.stl'}
    common = [ROOT / n for n in ['README.md', 'PRINT_GUIDE.pdf', 'LICENSE', 'ATTRIBUTION.md', 'measurements.json']]
    previews = sorted((ROOT / 'previews').glob('*.png'))
    samples = sorted((ROOT / 'test-pieces').glob('*.stl'))
    package('ESP32_Smart_Clock_Final_STLs.zip', models + [ROOT / n for n in ['START_HERE.txt', 'PRINT_GUIDE.pdf', 'LICENSE', 'ATTRIBUTION.md']])
    package('ESP32_Smart_Clock_Creality_Upload.zip', models + samples + common + previews + list((ROOT / 'publication').glob('*')) + list((ROOT / 'print-profiles').glob('*')))
    source = [p for p in ROOT.rglob('*') if p.is_file()
              and not any(part in {'dist', '__pycache__', '.venv'} for part in p.relative_to(ROOT).parts)
              and p.suffix not in {'.log', '.pyc'}]
    package('ESP32_Smart_Clock_GitHub_Source.zip', source, ROOT.name + '/')
    paths = models + sorted(OUT.glob('*.zip'))
    (OUT / 'SHA256SUMS.txt').write_text(''.join(f'{hashlib.sha256(p.read_bytes()).hexdigest()}  {p.name}\n' for p in paths))
