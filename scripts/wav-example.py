#!/usr/bin/env python3
"""Generate original PCM chirps in RIFF, raw, and fixed-layout DIGI containers."""
import argparse
import io
import math
import struct
import wave
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / 'content/docs/wav'
RATE, COUNT = 11025, 4410


def riff(payload, bits):
    fmt = struct.pack('<HHIIHH', 1, 1, RATE, RATE * bits//8, bits//8, bits)
    chunks = b'fmt ' + struct.pack('<I', 16) + fmt + b'data' + struct.pack('<I', len(payload)) + payload
    return b'RIFF' + struct.pack('<I', len(chunks)+4) + b'WAVE' + chunks


def build():
    samples = []
    for i in range(COUNT):
        t = i / RATE
        envelope = min(1, i/220) * max(0, 1 - i/(COUNT-1))**2
        samples.append(.28 * envelope * math.sin(2*math.pi*(880*t - 550*t*t)))
    pcm8 = bytes(round(128 + 127*s) for s in samples)
    pcm16 = b''.join(struct.pack('<h', round(32767*s)) for s in samples)
    wav8, wav16 = riff(pcm8, 8), riff(pcm16, 16)
    digi = bytearray(40)
    digi[:4], digi[8:12], digi[32:36] = b'DIGI', b'HSHD', b'SDAT'
    struct.pack_into('<I', digi, 22, RATE)
    # Unused size fields deliberately remain zero: this is a reader fixture.
    for data, width in [(wav8, 1), (wav16, 2)]:
        with wave.open(io.BytesIO(data), 'rb') as parsed:
            assert parsed.getnchannels() == 1 and parsed.getsampwidth() == width
            assert parsed.getframerate() == RATE and parsed.getnframes() == COUNT
            assert parsed.readframes(COUNT) == (pcm8 if width == 1 else pcm16)
    bars = ''
    for n in range(640):
        chunk = pcm8[n*COUNT//640:(n+1)*COUNT//640]
        lo, hi = min(chunk), max(chunk)
        bars += f'<path d="M{60+n} {160-(hi-128)*2.4:.2f}V{160-(lo-128)*2.4:.2f}" stroke="#82cbbb" stroke-width="1.2"/>'
    svg = ('<svg xmlns="http://www.w3.org/2000/svg" width="760" height="300" viewBox="0 0 760 300">'
           '<title>Waveform of the original 400-millisecond descending chirp</title>'
           '<rect width="760" height="300" rx="12" fill="#111e26"/>'
           '<g fill="#dbe9e4" font-family="monospace"><text x="28" y="36" font-size="19">4,410 samples · 11,025 Hz · 0.400 seconds</text>'
           '<text x="30" y="165" font-size="13">128</text><text x="60" y="265">0 ms</text><text x="325" y="265">200 ms</text><text x="640" y="265">400 ms</text></g>'
           '<path d="M60 160H700" stroke="#435763" stroke-dasharray="5 5"/>' + bars + '</svg>').encode()
    return {'example-8bit.wav': wav8, 'example-16bit.wav': wav16,
            'example-raw.wav': pcm8, 'example-digi.wav': bytes(digi)+pcm8,
            'waveform.svg': svg}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    for name, data in build().items():
        path = ROOT / name
        if args.check:
            if not path.exists() or path.read_bytes() != data:
                raise SystemExit(f'Fixture differs: {path}')
        else:
            path.write_bytes(data)
    print('WAV fixtures verified' if args.check else 'WAV fixtures generated')
