#!/usr/bin/env python3
"""Generate original PAL fixtures and matching explanatory SVGs; no retail data."""
import argparse
import colorsys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / 'content/docs/pal'


def build():
    day = [(13, 25, 38), (29, 50, 65), (41, 81, 99), (83, 143, 157),
           (160, 211, 202), (230, 243, 217), (250, 185, 72), (210, 105, 62)]
    night = [(10, 13, 32), (28, 25, 59), (50, 40, 88), (103, 75, 142),
             (169, 126, 186), (242, 221, 230), (250, 142, 117), (170, 77, 114)]
    for i in range(8, 256):
        rgb = tuple(round(c * 255) for c in colorsys.hsv_to_rgb((i % 32) / 32, .65, .3 + (i // 32) / 10))
        day.append(rgb)
        night.append(rgb)
    pixels = []
    for y in range(20):
        for x in range(32):
            c = 1 if y < 13 else 2
            if (x - 25) ** 2 + (y - 4) ** 2 < 8:
                c = 6
            if y >= 13 and (x + y) % 7 == 0:
                c = 3
            if 9 <= x <= 21 and 11 <= y <= 14:
                c = 3
            if 13 <= x <= 17 and 6 <= y <= 11:
                c = 4
            if 14 <= x <= 16 and y == 7:
                c = 5
            if 12 <= x <= 18 and y == 5:
                c = 6
            if 14 <= x <= 16 and y == 4:
                c = 7
            pixels.append(c)
    outputs = {'indices.bin': bytes(pixels)}
    for name, palette in [('day', day), ('night', night)]:
        outputs[f'{name}.pal'] = bytes(v for rgb in palette for v in (*rgb, 0))
        cells = ''.join(f'<rect x="{i % 32 * 20}" y="{i // 32 * 20}" width="20" height="20" fill="rgb{palette[c]}"/>' for i, c in enumerate(pixels))
        outputs[f'{name}.svg'] = f'<svg xmlns="http://www.w3.org/2000/svg" width="640" height="400" viewBox="0 0 640 400"><title>Original beacon with the {name} palette</title>{cells}</svg>'.encode()
    cells = ''.join(f'<rect x="{i % 16 * 40}" y="{i // 16 * 30}" width="40" height="30" fill="rgb{rgb}"/>' for i, rgb in enumerate(day))
    outputs['palette-grid.svg'] = f'<svg xmlns="http://www.w3.org/2000/svg" width="640" height="480" viewBox="0 0 640 480"><title>All 256 authored palette slots, index 0 at upper left, 255 at lower right</title>{cells}</svg>'.encode()
    assert len(outputs['day.pal']) == 1024 and len(outputs['indices.bin']) == 640
    assert outputs['day.pal'][24:28] == bytes([250, 185, 72, 0])
    return outputs


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
    print('PAL fixtures verified' if args.check else 'PAL fixtures generated')
