#!/usr/bin/env python3
"""Reproduce an original two-schema OTA metadata example and its schematic map."""
import argparse,json,pathlib,re
ROOT=pathlib.Path(__file__).resolve().parents[1];OUT=ROOT/'content/docs/ota'
def build():
    schemas=[{'type':'Network 1','metal':3,'humanMetal':1000,'humanEnergy':1000,'starts':[(768,640),(3328,2432)]},{'type':'Network 2','metal':6,'humanMetal':2000,'humanEnergy':1500,'starts':[(768,2432),(3328,640)]}]
    text='// Original documentation example. No paired terrain is supplied.\n[GlobalHeader]\n{\n missionname=Illustrated Basin;\n missiondescription=Two variants on one schematic landscape.;\n size=8 x 6;\n SCHEMACOUNT=2;\n gravity=112;\n minwindspeed=100;\n maxwindspeed=2000;\n'
    for i,s in enumerate(schemas):
        text+=f' [Schema {i}]\n {{\n  Type={s["type"]};\n  SurfaceMetal={s["metal"]};\n  HumanMetal={s["humanMetal"]};\n  HumanEnergy={s["humanEnergy"]};\n  ComputerMetal={s["humanMetal"]};\n  ComputerEnergy={s["humanEnergy"]};\n  [specials]\n  {{\n'
        for j,(x,z) in enumerate(s['starts']):text+=f'   [special{j}]\n   {{\n    specialwhat=StartPos{j+1};\n    XPos={x};\n    ZPos={z};\n   }}\n'
        text+='  }\n }\n'
    text+='}\n'
    found=re.findall(r'Type=(Network \d);.*?SurfaceMetal=(\d+);.*?HumanMetal=(\d+);.*?HumanEnergy=(\d+);.*?specialwhat=StartPos1;\s+XPos=(\d+);\s+ZPos=(\d+);.*?specialwhat=StartPos2;\s+XPos=(\d+);\s+ZPos=(\d+);',text,re.S)
    assert len(found)==2
    decoded=[]
    for row in found:decoded.append({'type':row[0],'metal':int(row[1]),'humanMetal':int(row[2]),'humanEnergy':int(row[3]),'starts':[[int(row[4]),int(row[5])],[int(row[6]),int(row[7])]]})
    svg='''<svg xmlns="http://www.w3.org/2000/svg" width="640" height="480" viewBox="0 0 640 480"><title>Original schematic basin; terrain is shared by both metadata variants</title><rect width="640" height="480" fill="#2e4b52"/><path d="M0 0H640V150L560 135 490 184 421 168 337 216 265 147 161 195 97 135 0 162Z" fill="#739862"/><path d="M0 480H640V320L560 305 486 337 413 293 324 324 253 270 186 328 93 302 0 340Z" fill="#739862"/><g fill="none" stroke="#acd080" stroke-width="2" opacity=".6"><path d="M0 116L98 93 161 150 263 103 338 166 421 126 489 139 560 91 640 112"/><path d="M0 382L98 347 186 373 253 314 324 369 412 338 486 382 560 348 640 365"/></g><g fill="#496c49"><path d="M35 0L75 51 160 31 199 74 254 0Z"/><path d="M363 480L403 420 479 442 527 403 584 480Z"/></g></svg>'''
    return {'example.ota':text.encode(),'example.json':(json.dumps({'mapWidth':4096,'mapHeight':3072,'schemas':decoded},separators=(',',':'))+'\n').encode(),'basin.svg':svg.encode()}
def main():
    p=argparse.ArgumentParser();p.add_argument('--check',action='store_true');a=p.parse_args();OUT.mkdir(parents=True,exist_ok=True)
    for name,data in build().items():
        path=OUT/name
        if a.check:
            if not path.exists() or path.read_bytes()!=data:raise SystemExit(f'Out of date: {path}')
        else:path.write_bytes(data)
    print('OTA original schema fixture and schematic: OK')
if __name__=='__main__':main()
