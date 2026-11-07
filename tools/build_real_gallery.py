"""Compose a rotating feature gallery from original project photographs."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageOps

ROOT = Path(__file__).resolve().parents[1]
IMAGES = ROOT / 'docs/images'
SLIDES = [
    ('clock-real.jpg', 'Time and date', 'Large, readable clock digits. Choose 12/24-hour time or seconds, with a date screen at the top of each hour.'),
    ('sensors-real.jpg', 'Room conditions', 'Temperature, humidity and pressure in Home Assistant. Temperature and humidity on the clock.'),
    ('clock-real.jpg', 'Countdown timer', 'Start, pause, resume or cancel. Alternate the countdown with the clock and choose a completion sound.'),
    ('clock-real.jpg', 'Flexible alarms', 'Daily, weekly, monthly or specific-date alarms, with optional start and end dates.'),
    ('clock-real.jpg', 'Day / night brightness', 'Set time ranges in the Home Assistant editor. Adjust each range from 0 to 15, including overnight schedules.'),
    ('clock-real.jpg', 'Your messages', 'Send custom text from Home Assistant. English and Hebrew pixel text scroll across the matrix.'),
    ('clock-real.jpg', 'Sound your way', 'Choose separate alarm, hourly, timer, reminder and volume sounds. Test each choice from Home Assistant.'),
    ('clock-real.jpg', 'Music and controls', 'Play audio through the I2S speaker. Control playback and volume from Home Assistant; music search needs Music Assistant.'),
    ('desktop-setup.png', 'Guided desktop setup', 'Open the Windows EXE or Mac DMG. Fill in your settings, find USB, then build and install. No separate Python or Java setup.'),
    ('clock-real.jpg', 'Updates and recovery', 'Personalized firmware updates over USB or the network. Port refresh, total progress and verified downloads protect your setup.'),
    ('clock-real.jpg', 'Home Assistant + AI', 'Control sensors, settings, alarms and timers. Optional MCP scripts connect an authenticated AI client; setup and verification required.'),
    ('assembly-real.jpg', 'Make it your own', 'Print the enclosure, follow the wiring guide and assemble your clock. Editable sources, STL files and dashboard examples included.'),
]


def font(size, bold=False):
    candidates = [Path('C:/Windows/Fonts') / ('seguisb.ttf' if bold else 'segoeui.ttf'),
                  Path('/usr/share/fonts/truetype/dejavu') / ('DejaVuSans-Bold.ttf' if bold else 'DejaVuSans.ttf')]
    return next((ImageFont.truetype(str(p), size) for p in candidates if p.exists()), ImageFont.load_default(size=size))


def wrap(draw, text, face, width):
    lines = []; line = ''
    for word in text.split():
        trial = (line + ' ' + word).strip()
        if draw.textbbox((0, 0), trial, font=face)[2] > width and line:
            lines.append(line); line = word
        else:
            line = trial
    return lines + [line]


frames = []
for index, (name, title, description) in enumerate(SLIDES):
    frame = Image.new('RGB', (1000, 640), '#f5f3ef')
    draw = ImageDraw.Draw(frame)
    draw.text((24, 15), 'SMART CLOCK', font=font(26, True), fill='#14283a')
    draw.text((760, 25), 'REAL PROJECT PHOTOS', font=font(16, True), fill='#45617a')
    draw.rounded_rectangle((18, 77, 673, 583), radius=16, fill='white')
    photo = ImageOps.contain(Image.open(IMAGES / name).convert('RGB'), (640, 480), Image.Resampling.LANCZOS)
    frame.paste(photo, (26 + (640 - photo.width) // 2, 90 + (480 - photo.height) // 2))
    draw.text((703, 100), f'{index + 1:02d} / {len(SLIDES):02d}', font=font(18, True), fill='#2766c7')
    y = 148
    for line in wrap(draw, title, font(30, True), 270):
        draw.text((700, y), line, font=font(30, True), fill='#14283a'); y += 39
    y += 18
    for line in wrap(draw, description, font(20), 268):
        draw.text((701, y), line, font=font(20), fill='#33495c'); y += 29
    assert y < 565, (title, y)
    for item in range(len(SLIDES)):
        draw.rounded_rectangle((704 + item * 21, 555, 716 + item * 21, 560), radius=2,
                               fill='#2766c7' if item == index else '#c9d4dc')
    draw.text((25, 606), 'Original project photos + feature descriptions. Not every mode is photographed.', font=font(15), fill='#526475')
    frames.append(frame)

palette_sheet = Image.new('RGB', (1000, 640 * len(frames)))
for i, frame in enumerate(frames):
    palette_sheet.paste(frame, (0, i * 640))
palette = palette_sheet.resize((500, 320 * len(frames))).quantize(colors=256)
indexed = [frame.quantize(palette=palette, dither=Image.Dither.FLOYDSTEINBERG) for frame in frames]
target = IMAGES / 'clock-real-showcase.gif'
indexed[0].save(target, save_all=True, append_images=indexed[1:], duration=4500, loop=0, optimize=True, disposal=1)
storyboard = Image.new('RGB', (2000, 640 * 6), 'white')
for i, frame in enumerate(frames):
    storyboard.paste(frame, ((i % 2) * 1000, (i // 2) * 640))
storyboard.save(IMAGES / 'clock-real-storyboard.jpg', quality=88, optimize=True)
with Image.open(target) as check:
    assert check.n_frames == len(SLIDES) and check.info['loop'] == 0
print(f'{target.name}: {len(frames)} real-photo feature slides; {target.stat().st_size:,} bytes')
