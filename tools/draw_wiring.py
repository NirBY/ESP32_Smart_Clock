"""Export KiCad wiring sheets. Requires KiCad 10 and PyMuPDF.
Run: python tools/draw_wiring.py --kicad-cli PATH
Omit the option if kicad-cli is on PATH.
"""
import argparse
import shutil
import subprocess
import tempfile
from pathlib import Path
import pymupdf

root = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--kicad-cli', default=shutil.which('kicad-cli'))
args = parser.parse_args()
if not args.kicad_cli:
    parser.error('Install KiCad and supply --kicad-cli or add its bin directory to PATH.')
images = root / 'docs/images'
with tempfile.TemporaryDirectory() as temporary:
    out = Path(temporary)
    combined = pymupdf.open()
    for stem, target in [('power-distribution', 'power-distribution'), ('clock-wiring', 'wiring')]:
        source = root / 'docs/hardware' / (stem + '.kicad_sch')
        for fmt in ['pdf', 'svg']:
            destination = out / (stem + '.pdf') if fmt == 'pdf' else out
            subprocess.run([args.kicad_cli, 'sch', 'export', fmt,
                '--exclude-drawing-sheet', '--black-and-white', '--default-font', 'Arial',
                '-o', str(destination), str(source)], check=True)
        (images / (target + '.svg')).write_text('\n'.join(line.rstrip() for line in (out / (stem + '.svg')).read_text().splitlines()) + '\n')
        with pymupdf.open(out / (stem + '.pdf')) as doc:
            combined.insert_pdf(doc)
            doc[0].get_pixmap(dpi=300).save(images / (target + '.png'))
    combined.save(root / 'docs/hardware/clock-wiring.pdf')
    combined.close()
print('Exported two-sheet PDF, vector SVGs and 300 dpi PNGs.')
