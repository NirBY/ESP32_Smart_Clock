"""Generate the original six-second timer melody (16 kHz mono PCM)."""
import math
import struct
import wave
from pathlib import Path

RATE = 16000
DURATION = 6.0
# Three ascending major-triad phrases, with space between repetitions.
NOTES = (659.255, 830.609, 987.767)
samples = [0.0] * int(RATE * DURATION)
for phrase in (0.25, 2.15, 4.05):
    for index, frequency in enumerate(NOTES):
        start = phrase + index * 0.48
        length = 0.65 if index == 2 else 0.42
        for n in range(int(length * RATE)):
            t = n / RATE
            envelope = min(1.0, t / 0.025, (length - t) / 0.15)
            tone = (math.sin(2 * math.pi * frequency * t)
                    + 0.12 * math.sin(4 * math.pi * frequency * t)) / 1.12
            samples[int(start * RATE) + n] += 0.34 * envelope * tone
assert max(abs(x) for x in samples) <= 0.34
target = Path(__file__).resolve().parents[1] / 'media' / 'timer-finished.wav'
with wave.open(str(target), 'wb') as output:
    output.setparams((1, 2, RATE, 0, 'NONE', 'not compressed'))
    output.writeframes(b''.join(struct.pack('<h', round(x * 32767)) for x in samples))
print(f'Generated {target.name}: {DURATION}s, peak {max(map(abs, samples)):.3f}')
