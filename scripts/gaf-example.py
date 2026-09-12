"""Build original GAF teaching assets; no retail inputs or third-party libraries.

The SVGs and manifest are decoded from the authored binary, not parallel mockups.
Run with --check to verify committed outputs without writing them.
"""
import json
import math
from pathlib import Path
import struct
import sys

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'content/docs/gaf'
PALETTE = ['#000000', '#303c32', '#537242', '#789e4b', '#a9d762', '#d8ef9f', '#f5f3cf', '#e7b66f', '#887447', '#5454fc'] + ['#121516'] * 246

def pulse(n):
    size = 12 + n * 4
    mid = size // 2
    pixels = []
    for y in range(size):
        for x in range(size):
            dx, dy = x - mid, y - mid
            d = math.hypot(dx, dy)
            angle = math.atan2(dy, dx)
            radius = size * (.32 + .07 * math.cos(angle * 8))
            if d < radius:
                ratio = d / radius
                c = 0 if d < 1.5 else 6 if ratio < .4 else 5 if ratio < .6 else 4 if ratio < .78 else 3 if ratio < .92 else 2
            else:
                c = 9
            pixels.append(c)
    return size, size, mid, mid, pixels

def mask():
    size = 24
    return size, size, 12, 12, [0 if abs(x-12)+abs(y-12) < 11 else 9 for y in range(size) for x in range(size)]

def rle(w, h, pixels):
    output = bytearray()
    for y in range(h):
        row = pixels[y*w:(y+1)*w]
        payload = bytearray()
        x = 0
        while x < w:
            v = row[x]
            end = x + 1
            while end < w and row[end] == v and end-x < (127 if v == 9 else 64):
                end += 1
            count = end-x
            if v == 9:
                payload.append(count*2+1)
            else:
                payload.extend(((count-1)*4+2, v))
            x = end
        output.extend(struct.pack('<H', len(payload)))
        output.extend(payload)
    return output

# Pointer-linked layout: pixels and frame headers precede the entry headers.
bank = bytearray(struct.pack('<III', 0x00010100, 2, 0) + bytes(8))
entries = []
for name, frames, compressed in [('PULSE', [pulse(i) for i in range(6)], 1), ('MASK', [mask()], 0)]:
    refs = []
    for w, h, ox, oy, pixels in frames:
        data_offset = len(bank)
        bank.extend(rle(w,h,pixels) if compressed else bytes(pixels))
        frame_offset = len(bank)
        bank.extend(struct.pack('<HHhhBBHIII', w,h,ox,oy,9,compressed,0,0,data_offset,0))
        refs.append(frame_offset)
    entry_offset = len(bank)
    bank.extend(struct.pack('<HHI32s',len(refs),1,0,name.encode()))
    for ref in refs:
        bank.extend(struct.pack('<II',ref,3))
    entries.append(entry_offset)
for i, entry in enumerate(entries):
    struct.pack_into('<I',bank,12+i*4,entry)

# Independent reader checks pointers, row boundaries, run expansion and geometry.
def decode(blob):
    version, count, reserved = struct.unpack_from('<III',blob)
    assert (version,count,reserved) == (0x00010100,2,0)
    decoded = []
    for i in range(count):
        entry, = struct.unpack_from('<I',blob,12+i*4)
        n, loop, unused, name = struct.unpack_from('<HHI32s',blob,entry)
        frames = []
        for j in range(n):
            offset, hold = struct.unpack_from('<II',blob,entry+40+j*8)
            w,h,ox,oy,key,compressed,children,u2,data,u3 = struct.unpack_from('<HHhhBBHIII',blob,offset)
            assert w*h and not children
            cursor = data
            pixels = []
            for y in range(h):
                if not compressed:
                    row = list(blob[cursor:cursor+w]); cursor += w
                    assert len(row) == w
                    row = [None if c == key else c for c in row]
                else:
                    length, = struct.unpack_from('<H',blob,cursor)
                    cursor += 2; end = cursor+length; row = []
                    while cursor < end:
                        cmd = blob[cursor]; cursor += 1
                        if cmd & 1:
                            assert cmd >> 1
                            row.extend([None]*(cmd>>1))
                        elif cmd & 2:
                            row.extend([blob[cursor]]*((cmd>>2)+1)); cursor += 1
                        else:
                            run = (cmd>>2)+1
                            row.extend(blob[cursor:cursor+run]); cursor += run
                        assert len(row) <= w and cursor <= end
                    assert cursor == end
                    if not length: row = [None]*w
                    assert len(row) == w
                pixels.extend(row)
            frames.append(dict(width=w,height=h,x=ox,y=oy,hold=hold,offset=offset,dataOffset=data,pixels=pixels))
        decoded.append(dict(name=name.rstrip(b'\0').decode(),offset=entry,loop=loop,frames=frames))
    return decoded

assets = {}
def svg(w,h,pixels,show_key=False):
    rects = ''.join(f'<rect x="{i%w}" y="{i//w}" width="1" height="1" fill="{PALETTE[9 if c is None else c]}"/>' for i,c in enumerate(pixels) if c is not None or show_key)
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" shape-rendering="crispEdges">{rects}</svg>\n'.encode()

decoded = decode(bank)
for i,frame in enumerate(decoded[0]['frames']):
    authored = pulse(i)
    assert frame['pixels'] == [None if c == 9 else c for c in authored[4]]
    assets[f'pulse-{i}.svg'] = svg(frame['width'],frame['height'],frame['pixels'])
frame = decoded[1]['frames'][0]
assets['mask-keyed.svg'] = svg(24,24,frame['pixels'])
assets['mask-storage.svg'] = svg(24,24,frame['pixels'],True)
assets['example.gaf'] = bytes(bank)
assets['example-palette.json'] = (json.dumps(PALETTE,indent=2)+'\n').encode()
manifest = dict(byteLength=len(bank), entries=[dict(e,frames=[{k:v for k,v in f.items() if k!='pixels'} for f in e['frames']]) for e in decoded])
assets['example.json'] = (json.dumps(manifest,indent=2)+'\n').encode()
# Six indexed frames on one checkerboard sheet, available without JavaScript.
parts=['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 720 148" width="720" height="148"><defs><pattern id="grid" width="12" height="12" patternUnits="userSpaceOnUse"><path fill="#22292a" d="M0 0h12v12H0z"/><path fill="#2c3333" d="M0 0h6v6H0zM6 6h6v6H6z"/></pattern></defs>']
for i,f in enumerate(decoded[0]['frames']):
    x=i*120
    parts.append(f'<rect x="{x+2}" y="2" width="116" height="116" fill="url(#grid)"/>')
    ox=x+60-f['x']*3; oy=60-f['y']*3
    for j,c in enumerate(f['pixels']):
        if c is not None: parts.append(f'<rect x="{ox+j%f["width"]*3}" y="{oy+j//f["width"]*3}" width="3" height="3" fill="{PALETTE[c]}"/>')
    parts.append(f'<text x="{x+60}" y="139" text-anchor="middle" font-family="monospace" font-size="12" fill="#a8b09e">{i:02d} · {f["width"]}×{f["height"]}</text>')
parts.append('</svg>')
assets['contact-sheet.svg']=''.join(parts).encode()
# Educational composition: two overlapping leaves, larger than the parent.
for clipped in (False,True):
    clip=' clip-path="url(#parent)"' if clipped else ''
    body=f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 300 180" width="300" height="180"><defs><clipPath id="parent"><rect x="86" y="26" width="128" height="128"/></clipPath></defs><g{clip}><path d="M38 74h112v-32h48v64H86v32H38z" fill="#789e4b"/><path d="M126 90h88V58h48v64h-88v32h-48z" fill="#e7b66f"/></g><rect x="86" y="26" width="128" height="128" fill="none" stroke="#edf0e7" stroke-dasharray="4 4"/><path d="M142 90h16m-8-8v16" stroke="#fff" stroke-width="2"/></svg>'''
    assets[f'composition-{ "clipped" if clipped else "destination"}.svg']=body.encode()
for name,data in assets.items():
    path=OUT/name
    if '--check' in sys.argv:
        assert path.read_bytes() == data, f'Stale generated asset: {path}'
    else:
        path.write_bytes(data)
print(f'{"Verified" if "--check" in sys.argv else "Generated"} {len(assets)} original assets; {len(bank)}-byte GAF, 2 entries, 7 independently decoded frames.')
