"""Validate current models, fit samples and important geometry."""
from pathlib import Path
import hashlib
import json
import subprocess
import sys
import trimesh

root = Path(__file__).resolve().parent
checks = ['validate_revision.py', 'check_features.py', 'check_integrated_cover.py',
          'check_power_position.py', 'check_bottom_vents.py', 'check_sensor_installation.py']
for check in checks:
    result = subprocess.run([sys.executable, str(root / check)], cwd=root, capture_output=True, text=True)
    if result.returncode:
        raise SystemExit(f'{check} FAILED\n{result.stdout}\n{result.stderr}')
    print(f'PASS {check}')
files = []
for folder in ['stl', 'test-pieces']:
    for path in sorted((root / folder).glob('*.stl')):
        mesh = trimesh.load_mesh(path)
        components = len(mesh.split(only_watertight=False))
        assert mesh.is_volume and components == 1, path
        files.append({'file': path.relative_to(root).as_posix(),
                      'sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
                      'bytes': path.stat().st_size, 'components': components,
                      'watertight': bool(mesh.is_watertight),
                      'bounds_mm': mesh.bounds.tolist()})
report = {'revision': 18, 'units': 'mm', 'checks_passed': checks, 'files': files,
          'physical_validation': 'Creator confirms working printed assembly and white PLA diffuser.'}
(root / 'release_validation.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf8')
print('PASS: all three assembly parts and both fit samples are single watertight solids.')
