#!/usr/bin/env python3
"""Author two small SMK2 movies and decode their bytes into teaching assets.

Standard-library checks cover the fixture's solid/retain subset, not arbitrary
Smacker files. --verify-ffmpeg optionally compares every RGB pixel with FFmpeg.
No engine decoder source, retail imagery, or extracted palette is used.
"""
import argparse
import json
import struct
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / 'content/docs/zrb'
WIDTH, HEIGHT, COUNT, INTERVAL = 64, 32, 16, 125
COLORS = [(4, 5, 5), (15, 24, 22), (45, 59, 24), (57, 45, 27)]
WARM = [COLORS[0], COLORS[1], (57, 23, 17), COLORS[3]]
WORDS = [3, 259, 515, 771, 2]  # Four solid indices and one retained block.


class Writer:
    def __init__(self):
        self.bits = []

    def put(self, value, count=1):
        self.bits.extend((value >> i) & 1 for i in range(count))

    def data(self):
        out = bytearray((len(self.bits) + 7) // 8)
        for i, bit in enumerate(self.bits):
            out[i // 8] |= bit << (i % 8)
        return bytes(out)


class Reader:
    def __init__(self, data):
        self.data, self.pos = data, 0

    def get(self, count=1):
        assert self.pos + count <= len(self.data) * 8, 'Truncated bits'
        value = 0
        for i in range(count):
            value |= ((self.data[self.pos // 8] >> (self.pos % 8)) & 1) << i
            self.pos += 1
        return value


def tree(values):
    if len(values) == 1:
        return values[0]
    mid = len(values) // 2
    return tree(values[:mid]), tree(values[mid:])


def codes(node, path=()):
    if isinstance(node, int):
        return {node: path}
    return codes(node[0], path + (0,)) | codes(node[1], path + (1,))


def write_tree(out, node, leaf):
    out.put(int(not isinstance(node, int)))
    if isinstance(node, int):
        leaf(node)
    else:
        write_tree(out, node[0], leaf)
        write_tree(out, node[1], leaf)


def read_tree(bits, leaf):
    if bits.get() == 0:
        return leaf()
    return read_tree(bits, leaf), read_tree(bits, leaf)


def symbol(bits, node):
    while not isinstance(node, int):
        node = node[bits.get()]
    return node


def emit(out, paths, value):
    for bit in paths[value]:
        out.put(bit)


def author(scene):
    out = Writer()
    out.put(0, 3)  # Absent map, color-pair and full-color trees.
    out.put(1)  # Present type tree.
    byte_trees = [tree([2, 3]), tree([0, 1, 2, 3])]
    for node in byte_trees:
        out.put(1)
        write_tree(out, node, lambda v: out.put(v, 8))
        out.put(0)  # Each present tree has a terminating zero.
    for marker in [65535, 65534, 65533]:
        out.put(marker, 16)
    paths = [codes(t) for t in byte_trees]
    def word(value):
        emit(out, paths[0], value & 255)
        emit(out, paths[1], value >> 8)
    type_tree = tree(WORDS)
    write_tree(out, type_tree, word)
    out.put(0)
    trees = out.data()
    packets, masks, expected = [], [], []
    previous = None
    for frame in range(COUNT):
        if scene == 'palette':
            # Frame 8 changes only the palette, retaining every index from frame 7.
            sweep = frame if frame < 8 else frame - 1
            wave = [4, 4, 3, 4, 5, 4, 2, 1, 6, 4, 3, 4, 5, 4, 4, 4]
            blocks = [2 if y == wave[x] else 1 if y == 4 else 0
                      for y in range(8) for x in range(16)]
            for y in range(1, 7):
                blocks[y * 16 + sweep] = 3
        else:
            # A 16 × 12 rectangle moves out and back, changing palette indices.
            # Its palette stays fixed throughout the clip.
            left = 1 + min(frame, COUNT - frame)
            color = [2, 3, 1, 2][frame // 4]
            blocks = [color if left <= x < left + 4 and 2 <= y < 5 else 0
                      for y in range(8) for x in range(16)]
        video = Writer()
        for i, value in enumerate(blocks):
            emit(video, codes(type_tree), 2 if previous and previous[i] == value else (value << 8) | 3)
        palette = b''
        if frame == 0 or (scene == 'palette' and frame == 8):
            # Four RGB literals, then retain the remaining 252 palette entries.
            payload = bytes(v for rgb in (COLORS if frame == 0 else WARM) for v in rgb) + bytes([255, 251])
            palette = bytes([4]) + payload + b'\0'  # Total chunk = 16 bytes.
        packet = palette + video.data()
        packet += b'\0' * (-len(packet) % 4)
        packets.append(packet)
        masks.append(int(bool(palette)))
        expected.append(blocks)
        previous = blocks
    header = bytearray(104)
    struct.pack_into('<4sIIIiI', header, 0, b'SMK2', WIDTH, HEIGHT, COUNT, INTERVAL, 4 if scene == 'palette' else 0)
    struct.pack_into('<5I', header, 52, len(trees), 0, 0, 0, 1024)
    sizes = b''.join(struct.pack('<I', len(p) | int(i == 0)) for i, p in enumerate(packets))
    return bytes(header) + sizes + bytes(masks) + trees + b''.join(packets), expected


def decode(data):
    assert data[:4] == b'SMK2'
    width, height, count, interval, flags = struct.unpack_from('<IIIiI', data, 4)
    assert (width, height, count, interval) == (WIDTH, HEIGHT, COUNT, INTERVAL)
    assert flags in (0, 4)
    sizes = struct.unpack_from(f'<{count}I', data, 104)
    masks = data[104 + 4 * count:104 + 5 * count]
    tree_size = struct.unpack_from('<I', data, 52)[0]
    offset = 104 + 5 * count
    bits = Reader(data[offset:offset + tree_size])
    assert bits.get(3) == 0 and bits.get() == 1
    byte_trees = []
    for _ in range(2):
        assert bits.get() == 1
        byte_trees.append(read_tree(bits, lambda: bits.get(8)))
        assert bits.get() == 0
    markers = [bits.get(16) for _ in range(3)]
    types = read_tree(bits, lambda: symbol(bits, byte_trees[0]) | (symbol(bits, byte_trees[1]) << 8))
    assert bits.get() == 0
    offset += tree_size
    palette, pixels, frames = [(0, 0, 0)] * 256, [0] * (width * height), []
    for frame, raw_size in enumerate(sizes):
        size = raw_size & ~3
        packet = data[offset:offset + size]
        assert len(packet) == size
        cursor = 0
        if masks[frame] & 1:
            cursor = packet[0] * 4
            old, i, pos = palette[:], 0, 1
            while i < 256 and pos < cursor:
                c = packet[pos]
                pos += 1
                if c & 128:
                    i += (c & 127) + 1
                elif c & 64:
                    n, source = (c & 63) + 1, packet[pos]
                    pos += 1
                    palette[i:i + n] = old[source:source + n]
                    i += n
                else:
                    palette[i] = tuple((v << 2) | (v >> 4) for v in (c, packet[pos], packet[pos + 1]))
                    pos += 2
                    i += 1
            assert i == 256
        video = Reader(packet[cursor:])
        operations = []
        for block in range(width * height // 16):
            value = symbol(video, types)
            assert value not in markers and (value & 252) == 0
            op = value & 3
            assert op in (2, 3)
            operations.append(op)
            if op == 3:
                x, y = (block % (width // 4)) * 4, (block // (width // 4)) * 4
                for row in range(4):
                    pixels[(y + row) * width + x:(y + row) * width + x + 4] = [value >> 8] * 4
        frames.append(dict(index=frame, offset=offset, size=size, mask=masks[frame],
                           paletteBytes=cursor, videoAndPaddingBytes=size - cursor,
                           solid=operations.count(3), retained=operations.count(2),
                           pixels=pixels[:], palette=palette[:4], operations=operations))
        offset += size
    assert offset == len(data)
    return frames


def svg(frame, operations=False):
    rects = []
    for block, op in enumerate(frame['operations']):
        x, y = block % 16 * 4, block // 16 * 4
        rgb = frame['palette'][frame['pixels'][y * WIDTH + x]]
        color = ('#b6ef63' if op == 3 else '#22292a') if operations else '#%02x%02x%02x' % tuple(rgb)
        outline = ' stroke="#53615a" stroke-width=".12"' if operations else ''
        rects.append(f'<rect x="{x}" y="{y}" width="4" height="4" fill="{color}"{outline}/>')
        if operations and op == 2:
            rects.append(f'<path d="M{x+1} {y+2}h2" stroke="#a8b09e" stroke-width=".35"/>')
    title = f"Frame {frame['index']}: " + ('solid writes and retained blocks' if operations else frame['description'])
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="640" height="320" viewBox="0 0 64 32" preserveAspectRatio="none" shape-rendering="crispEdges"><title>{title}</title>' + ''.join(rects) + '</svg>').encode()


def build():
    assets, reference_clips = {}, []
    for scene, name, prefix in [('rectangle', 'rectangle', 'rectangle-'), ('palette', 'example', '')]:
        data, expected = author(scene)
        frames = decode(data)
        for frame, blocks in zip(frames, expected):
            pixels = [blocks[(y // 4) * 16 + x // 4] for y in range(HEIGHT) for x in range(WIDTH)]
            assert frame['pixels'] == pixels
            colors = WARM if scene == 'palette' and frame['index'] >= 8 else COLORS
            assert frame['palette'] == [tuple((v << 2) | (v >> 4) for v in rgb) for rgb in colors]
            index = frame['index']
            if scene == 'rectangle':
                color = ['green', 'amber', 'teal', 'green'][index // 4]
                left = 4 * (1 + min(index, COUNT - index))
                frame['description'] = f'{color} rectangle, 16 × 12 pixels, at ({left}, 8)'
                frame['note'] = ('The first packet writes the rectangle and its background.' if index == 0 else
                                 'The rectangle changes color by writing a different palette index. The palette stays fixed.' if index in (4, 8, 12) else
                                 'Solid writes move the rectangle and erase its trailing edge. The rest of the picture is retained.')
            else:
                frame['description'] = f"original {'green' if index < 8 else 'red'} waveform with an amber scan column"
                frame['note'] = ('The first packet defines four palette colors and writes every block.' if index == 0 else
                                 'Only the palette changes: all 128 blocks retain their indices, but the waveform turns red.' if index == 8 else
                                 'Twelve solid writes move the scan column; the other 116 blocks retain their previous indices.')
        assert frames[0]['solid'] == 128
        if scene == 'palette':
            assert frames[8]['retained'] == 128 and frames[8]['pixels'] == frames[7]['pixels']
            assert frames[8]['palette'] != frames[7]['palette']
        else:
            assert all(f['paletteBytes'] == 0 for f in frames[1:])
            assert all(f['pixels'] != frames[i - 1]['pixels'] for i, f in enumerate(frames) if i)
            assert all(f['solid'] == (15 if f['index'] in (4, 8, 12) else 6) for f in frames[1:])
        assets[f'{name}.zrb'] = data
        for frame in frames:
            assets[f"{prefix}frame-{frame['index']}.svg"] = svg(frame)
            assets[f"{prefix}blocks-{frame['index']}.svg"] = svg(frame, True)
        metadata = dict(width=WIDTH, height=HEIGHT, displayHeight=HEIGHT * (2 if scene == 'palette' else 1),
                        intervalMs=INTERVAL, fileBytes=len(data), prefix=prefix,
                        frames=[{k: v for k, v in f.items() if k != 'pixels'} for f in frames])
        assets[f'{name}.json'] = (json.dumps(metadata, indent=2) + '\n').encode()
        reference_clips.append((name, frames))
    return assets, reference_clips


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    parser.add_argument('--verify-ffmpeg', action='store_true')
    args = parser.parse_args()
    assets, reference_clips = build()
    if args.verify_ffmpeg:
        with tempfile.TemporaryDirectory(prefix='zrb-reference-') as tmp:
            for name, frames in reference_clips:
                movie = Path(tmp) / f'{name}.smk'
                movie.write_bytes(assets[f'{name}.zrb'])
                result = subprocess.run(['ffmpeg', '-v', 'error', '-i', str(movie), '-f', 'rawvideo',
                                         '-pix_fmt', 'rgb24', '-'], check=True, capture_output=True)
                expected = bytes(c for f in frames for p in f['pixels'] for c in f['palette'][p])
                assert result.stdout == expected, f'{name}: FFmpeg RGB output differs'
                print(f'{name}: FFmpeg matches all {len(frames)} RGB24 frames ({len(expected):,} bytes).')
    for name, data in assets.items():
        path = ROOT / name
        if args.check:
            if not path.exists() or path.read_bytes() != data:
                raise SystemExit(f'Fixture differs: {path}')
        else:
            path.write_bytes(data)
    print('ZRB fixtures verified' if args.check else 'ZRB fixtures generated')
