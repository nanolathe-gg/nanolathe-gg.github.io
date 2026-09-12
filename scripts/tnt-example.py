#!/usr/bin/env python3
"""Generate a small original TNT, decoded layer diagrams, and inspection data."""
import argparse,json,pathlib,struct,math
ROOT=pathlib.Path(__file__).resolve().parents[1]; OUT=ROOT/'content/docs/tnt'
W,H=32,24
PALETTE=['#27424e','#345d68','#517d70','#749b64','#9fba73','#c4cb93','#dfd6af','#718969']
def build():
    heights=[max(8,min(120,round(20+85*math.exp(-((x-20)**2/130+(y-9)**2/70))))) for y in range(H) for x in range(W)]
    tilemap=[]
    for y in range(H//2):
        for x in range(W//2):
            h=heights[(y*2)*W+x*2];tilemap.append(0 if h<35 else 1 if h<55 else 2 if h<80 else 3)
    tiles=[]
    for t in range(4):
        tiles.append(bytes(t*2+int((x*7+y*11+x*y)%19<5) for y in range(32) for x in range(32)))
    refs=[65535]*(W*H);refs[10*W+20]=0
    for x,y in [(21,10),(20,11),(21,11),(6,5)]:refs[y*W+x]=65534
    refs[8*W+18]=65532
    attrs=b''.join(struct.pack('<BHB',h,r,0) for h,r in zip(heights,refs))
    b=bytearray(64)
    def put(data):p=len(b);b.extend(data);return p
    im=put(struct.pack('<'+'H'*len(tilemap),*tilemap));at=put(attrs);gfx=put(b''.join(tiles));feat=put(struct.pack('<I128s',0,b'ExampleBeacon'))
    # Synthetic preview is a stored 64x64 image, with a top-left used rectangle.
    mw=mh=64;usedh=(H*16-128)*mh//(W*16-32)
    mini=[]
    for y in range(mh):
        for x in range(mw):
            if y>=usedh:mini.append(0);continue
            px=x*W*16//mw;py=y*H*16//usedh;t=tilemap[(py//32)*(W//2)+px//32];mini.append(tiles[t][(py%32)*32+px%32])
    mm=put(struct.pack('<II',mw,mh)+bytes(mini));struct.pack_into('<16I',b,0,0x2000,W,H,im,at,gfx,4,1,feat,35,mm,1,0,0,0,0)
    # Decode the canonical sections to drive both browser state and the pictures.
    header=struct.unpack_from('<16I',b);assert header[3]+W*H//2==header[4]
    decoded=[struct.unpack_from('<BHB',b,at+i*4) for i in range(W*H)]
    assert [r[0] for r in decoded]==heights and [r[1] for r in decoded]==refs
    assert mm+8+mw*mh==len(b)
    def svg_start(title):return f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="512" height="384" viewBox="0 0 512 384" role="img"><title>{title}</title>'
    art=svg_start('Original TNT terrain art: repeated tiles form a stylized island')+'<defs>'
    for t,tile in enumerate(tiles):
        art+=f'<g id="tile{t}">'
        for y in range(32):
            for x in range(32):art+=f'<rect x="{x}" y="{y}" width="1" height="1" fill="{PALETTE[tile[y*32+x]]}"/>'
        art+='</g>'
    art+='</defs>'
    for i,t in enumerate(tilemap):art+=f'<use xlink:href="#tile{t}" x="{i%(W//2)*32}" y="{i//(W//2)*32}"/>'
    art+='</svg>'
    height_svg=svg_start('Original TNT corner heights shown as a color grid, brighter means higher')
    feature_svg=svg_start('Original source feature words: one live anchor, four fringe words and one void')+'<rect width="512" height="384" fill="#1d2927"/>'
    for i,(h,r,_) in enumerate(decoded):
        x,y=i%W*16,i//W*16;c=round(25+h*1.8);height_svg+=f'<rect x="{x}" y="{y}" width="16" height="16" fill="rgb({round(c*.8)},{c},{round(c*.66)})"/>'
        if r!=65535:
            color={0:'#d4ef8c',65534:'#bd9360',65532:'#111415'}[r];feature_svg+=f'<rect x="{x}" y="{y}" width="16" height="16" fill="{color}" stroke="#eee" stroke-width="1"/>'
    height_svg+='</svg>';feature_svg+='</svg>'
    data={'width':W,'height':H,'seaLevel':35,'heights':heights,'features':refs,'tiles':tilemap,'sectionOffsets':{'tileMap':im,'attributes':at,'graphics':gfx,'features':feat,'minimap':mm}}
    return {'example.tnt':bytes(b),'example.json':(json.dumps(data,separators=(',',':'))+'\n').encode(),'terrain.svg':art.encode(),'heights.svg':height_svg.encode(),'features.svg':feature_svg.encode()}
def main():
    p=argparse.ArgumentParser();p.add_argument('--check',action='store_true');args=p.parse_args();OUT.mkdir(parents=True,exist_ok=True)
    for name,data in build().items():
        path=OUT/name
        if args.check:
            if not path.exists() or path.read_bytes()!=data:raise SystemExit(f'Out of date: {path}')
        else:path.write_bytes(data)
    print('TNT original fixture and decoded layer diagrams: OK')
if __name__=='__main__':main()
