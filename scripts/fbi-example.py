#!/usr/bin/env python3
"""Original FBI schema fixture and case-sensitive yard decoding manifest."""
import argparse,json,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]/'content/docs/fbi'
CELL={'.':0x00,'c':0x2d,'C':0x35,'f':0x6f,'G':0x8f,'o':0x2f,'O':0x2b,'w':0x37,'Y':0x31,'y':0x29}
SOURCE='''// Original schema illustration, not an installable retail unit pack.
[UNITINFO] {
    UnitName=EX_RELAY;
    Version=1;
    Name=Relay workshop;
    Description=An authored documentation example;
    Objectname=ex_relay;
    Corpse=ex_relay_dead;
    SoundCategory=EX_UTILITY;
    Weapon1=EX_PULSE;
    BMcode=0;
    Builder=1;
    CanMove=1;
    MaxVelocity=0;
    FootprintX=4;
    FootprintZ=4;
    YardMap=oooo o..o occo oYYo;
    BuildCostMetal=120;
    BuildCostEnergy=900;
    BuildTime=1800;
    WorkerTime=100;
}
'''
def decode(text,count):
    # This fixture deliberately covers only bounded sources ending in a known character.
    assert text and text[-1] in CELL
    cells=[];pos=0
    while len(cells)<count:
        char=text[pos]
        if char not in CELL:pos+=1;continue
        repeated=pos==len(text)-1 and any(c['sourceIndex']==pos for c in cells)
        cells.append({'character':char,'byte':f'0x{CELL[char]:02X}','sourceIndex':pos,'repeated':repeated})
        if pos<len(text)-1:pos+=1
    return cells

def outputs():
    fields=dict((k.strip(),v.strip()) for k,v in re.findall(r'^\s*(\w+)=([^;]*);',SOURCE,re.M))
    presets=[]
    for label,value in [('Authored 4 × 4 pattern',fields['YardMap']),('Same cells, no spaces',fields['YardMap'].replace(' ','')),('One final o repeats','o'),('Lowercase g is skipped','o g o . . c Y')]:
        presets.append({'label':label,'source':value,'cells':decode(value,16)})
    assert [c['byte'] for c in presets[0]['cells']]==[c['byte'] for c in presets[1]['cells']]
    assert sum(c['repeated'] for c in presets[2]['cells'])==15
    return {'example.fbi':SOURCE.encode(),'example.json':(json.dumps({'provenance':'Original schema illustration. Referenced resources do not ship with this fixture. Yard presets use established successful-source behavior, not an unsafe malformed-source emulation.','fields':fields,'presets':presets},indent=2)+'\n').encode()}
def main():
    p=argparse.ArgumentParser();p.add_argument('--check',action='store_true');a=p.parse_args()
    for name,data in outputs().items():
        target=ROOT/name
        if a.check:assert target.read_bytes()==data,f'Stale fixture: {target}'
        else:target.write_bytes(data)
    print('FBI fixture and decoded yard maps verified.')
if __name__=='__main__':main()
