"""Bake the one-pose presentation mesh and a padded RGBA atlas for WebGL."""
import argparse
import hashlib
import json
import math
from pathlib import Path
from PIL import Image

parser = argparse.ArgumentParser()
parser.add_argument('--input', type=Path, default=Path('/private/tmp/nanolathe-material-preview'))
parser.add_argument('--output', type=Path, default=Path('static/models/materials'))
args = parser.parse_args()
args.output.mkdir(parents=True, exist_ok=True)
source = json.loads((args.input / 'mesh.json').read_text())
# One row of texture tiles, clamped and sampled at pixel centers to avoid seams.
width = sum(t['width'] + 4 for t in source['textures'])
height = max(t['height'] + 4 for t in source['textures'])
atlas = Image.new('RGBA', (width, height))
x = 0
for t in source['textures']:
    tile = Image.open(args.input / t['file']).convert('RGBA')
    t['x'], t['y'] = x + 2, 2
    for dy in range(-2, t['height'] + 2):
        for dx in range(-2, t['width'] + 2):
            atlas.putpixel((x + 2 + dx, 2 + dy), tile.getpixel((max(0, min(dx, tile.width-1)), max(0, min(dy, tile.height-1)))))
    x += t['width'] + 4
vertices = []
positions = [p for face in source['faces'] for p in face['positions']]
lo = [min(p[i] for p in positions) for i in range(3)]
hi = [max(p[i] for p in positions) for i in range(3)]
center = [(a+b)/2 for a,b in zip(lo,hi)]
radius = max(math.dist(p,center) for p in positions)
for face in source['faces']:
    t = source['textures'][face['texture']]
    uv = [(0,0),(t['width']-1,0),(t['width']-1,t['height']-1),(0,t['height']-1)]
    # Mirroring model Z into world Z flips winding. Reverse the triangle fan.
    for j in range(1,len(face['positions'])-1):
        for k in [0,j+1,j]:
            u,v = uv[k] if len(face['positions'])==4 else (0,0)
            values = face['positions'][k] + face['normal'] + [(t['x']+u+.5)/width,(t['y']+v+.5)/height,face['material']]
            vertices.extend(round(v,6) for v in values)
model = {'version':1,'unit':'ARM mobile Annihilator','revision':'801c8b2','center':center,'floor':lo[1],'radius':radius,'vertices':vertices}
(args.output/'annihilator.json').write_text(json.dumps(model,separators=(',',':'))+'\n')
atlas.save(args.output/'annihilator.png',optimize=True)
manifest = {'revision':'801c8b28c38ff6505b4939d96cce7fcf22200da5','faces':len(source['faces']),'triangles':len(vertices)//27,'material_faces':{str(i):sum(f['material']==i for f in source['faces']) for i in range(3)},'atlas_size':[width,height],'source_sha256':hashlib.sha256((args.input/'mesh.json').read_bytes()).hexdigest(),'files':[]}
for p in sorted(args.output.iterdir()):
    manifest['files'].append({'path':str(p),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
Path('scripts/renderer-capture/live-materials/manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
print(json.dumps({k:v for k,v in manifest.items() if k!='files'}))
