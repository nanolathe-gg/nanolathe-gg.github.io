#!/usr/bin/env python3
"""Original Smartpak fragments; deliberately not a complete recording or replay."""
import argparse,json,pathlib,struct
ROOT=pathlib.Path(__file__).resolve().parents[1];OUT=ROOT/'content/docs/tad'
def build():
    bits=[]
    def write(v,n):bits.extend((v>>i)&1 for i in range(n))
    # Authored context: C=283 => W=9; definition 1 is ground; maxUnits=500.
    write(0,16);write(1,9);write(0,1);write(1,2);write(120,16);write(80,16)
    write(65535,16);write(1,1);write(0,9)
    body=bytes(sum(bits[j+i]<<i for i in range(min(8,len(bits)-j))) for j in range(0,len(bits),8))
    packet=struct.pack('<BHI',0x2c,len(body)+7,600)+body
    idle=struct.pack('<BHI',0x2c,11,601)+bytes.fromhex('ffff0100')
    stored=b'\xfe'+struct.pack('<I',600)+b'\xfd'+struct.pack('<H',len(packet))+body+b'\xff'
    framed=struct.pack('<HHBB',len(stored)+6,33,1,3)+stored
    # Independently decode the stored token framing and bit-packed source values.
    cursor=0;tick=None;out=[]
    while cursor<len(stored):
        op=stored[cursor]
        if op==254:tick=struct.unpack_from('<I',stored,cursor+1)[0];cursor+=5
        elif op==253:
            n=struct.unpack_from('<H',stored,cursor+1)[0];part=stored[cursor+3:cursor+n-4];out.append(struct.pack('<BHI',44,n,tick)+part);cursor+=n-4;tick+=1
        elif op==255:out.append(struct.pack('<BHI',44,11,tick)+bytes.fromhex('ffff0100'));cursor+=1;tick+=1
        else:raise AssertionError(op)
    assert out==[packet,idle] and cursor==len(stored) and len(framed)==struct.unpack_from('<H',framed)[0]
    cursor=0
    def read(n):
        nonlocal cursor
        v=sum(((body[(cursor+i)//8]>>((cursor+i)%8))&1)<<i for i in range(n));cursor+=n;return v
    assert [read(n) for n in (16,9,1,2,16,16,16,1,9)]==[0,1,0,1,120,80,65535,1,0]
    data={'stored':stored.hex(' ').upper(),'framed':framed.hex(' ').upper(),'packet':packet.hex(' ').upper(),'idle':idle.hex(' ').upper(),'body':body.hex(' ').upper(),'steps':[{'name':'FE · set counter','bytes':stored[:5].hex(' ').upper(),'output':'No packet emitted. The next sync receives tick 600.','counter':600},{'name':'FD · restore tick','bytes':stored[5:-1].hex(' ').upper(),'output':packet.hex(' ').upper(),'counter':601},{'name':'FF · expand idle','bytes':'FF','output':idle.hex(' ').upper(),'counter':602}]}
    svg='''<svg xmlns="http://www.w3.org/2000/svg" width="840" height="410" viewBox="0 0 840 410"><title>Smartpak removes repeated tick words and compresses an idle update</title><rect width="840" height="410" fill="#121918"/><g font-family="monospace" fill="#d7e5cc"><text x="28" y="36" font-size="16" fill="#addb76">STORED SMARTPAK · 20 BYTES</text><g stroke="#65784f"><rect x="28" y="57" width="214" height="83" fill="#3c4326"/><rect x="256" y="57" width="385" height="83" fill="#273b32"/><rect x="655" y="57" width="155" height="83" fill="#473b28"/></g><g font-size="17"><text x="43" y="88">FE 58 02 00 00</text><text x="43" y="116" font-size="13">set counter = 600</text><text x="271" y="88">FD 12 00 + body</text><text x="271" y="116" font-size="13">14 stored bytes; original length 18</text><text x="670" y="88">FF</text><text x="670" y="116" font-size="13">1 byte idle</text></g><path d="M448 149v44m285-44v44" stroke="#addb76" stroke-width="2"/><text x="28" y="221" font-size="16" fill="#addb76">RECONSTRUCTED UNIT SYNC · 29 BYTES</text><g stroke="#65784f"><rect x="28" y="243" width="460" height="94" fill="#273b32"/><rect x="505" y="243" width="305" height="94" fill="#473b28"/></g><text x="43" y="273" font-size="16">2C · length 18 · tick 600</text><text x="43" y="305" font-size="13">ground entry + empty scheduled slot</text><text x="520" y="273" font-size="16">2C · length 11 · tick 601</text><text x="520" y="305" font-size="13">idle body FF FF 01 00</text><text x="28" y="378" font-size="13">Original teaching context: C=283, W=9. No private recording bytes.</text></g></svg>'''
    return {'smartpak.bin':stored,'match-record.bin':framed,'reconstructed.bin':packet+idle,'example.json':(json.dumps(data,separators=(',',':'))+'\n').encode(),'smartpak.svg':svg.encode()}
def main():
    p=argparse.ArgumentParser();p.add_argument('--check',action='store_true');a=p.parse_args();OUT.mkdir(parents=True,exist_ok=True)
    for name,data in build().items():
        path=OUT/name
        if a.check:
            if not path.exists() or path.read_bytes()!=data:raise SystemExit(f'Out of date: {path}')
        else:path.write_bytes(data)
    print('TAD original Smartpak fragments and reconstruction: OK')
if __name__=='__main__':main()
