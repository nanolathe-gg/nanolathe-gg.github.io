#!/usr/bin/env python3
"""Package frozen, real engine meshes and the projected shoreline field; no archives."""
import argparse, hashlib, json, shutil
from pathlib import Path
from PIL import Image
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('input',type=Path)
p.add_argument('--output',type=Path,default=Path('static/models/water'))
a=p.parse_args();a.output.mkdir(parents=True,exist_ok=True)
scene=json.loads((a.input/'scene.json').read_text());assert scene['publication_unchanged'] and scene['terrain_model_commands']==0
models=[];audit=[]
for unit in scene['models']:
 raw=json.loads((a.input/unit['unit']/'mesh.json').read_text());tiles=raw['textures']
 width=sum(t['width']+4 for t in tiles);height=max(t['height']+4 for t in tiles)
 atlas=Image.new('RGBA',(width,height));blue=Image.new('RGBA',(width,height));x=0
 for t in tiles:
  t['x'],t['y']=x+2,2
  for prefix,target in [('',atlas),('blue-',blue)]:
   tile=Image.open(a.input/unit['unit']/(prefix+t['file'])).convert('RGBA')
   for dy in range(-2,t['height']+2):
    for dx in range(-2,t['width']+2):
     target.putpixel((x+2+dx,2+dy),tile.getpixel((max(0,min(dx,tile.width-1)),max(0,min(dy,tile.height-1)))))
  x+=t['width']+4
 vertices=[];visible=0
 for face in raw['faces']:
  ring=face['positions'];xy=[(v[0],v[2]-v[1]/2) for v in ring]
  area=sum(u[0]*v[1]-v[0]*u[1] for u,v in zip(xy,xy[1:]+xy[:1]))
  # This fixed camera admits the same clockwise projected rings as Modern.
  # Reflections use these same visible faces; never reveal a hidden backside.
  if area<=0:continue
  visible+=1;t=tiles[face['texture']];uv=[(0,0),(t['width']-1,0),(t['width']-1,t['height']-1),(0,t['height']-1)]
  for j in range(1,len(ring)-1):
   for k in [0,j,j+1]:
    u,v=uv[k] if len(ring)==4 else (0,0)
    vertices.extend(round(v,6) for v in ring[k]+[(t['x']+u+.5)/width,(t['y']+v+.5)/height])
 unit['mesh']=unit['unit']+'.json';unit['atlas']=unit['unit']+'.png';unit['blueAtlas']=unit['unit']+'-blue.png'
 (a.output/unit['mesh']).write_text(json.dumps({'vertices':vertices,'stride':5},separators=(',',':'))+'\n')
 atlas.save(a.output/unit['atlas'],optimize=True);blue.save(a.output/unit['blueAtlas'],optimize=True)
 audit.append({'unit':unit['unit'],'exported_faces':len(raw['faces']),'visible_faces':visible,'triangles':len(vertices)//15,'atlas_size':[width,height],'mesh_source_sha256':hashlib.sha256((a.input/unit['unit']/'mesh.json').read_bytes()).hexdigest()})
for name in ['terrain.png','mask.png','damp.png']:shutil.copyfile(a.input/name,a.output/name)
scene.update(terrain='terrain.png',maskTexture='mask.png',dampTexture='damp.png',version=1)
(a.output/'scene.json').write_text(json.dumps(scene,separators=(',',':'))+'\n')
files=[{'path':str(f),'bytes':f.stat().st_size,'sha256':hashlib.sha256(f.read_bytes()).hexdigest()} for f in sorted(a.output.iterdir())]
manifest={'engine_revision':scene['revision'],'export_backend':scene['backend'],'tick':scene['tick'],'publication_sha256':scene['publication_sha256'],'publication_unchanged':True,'models':audit,'files':files}
Path('scripts/renderer-capture/live-water/manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
print(json.dumps({'models':audit,'bytes':sum(f['bytes'] for f in files)}))
