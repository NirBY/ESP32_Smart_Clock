"""Package ImageGen's eight-slide storyboard as a GitHub-compatible GIF."""
from pathlib import Path
from PIL import Image, ImageOps

root = Path(__file__).resolve().parents[1]
source = Image.open(root / 'docs/images/showcase-storyboard.png').convert('RGB')
# Panel dividers measured in the generated 1024 x 1536 storyboard.
rows = (0, 384, 758, 1126, 1536)
frames = []
for top, bottom in zip(rows, rows[1:]):
    for left, right in ((0, 512), (512, 1024)):
        box = tuple(round(v * source.width / 1024) for v in (left, top, right, bottom))
        panel = source.crop(box)
        frame = ImageOps.pad(panel, (768, 576), method=Image.Resampling.LANCZOS, color='#020b1e')
        frames.append(frame.quantize(colors=256, method=Image.Quantize.MEDIANCUT))
target = root / 'docs/images/clock-showcase.gif'
frames[0].save(target, save_all=True, append_images=frames[1:], duration=4000, loop=0, disposal=2, optimize=False)
with Image.open(target) as check:
    assert check.n_frames == 8 and check.size == (768, 576)
    assert check.info['loop'] == 0
print(f'{target.name}: eight slides, four seconds each; {target.stat().st_size:,} bytes')
