"""Generate compact, original alert sounds: 16 kHz mono PCM, no runtime synthesis."""
import math
import struct
import wave
from pathlib import Path
RATE = 16000

def generate(name, duration, notes):
    samples = [0.0] * round(duration * RATE)
    for start, length, frequency, harmonics in notes:
        for n in range(round(length * RATE)):
            t = n / RATE
            envelope = max(0, min(1, t / .012, (length-t) / .045))
            tone = (math.sin(2*math.pi*frequency*t) + harmonics*math.sin(4*math.pi*frequency*t))/(1+harmonics)
            samples[round(start*RATE)+n] += .32*envelope*tone
    assert max(map(abs,samples)) <= .33
    target = Path(__file__).resolve().parents[1] / 'media' / name
    with wave.open(str(target), 'wb') as output:
        output.setparams((1,2,RATE,0,'NONE','not compressed'))
        output.writeframes(b''.join(struct.pack('<h',round(x*32767)) for x in samples))
    print(f'{name}: {target.stat().st_size} bytes')

if __name__ == '__main__':
    generate('double-beep.wav', .48, [(0,.12,1000,0),(.22,.12,1000,0)])
    generate('classic-alarm.wav', 1.45, [(i*.16,.09,2000,.15) for i in (0,1,2,3,5,6,7)])
    generate('cuckoo.wav', 1.15, [(0,.32,784,.12),(.40,.42,659.25,.12)])
