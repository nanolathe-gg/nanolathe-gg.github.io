"""Render the guide's pinned engine geometry; no retail assets or third-party modules.

Run: python3 scripts/strategic-icon-examples.py --engine ../nanolathe
Requires Go and the documented engine revision. Ordinary website builds use the
checked-in PNGs and do not need Go or an engine checkout.
"""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--engine', type=Path, required=True)
parser.add_argument('--check', action='store_true')
args = parser.parse_args()
data = json.loads((ROOT / 'data/strategic-icons.json').read_text())
source = (args.engine / 'internal/client/strategic_icon_art.go').read_bytes()
if hashlib.sha256(source).hexdigest() != data['sourceSHA256']:
    raise SystemExit('Icon geometry differs from the pinned source; review before updating.')
# Keep all coverage, atlas construction, and sampling functions unchanged. Only
# replace package-local type/import names to run this file with the Go stdlib.
art = source.decode().replace('package client', 'package main', 1)
art = art.replace('\n\t"github.com/nanolathe-gg/nanolathe/internal/drawlist"', '')
art = art.replace('drawlist.MarkerAtlas', 'MarkerAtlas').replace('drawlist.Rect', 'Rect')
main = '''package main
import ("encoding/json"; "image/color"; "image/png"; "os"; "path/filepath")
type MarkerAtlas struct { Width, Height int; Pixels []byte }
type Rect struct { X, Y, W, H int32 }
type StrategicIconDescriptor struct {
 Atlas *MarkerAtlas; Rect Rect; Family, Role, Subtype string
 CommanderAppearance bool; Level int
}
type Item struct { ID string; StrategicIconDescriptor }
func main() {
 var items []Item
 b,err:=os.ReadFile(os.Args[1]); if err!=nil { panic(err) }
 if err=json.Unmarshal(b,&items); err!=nil { panic(err) }
 for _,item:=range items {
  d:=item.StrategicIconDescriptor
  atlas,rects:=makeStrategicIconAtlas([]StrategicIconDescriptor{d})
  d.Atlas=atlas; d.Rect=rects[strategicArtKey(d)]
  img:=StrategicIconPreview(d,24,color.RGBA{75,215,240,255},color.RGBA{255,240,135,255},color.RGBA{27,32,33,255},false)
  f,err:=os.Create(filepath.Join(os.Args[2],item.ID+".png")); if err!=nil { panic(err) }
  if err=png.Encode(f,img); err!=nil { panic(err) }; if err=f.Close(); err!=nil { panic(err) }
 }
}
'''
items = [item for group in data['groups'].values() for item in group]
output = ROOT / 'static/images/strategic-icons'
with tempfile.TemporaryDirectory(prefix='nanolathe-icon-docs-') as tmp:
    tmp = Path(tmp)
    (tmp / 'art.go').write_text(art)
    (tmp / 'main.go').write_text(main)
    (tmp / 'items.json').write_text(json.dumps(items))
    subprocess.run(['go', 'run', str(tmp / 'main.go'), str(tmp / 'art.go'), str(tmp / 'items.json'), str(tmp)], check=True)
    for item in items:
        name = item['id'] + '.png'
        expected = (tmp / name).read_bytes()
        if args.check:
            if not (output / name).exists() or (output / name).read_bytes() != expected:
                raise SystemExit(f'Stale icon: {name}')
        else:
            output.mkdir(parents=True, exist_ok=True)
            (output / name).write_bytes(expected)
print(f'{"Verified" if args.check else "Rendered"} {len(items)} strategic icon examples.')
