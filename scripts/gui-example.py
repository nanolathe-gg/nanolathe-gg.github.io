#!/usr/bin/env python3
"""Generate an original GUI and parse its bounded TDF subset for the diagram."""
import argparse,json,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]/'content/docs/gui'
SOURCE='''// Original documentation panel; the bracket names are deliberately unordered.
[Panel] {
  [COMMON] { id=0; name=EXAMPLE; xpos=0; ypos=0; width=640; height=400; active=1; }
  totalgadgets=4; defaultfocus=DEPLOY;
}
[GADGET72] {
  [COMMON] { id=2; name=ROSTER; xpos=36; ypos=76; width=408; height=204; assoc=7; active=1; attribs=16; }
  itemheight=40;
}
[Scroll] {
  [COMMON] { id=4; name=ROSTER_SCROLL; xpos=456; ypos=76; width=20; height=204; assoc=7; active=1; attribs=2; }
  range=164; knobpos=0; knobsize=40; thick=100;
}
[GADGET3] {
  [COMMON] { id=1; name=DEPLOY; xpos=452; ypos=320; width=152; height=44; active=1; help=Choose this authored option; }
  text=DEPLOY; status=0; grayedout=0; stages=0; quickkey=68;
}
[HelpLabel] {
  [COMMON] { id=5; name=HELPTEXT; xpos=36; ypos=326; width=392; height=28; active=1; }
  text=An original panel schematic;
}
'''
def parse(source):
    source=re.sub(r'//[^\n]*','',source)
    tokens=re.findall(r'\[[^\]]*\]|[{}]|[^{};\[\]]+;',source)
    def sections(i,inner=False):
        result=[];fields={}
        while i<len(tokens):
            token=tokens[i].strip();i+=1
            if token=='}':return result,fields,i
            if token.startswith('['):
                assert tokens[i]=='{';i+=1
                children,values,i=sections(i,True)
                result.append({'section':token[1:-1],'fields':values,'children':children})
            else:
                k,v=token[:-1].split('=',1);fields[k.strip()]=v.strip()
        assert not inner
        return result,fields,i
    nodes,_,_=sections(0)
    return [{'section':n['section'],'common':n['children'][0]['fields'],'fields':n['fields']} for n in nodes]
def outputs():
    gadgets=parse(SOURCE)
    assert len(gadgets)==5 and gadgets[1]['common']['assoc']==gadgets[2]['common']['assoc']=='7'
    assert gadgets[0]['common']['width']=='640' and gadgets[3]['fields']['grayedout']=='0'
    return {'example.gui':SOURCE.encode(),'example.json':(json.dumps({'provenance':'Original authored schematic; parser handles only this controlled fixture subset, not general retail TDF.','gadgets':gadgets},indent=2)+'\n').encode()}
def main():
    parser=argparse.ArgumentParser();parser.add_argument('--check',action='store_true');args=parser.parse_args();ROOT.mkdir(parents=True,exist_ok=True)
    for name,data in outputs().items():
        p=ROOT/name
        if args.check:assert p.read_bytes()==data,f'Stale fixture: {p}'
        else:p.write_bytes(data)
    print('GUI authored fixture and parsed records verified.')
if __name__=='__main__':main()
