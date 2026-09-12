from PIL import Image,ImageChops,ImageDraw
from pathlib import Path
import json,sys
root=Path(sys.argv[1] if len(sys.argv)>1 else '/private/tmp/nanolathe-feature-v3-finishes-media/scout')
metadata=json.loads((root/"metadata.json").read_text())
heading_by_key={(m["model"],m["frame"]):m["heading"] for m in metadata}
rows=[]
for folder in sorted(p for p in root.iterdir() if p.is_dir()):
 stats=[]
 for on in sorted(folder.glob('on-*.png')):
  off=on.with_name(on.name.replace('on-','off-'))
  a,b=Image.open(off).convert('RGB'),Image.open(on).convert('RGB')
  d=ImageChops.difference(a,b)
  pixels=list(d.getdata()); changed=sum(max(p)>0 for p in pixels);strong=sum(max(p)>=16 for p in pixels);total=sum(sum(p) for p in pixels)
  stats.append(dict(frame=int(on.stem[-4:]),changed=changed,strong=strong,total=total,max=max(max(p) for p in pixels)))
 best=max(stats,key=lambda d:d['total']);print(folder.name,best)
 rows.append((folder,best,stats))
# Native crops, no resampling. Show strongest pair of each model.
sheet=Image.new('RGB',(640,200*len(rows)),(15,17,20));draw=ImageDraw.Draw(sheet)
for row,(folder,best,_) in enumerate(rows):
 for j,mode in enumerate(['off','on']):
  im=Image.open(folder/f'{mode}-{best["frame"]:04d}.png').crop((96,136,416,312))
  sheet.paste(im,(j*320,row*200+24))
 draw.text((8,row*200+5),f'{folder.name} heading {heading_by_key[(folder.name,best["frame"])]}  OFF / ON  strong={best["strong"]}',fill='white')
sheet.save(root/'best-models.png')
(root/'analysis.json').write_text(json.dumps({p.name:{'best':b,'headings':s} for p,b,s in rows},indent=2))
