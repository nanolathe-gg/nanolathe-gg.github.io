"""Author an original 3DO teaching fixture; decode it to JSON and SVG.

Standard library only. --check compares committed assets without writing.
The projection is a teaching illustration, not the retail rasterizer.
"""
import html
import json
import math
from pathlib import Path
import struct
import sys

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'content/docs/3do'
COLORS = {20:'#64705d',21:'#7e8d70',22:'#3c4841',23:'#a8b695',24:'#b6ef63',25:'#e7b66f',26:'#a88652',27:'#354038'}

def box(vertices, faces, lo, hi, color):
    x,y,z=lo; X,Y,Z=hi; n=len(vertices)
    vertices.extend([(x,y,z),(X,y,z),(X,Y,z),(x,Y,z),(x,y,Z),(X,y,Z),(X,Y,Z),(x,Y,Z)])
    for indexes in ([0,3,2,1],[4,5,6,7],[0,4,7,3],[1,2,6,5],[3,7,6,2],[0,1,5,4]):
        faces.append(dict(indexes=[n+i for i in indexes], color=color))

def piece(name,translation,parent):
    return dict(name=name,translation=translation,parent=parent,vertices=[],faces=[],selection=-1)

pieces=[piece('base',[0,0,0],None),piece('turret',[0,8,0],0),piece('barrel',[0,3,-5],1),piece('flare',[0,0,-15],2),piece('mast',[-8,8,8],0)]
p=pieces[0]
p['vertices']=[(-17,0,-22),(17,0,-22),(17,0,22),(-17,0,22)]
p['faces']=[dict(indexes=[0,1,2,3],color=24)];p['selection']=0
box(p['vertices'],p['faces'],(-11,2,-15),(11,8,16),20)
box(p['vertices'],p['faces'],(-16,1,-18),(-11,6,18),22)
box(p['vertices'],p['faces'],(11,1,-18),(16,6,18),22)
box(p['vertices'],p['faces'],(-8,8,6),(8,9,13),21)
box(pieces[1]['vertices'],pieces[1]['faces'],(-7,0,-6),(7,6,6),25)
box(pieces[1]['vertices'],pieces[1]['faces'],(-4,6,-3),(4,8,3),26)
box(pieces[2]['vertices'],pieces[2]['faces'],(-2,-1.5,-14),(2,1.5,0),21)
box(pieces[2]['vertices'],pieces[2]['faces'],(-2.8,-2,-15),(2.8,2,-12),24)
pieces[3]['vertices']=[(0,0,0)]
box(pieces[4]['vertices'],pieces[4]['faces'],(-.6,0,-.6),(.6,12,.6),23)
box(pieces[4]['vertices'],pieces[4]['faces'],(-2,10,-1),(2,13,1),24)

blob=bytearray(52*len(pieces))
def append(data):
    offset=len(blob);blob.extend(data);return offset
for i,p in enumerate(pieces):
    name=append(p['name'].encode()+b'\0')
    verts=append(b''.join(struct.pack('<iii',*(round(v*65536) for v in xyz)) for xyz in p['vertices']))
    primitives=append(bytes(32*len(p['faces'])))
    for j,face in enumerate(p['faces']):
        indexes=append(struct.pack('<'+'H'*len(face['indexes']),*face['indexes']))
        struct.pack_into('<IiIiiiii',blob,primitives+j*32,face['color'],len(face['indexes']),0,indexes,0,0,0,1)
    siblings=[j for j,q in enumerate(pieces) if q['parent']==p['parent']]
    after=siblings.index(i)+1
    sibling=siblings[after]*52 if after<len(siblings) else 0
    children=[j for j,q in enumerate(pieces) if q['parent']==i]
    child=children[0]*52 if children else 0
    struct.pack_into('<13i',blob,i*52,1,len(p['vertices']),len(p['faces']),p['selection'],*(round(v*65536) for v in p['translation']),name,0,verts,primitives,sibling,child)

# Independent pointer reader: follows the binary graph and index arrays.
def decode(data):
    result=[];seen=set()
    def span(offset,size):
        assert 0<=offset<=len(data) and 0<=size<=len(data)-offset
    def string(offset):
        span(offset,1);end=data.index(0,offset);return bytes(data[offset:end]).decode('ascii')
    def chain(offset,parent):
        while True:
            assert offset not in seen;seen.add(offset);span(offset,52)
            version,nv,nf,selection,x,y,z,name,aux,vertices,faces,sibling,child=struct.unpack_from('<13i',data,offset)
            assert version==1 and nv>=0 and nf>=0 and (selection==-1 or 0<=selection<nf)
            assert aux==0;span(vertices,nv*12);span(faces,nf*32)
            verts=[list(v/65536 for v in struct.unpack_from('<iii',data,vertices+j*12)) for j in range(nv)]
            primitives=[]
            for j in range(nf):
                color,count,aux,indices,texture,u1,u2,colored=struct.unpack_from('<IiIiiiii',data,faces+j*32)
                assert count>=2 and aux==0;span(indices,count*2)
                idx=list(struct.unpack_from('<'+'H'*count,data,indices));assert all(k<nv for k in idx)
                primitives.append(dict(offset=faces+j*32,indexOffset=indices,indexes=idx,color=color,texture=string(texture) if texture else None,isColored=colored))
            index=len(result)
            result.append(dict(name=string(name),offset=offset,parent=parent,translation=[v/65536 for v in (x,y,z)],selection=selection,nameOffset=name,vertexOffset=vertices,primitiveOffset=faces,siblingOffset=sibling,childOffset=child,vertices=verts,faces=primitives))
            if child:chain(child,index)
            if not sibling:break
            offset=sibling
    chain(0,None)
    return result

model=decode(blob)
assert len(model)==len(pieces)
for authored,decoded in zip(pieces,model):
    assert authored['name']==decoded['name'] and authored['translation']==decoded['translation']
    assert [[round(c*65536)/65536 for c in v] for v in authored['vertices']]==decoded['vertices']
    assert [f['indexes'] for f in authored['faces']]==[f['indexes'] for f in decoded['faces']]

def origin(i,explode=False):
    p=model[i];t=p['translation'][:]
    if explode and p['parent'] is not None:t[1]+=9
    if p['parent'] is not None:t=[a+b for a,b in zip(t,origin(p['parent'],explode))]
    return t

def project(v):
    x,y,z=v;a=math.radians(-38);e=math.radians(28)
    u=x*math.cos(a)+z*math.sin(a);depth=-x*math.sin(a)+z*math.cos(a)
    return (360+u*7,310-(y*math.cos(e)+depth*math.sin(e))*7,depth*math.cos(e)-y*math.sin(e))

def render(explode=False):
    parts=['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 720 460" width="720" height="460"><rect width="720" height="460" fill="#151c1b"/>']
    def line(a,b,color='#2b3831',dash=''):
        x,y,_=project(a);X,Y,_=project(b)
        return f'<path d="M{x:.2f},{y:.2f}L{X:.2f},{Y:.2f}" fill="none" stroke="{color}" {dash}/>'
    for n in range(-30,31,5):
        parts.append(line([n,0,-30],[n,0,30]));parts.append(line([-30,0,n],[30,0,n]))
    polygons=[]
    for i,p in enumerate(model):
        o=origin(i,explode)
        for fi,f in enumerate(p['faces']):
            if fi==p['selection']:continue
            pts=[project([a+b for a,b in zip(p['vertices'][j],o)]) for j in f['indexes']]
            # This teaching projection uses depth ordering, never retail's compiled ordering.
            polygons.append((sum(v[2] for v in pts)/len(pts),f,pts))
    for _,f,pts in sorted(polygons,key=lambda face:face[0],reverse=True):
        xy=' '.join(f'{p[0]:.2f},{p[1]:.2f}' for p in pts)
        parts.append(f'<polygon points="{xy}" fill="{COLORS[f["color"]]}" stroke="#101712" stroke-width="1.1"/>')
    for i,p in enumerate(model):
        o=origin(i,explode);x,y,_=project(o)
        if explode and p['parent'] is not None:parts.append(line(origin(p['parent'],explode),o,'#c4d8ab','stroke-dasharray="4 4"'))
        if explode or p['name']=='flare':
            parts.append(f'<circle cx="{x:.2f}" cy="{y:.2f}" r="4" fill="#edf0e7"/><text x="{x+9:.2f}" y="{y-10:.2f}" fill="#edf0e7" font-size="13" font-family="monospace">{html.escape(p["name"])}</text>')
    parts.append('</svg>');return ''.join(parts).encode()

assets={'example.3do':bytes(blob),'model.json':(json.dumps(dict(byteLength=len(blob),palette=COLORS,pieces=model),indent=2)+'\n').encode(),'model.svg':render(),'exploded.svg':render(True)}
# Asymmetric texture: visible corner letters make implied mapping easy to inspect.
assets['texture.svg']=b'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 160 160" width="160" height="160"><path fill="#b6ef63" d="M0 0h80v80H0z"/><path fill="#e7b66f" d="M80 0h80v80H80z"/><path fill="#709ea3" d="M80 80h80v80H80z"/><path fill="#69785d" d="M0 80h80v80H0z"/><path d="M50 100V65H35l45-40 45 40h-15v35z" fill="#121516"/><g font-family="monospace" font-size="22" fill="#121516"><text x="10" y="27">A</text><text x="133" y="27">B</text><text x="133" y="151">C</text><text x="10" y="151" fill="#fff">D</text></g></svg>'''
for name,data in assets.items():
    path=OUT/name
    if '--check' in sys.argv:assert path.read_bytes()==data,f'Stale asset: {path}'
    else:path.write_bytes(data)
print(f'{"Verified" if "--check" in sys.argv else "Generated"} {len(assets)} assets: {len(blob)} bytes, {len(model)} pieces, {sum(len(p["vertices"]) for p in model)} vertices, {sum(len(p["faces"]) for p in model)} primitives.')
print('Root words:', ' '.join(f'{v & 0xffffffff:08X}' for v in struct.unpack_from('<13i',blob)))
