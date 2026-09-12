#!/usr/bin/env python3
"""Original TDF examples and checked duplicate-key/accessor walkthrough data."""
import argparse,bisect,json,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]/'content/docs/tdf'
SOURCE='''// Original example: three spellings, one lookup result.
[Example]
{
    Power=3;
    power=7;
    Power=9;
    [Nested] { label=An authored child section; }
}
'''
def outputs():
    entries=[];states=[]
    for key,value in re.findall(r'^\s*(Power|power)=(\d+);',SOURCE,re.M):
        i=bisect.bisect_left([k.lower() for k,v in entries],key.lower())
        action='replace in place' if i<len(entries) and entries[i][0]==key else 'insert at lower bound'
        if action.startswith('replace'):entries[i]=(key,value)
        else:entries.insert(i,(key,value))
        states.append({'assignment':f'{key}={value};','action':action,'entries':[{'key':k,'value':v} for k,v in entries],'lookup':entries[0][1]})
    assert states[-1]['entries']==[{'key':'Power','value':'9'},{'key':'power','value':'7'},{'key':'Power','value':'3'}]
    cases=[]
    for label,value in [('Absent',None),('Explicit zero','0'),('Explicit empty',''),('Unparsable','junk'),('Decimal prefix','12tail'),('Even flag','2')]:
        m=re.match(r'\s*([+-]?\d+)',value or '')
        integer=7 if value is None else (int(m[1]) if m else 0)
        cases.append({'label':label,'value':value,'integer':integer,'lowBit':integer&1})
    return {'example.tdf':SOURCE.encode(),'example.json':(json.dumps({'provenance':'Original examples of established insertion and ordinary integer-accessor rules; not a complete retail parser.','states':states,'cases':cases},indent=2)+'\n').encode()}
def main():
    p=argparse.ArgumentParser();p.add_argument('--check',action='store_true');a=p.parse_args()
    for name,data in outputs().items():
        target=ROOT/name
        if a.check:assert target.read_bytes()==data,f'Stale fixture: {target}'
        else:target.write_bytes(data)
    print('TDF authored examples and reference states verified.')
if __name__=='__main__':main()
