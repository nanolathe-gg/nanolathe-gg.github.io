#!/usr/bin/env python3
"""Build original, stored HPI examples and their pointer diagram; no retail bytes."""
import argparse, pathlib, struct
ROOT = pathlib.Path(__file__).resolve().parents[1]
OUT = ROOT / 'content/docs/hpi'

def build():
    b = bytearray(20)
    def alloc(data):
        pos = len(b); b.extend(data); return pos
    root = alloc(bytes(8)); entries = alloc(bytes(18))
    child = alloc(bytes(8)); child_entries = alloc(bytes(9))
    records = [alloc(bytes(9)), alloc(bytes(9))]
    names = [alloc(x) for x in (b'maps\0', b'readme.txt\0', b'island.ota\0')]
    end = len(b)
    payloads = [b'Original Nanolathe documentation fixture.\n', b'[GlobalHeader]\n{\n missionname=Illustrated Island;\n SchemaCount=0;\n}\n']
    offsets = [alloc(p) for p in payloads]
    struct.pack_into('<4s4I', b, 0, b'HAPI', 0x10000, end, 0, root)
    struct.pack_into('<2I', b, root, 2, entries)
    struct.pack_into('<IIB', b, entries, names[0], child, 1)
    struct.pack_into('<IIB', b, entries+9, names[1], records[0], 0)
    struct.pack_into('<2I', b, child, 1, child_entries)
    struct.pack_into('<IIB', b, child_entries, names[2], records[1], 0)
    for rec, pos, p in zip(records, offsets, payloads): struct.pack_into('<IIB', b, rec, pos, len(p), 0)
    payload_end = len(b)
    b.extend(b'Copyright 2026 Cavedog Entertainment')
    assert len(b[payload_end:]) == 36
    encrypted = bytearray(b)
    struct.pack_into('<I', encrypted, 12, 0xbf)
    for pos in range(20, payload_end): encrypted[pos] = (~(b[pos] ^ (pos & 255) ^ 1)) & 255
    for pos in range(20, payload_end): assert ((pos & 255) ^ 1 ^ (~encrypted[pos] & 255)) == b[pos]
    # Independently follow the root -> maps -> island.ota path and verify payload.
    count, ptr = struct.unpack_from('<II', b, root)
    assert count == 2
    _, node, flag = struct.unpack_from('<IIB', b, ptr)
    assert flag == 1
    n, ptr = struct.unpack_from('<II', b, node)
    name, rec, flag = struct.unpack_from('<IIB', b, ptr)
    pos, length, method = struct.unpack_from('<IIB', b, rec)
    assert n == 1 and flag == method == 0 and bytes(b[name:name+11]) == b'island.ota\0'
    assert bytes(b[pos:pos+length]) == payloads[1]
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="840" height="390" viewBox="0 0 840 390" role="img" aria-labelledby="title desc"><title id="title">Follow maps/island.ota through an original HPI archive</title><desc id="desc">Root at 20 points to an entry list at 28. Its maps entry points to a directory at 46, whose island.ota entry points to the file record at 72. The record points to {offsets[1]} where the {len(payloads[1])}-byte file begins.</desc><rect width="840" height="390" fill="#121918"/><g font-family="monospace" font-size="15" fill="#d7e5cc"><text x="28" y="35" fill="#addb76">DIRECTORY POINTERS · absolute byte offsets</text><g stroke="#607548" fill="#24311f"><rect x="28" y="62" width="220" height="76"/><rect x="306" y="62" width="240" height="76"/><rect x="602" y="62" width="210" height="76"/><rect x="306" y="204" width="240" height="76"/><rect x="602" y="204" width="210" height="76"/></g><g fill="#d7e5cc"><text x="43" y="89">Root @ 0x{root:02X}</text><text x="43" y="116">2 entries → 0x{entries:02X}</text><text x="321" y="89">maps · directory</text><text x="321" y="116">name 0x{names[0]:02X} → node 0x{child:02X}</text><text x="617" y="89">Directory @ 0x{child:02X}</text><text x="617" y="116">1 entry → 0x{child_entries:02X}</text><text x="321" y="231">island.ota · file</text><text x="321" y="258">record → 0x{records[1]:02X}</text><text x="617" y="231">File data @ 0x{offsets[1]:02X}</text><text x="617" y="258">{len(payloads[1])} bytes · stored</text></g><g stroke="#addb76" stroke-width="2" fill="none"><path d="M248 100h58m240 0h56m108 38v38H426v28m120 38h56"/></g><text x="28" y="329">20 plain header bytes | directory ends at 0x{end:02X}</text><text x="28" y="358" fill="#adc0b7">The other root entry, readme.txt, points to {len(payloads[0])} bytes at 0x{offsets[0]:02X}.</text></g></svg>'''
    return {'example.hpi': bytes(b), 'example-encrypted.hpi': bytes(encrypted), 'directory.svg': svg.encode()}

def main():
    p = argparse.ArgumentParser(); p.add_argument('--check', action='store_true'); args=p.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    for name, data in build().items():
        path=OUT/name
        if args.check:
            if not path.exists() or path.read_bytes()!=data: raise SystemExit(f'Out of date: {path}')
        else: path.write_bytes(data)
    print('HPI original fixtures and pointer diagram: OK')
if __name__ == '__main__': main()
