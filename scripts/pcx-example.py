#!/usr/bin/env python3
"""Create original PCX files plus standard-stride / retail-width comparisons."""
import argparse
import struct
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / 'content/docs/pcx'
COLORS = [(13, 25, 38), (29, 50, 65), (41, 81, 99), (83, 143, 157),
          (160, 211, 202), (230, 243, 217), (250, 185, 72), (210, 105, 62)]
PALETTE = COLORS + [(i, i, i) for i in range(8, 256)]
PALETTE[197] = (250, 185, 72)


def encode(row):
    data = bytearray()
    i = 0
    while i < len(row):
        count = 1
        while i + count < len(row) and row[i+count] == row[i] and count < 63:
            count += 1
        if count > 1 or row[i] >= 0xC0:
            data += bytes([0xC0 | count, row[i]])
        else:
            data.append(row[i])
        i += count
    return bytes(data)


def pcx(width, height, stride, rows, literal=False):
    head = bytearray(128)
    head[:4] = bytes([10, 5, 1, 8])
    struct.pack_into('<4H', head, 4, 0, 0, width-1, height-1)
    struct.pack_into('<2H', head, 12, 72, 72)
    head[65] = 1
    struct.pack_into('<2H', head, 66, stride, 1)
    raw = b''.join(bytes(row) if literal else encode(row) for row in rows)
    return bytes(head) + raw + b'\x0c' + bytes(c for rgb in PALETTE for c in rgb)


def decode(data, standard=False):
    xmin, ymin, xmax, ymax = struct.unpack_from('<4H', data, 4)
    width, height = xmax-xmin+1, ymax-ymin+1
    span = struct.unpack_from('<H', data, 66)[0] if standard else width
    rows, pos = [], 128
    for _ in range(height):
        row = []
        while len(row) < span:
            value = data[pos]
            pos += 1
            count = 1
            if value >= 0xC0:
                count, value = value & 63, data[pos]
                pos += 1
            assert count > 0 and pos < len(data)-768
            row += [value] * min(count, span-len(row))
        rows.append(row[:width])
    return rows


def render(rows):
    width, height = len(rows[0])*32, len(rows)*32
    cells = ''.join(f'<rect x="{x*32}" y="{y*32}" width="32" height="32" fill="rgb{PALETTE[value]}"/>' for y, row in enumerate(rows) for x, value in enumerate(row))
    return f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}"><title>Original PCX calibration tile decoded from fixture bytes</title>{cells}</svg>'.encode()


def build():
    rows = [[1]*16 for _ in range(12)]
    for y in range(2, 10):
        for x in range(3, 12):
            rows[y][x] = 3 if x in (3, 11) or y in (2, 9) else 2
    for y in range(4, 8):
        for x in range(6, 9):
            rows[y][x] = 197
    main = pcx(16, 12, 16, rows)
    assert decode(main) == rows == decode(main, True)
    # Literal-only indexed pixels keep the padding demonstration transparent.
    padded_rows = [[(6 if x == 197 else x) for x in row[:15]] + [7] for row in rows]
    padded = pcx(15, 12, 16, padded_rows, True)
    assert decode(padded, True) == [r[:15] for r in padded_rows]
    assert decode(padded) != decode(padded, True)
    assert encode([3, 3, 3, 197, 197, 7]) == bytes.fromhex('C3 03 C2 C5 07')
    return {'example.pcx': main, 'padded.pcx': padded,
            'example.svg': render(decode(main)),
            'padding-standard.svg': render(decode(padded, True)),
            'padding-retail.svg': render(decode(padded))}


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
    print('PCX fixtures verified' if args.check else 'PCX fixtures generated')
