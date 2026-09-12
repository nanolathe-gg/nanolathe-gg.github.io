#!/usr/bin/env python3
"""Build an original continuously packed FNT and byte-derived diagrams."""
import argparse
import struct
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / 'content/docs/fnt'
GLYPHS = {' ': ['000'] * 7,
          'A': ['01110', '10001', '10001', '11111', '10001', '10001', '10001'],
          'B': ['11110', '10001', '10001', '11110', '10001', '10001', '11110']}


def svg(body, width=760, height=340):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">'
            '<style>text{font-family:monospace;fill:#dbe9e4}.small{font-size:14px}.title{font-size:19px}</style>'
            f'<rect width="100%" height="100%" rx="12" fill="#111e26"/>{body}</svg>').encode()


def build():
    data = bytearray([7, 0, 2, 32]) + bytearray(224 * 2)
    for char, rows in GLYPHS.items():
        struct.pack_into('<H', data, 4 + (ord(char) - 32) * 2, len(data))
        bits = ''.join(rows)
        bits += '0' * (-len(bits) % 8)
        data += bytes([len(rows[0])]) + bytes(int(bits[i:i+8], 2) for i in range(0, len(bits), 8))
    offset = struct.unpack_from('<H', data, 4 + (65-32)*2)[0]
    packed = data[offset+1:offset+6]
    assert packed == bytes.fromhex('74 63 F8 C6 20')
    correct = [((packed[i//8] >> (7-i % 8)) & 1) for i in range(35)]
    wrong = [((packed[y] >> (7-x)) & 1) if y < len(packed) else 0 for y in range(7) for x in range(5)]
    body = '<text class="title" x="28" y="35">Continuous packing</text><text class="title" x="406" y="35">Incorrect row alignment</text>'
    for left, cells in [(28, correct), (406, wrong)]:
        for i, on in enumerate(cells):
            body += f'<rect x="{left + i%5*32}" y="{60+i//5*32}" width="30" height="30" fill="{"#82cbbb" if on else "#263b49"}"/>'
    body += '<text class="small" x="28" y="315">35 bits → 5 bitmap bytes</text><text class="small" x="406" y="315">Row 2 starts inside byte 0</text>'
    output = {'example.fnt': bytes(data), 'packing-comparison.svg': svg(body)}
    body = '<text class="title" x="26" y="35">A glyph · 5 × 7 · five packed bytes</text>'
    for i, on in enumerate(correct):
        color = ['#6dc5b4', '#e6b765', '#91a9ed', '#db93ac', '#abc577'][i//8]
        body += f'<rect x="{26+i%5*34}" y="{62+i//5*34}" width="32" height="32" fill="{color if on else "#263b49"}" stroke="{color}" stroke-width="2"/>'
    for i, byte in enumerate(packed):
        color = ['#6dc5b4', '#e6b765', '#91a9ed', '#db93ac', '#abc577'][i]
        body += f'<rect x="240" y="{62+i*47}" width="5" height="32" fill="{color}"/><text x="260" y="{84+i*47}" font-size="17">byte {i}: {byte:08b} = {byte:02X}</text>'
    body += '<text class="small" x="26" y="330">Border color groups bits by byte. Final five bits are padding.</text>'
    output['bit-packing.svg'] = svg(body, 760, 355)
    body = '<text class="title" x="26" y="35">A BA · bitmap width is also pen advance</text><path d="M26 135H730" stroke="#e6b765" stroke-dasharray="7 5"/><text class="small" x="550" y="160">penY = 9</text>'
    pen = 2
    for char in 'A BA':
        off = struct.unpack_from('<H', data, 4 + (ord(char)-32)*2)[0]
        width = data[off]
        raw = data[off+1:off+1+(width*7+7)//8]
        for i in range(width*7):
            if raw[i//8] & (0x80 >> (i % 8)):
                body += f'<rect x="{26+(pen+i%width)*20}" y="{95+i//width*20}" width="20" height="20" fill="#82cbbb"/>'
        body += f'<path d="M{26+pen*20} 80V245" stroke="#657886"/><text class="small" x="{26+pen*20}" y="285">+{width}</text>'
        pen += width
    body += '<text class="small" x="26" y="325">Blank space: width 3. First row = penY − 2. No extra spacing.</text>'
    output['text-metrics.svg'] = svg(body, 760, 350)
    return output


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
    print('FNT fixtures verified' if args.check else 'FNT fixtures generated')
