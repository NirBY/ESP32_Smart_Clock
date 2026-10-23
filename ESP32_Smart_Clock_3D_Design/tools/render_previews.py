"""Render current STL meshes with OpenSCAD; images are CAD views, not photographs."""
import importlib.util
from pathlib import Path
import os
import shutil
import subprocess
import tempfile
import concurrent.futures

root = Path(__file__).resolve().parents[1]
exe = os.environ.get('OPENSCAD') or shutil.which('openscad')
if not exe and os.name == 'nt': exe = str(Path(os.environ.get('ProgramFiles', 'C:/Program Files')) / 'OpenSCAD/openscad.com')
if not exe or not Path(exe).is_file(): raise SystemExit('Set OPENSCAD or install OpenSCAD on PATH.')

def imported(name): return f'import("{(root / "stl" / (name + ".stl")).as_posix()}");'
body = 'color([.90,.91,.93])' + imported('body')
lid = 'color([.67,.72,.78])translate([0,60,51.2])rotate([180,0,0])' + imported('lid')
cage = 'color([.67,.72,.78])multmatrix([[1,0,0,49.5],[0,0,1,-11.5],[0,-1,0,49.2],[0,0,0,1]])' + imported('sensor_cage')
upright = 'multmatrix([[1,0,0,0],[0,0,1,0],[0,-1,0,66],[0,0,0,1]])'
closed = upright + '{' + body + lid + cage + '}'
views = {
    'cover': (closed, '0,0,0,63,0,330,300'),
    'rear': (closed, '0,0,0,63,0,150,300'),
    'exploded': (upright + '{' + body + 'translate([0,0,28])' + lid + 'translate([0,-17,0])' + cage + '}', '0,0,0,63,0,150,350'),
    'lid_inside': ('color([.80,.84,.89])' + imported('lid'), '0,0,0,25,0,0,300'),
    'lid_back': ('color([.80,.84,.89])' + imported('lid'), '0,0,0,155,0,0,300'),
}

def render(item):
    name, (source, camera) = item
    with tempfile.TemporaryDirectory(prefix='clock-preview-') as folder:
        scad = Path(folder) / 'view.scad'
        scad.write_text(source, encoding='utf8')
        dest = root / 'previews' / f'{name}.png'
        result = subprocess.run([exe, '-o', str(dest), '--imgsize=1600,1600', '--viewall', '--autocenter',
                                 '--camera=' + camera, '--projection=o', '--colorscheme=Tomorrow', str(scad)],
                                capture_output=True, text=True)
        if result.returncode: raise RuntimeError(result.stderr)
        print(f'Rendered {name}')

if __name__ == '__main__':
    (root / 'previews').mkdir(exist_ok=True)
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool: list(pool.map(render, views.items()))
