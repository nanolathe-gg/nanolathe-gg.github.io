#!/usr/bin/env python3
"""Original COB fixture and independently decoded manifest; no retail inputs."""
import argparse, json, struct
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]/'content/docs/cob'
WORDS=[0x10021001,16384,0x1000C000,1,1,0x10021001,0,0x10065000]
BOS='piece base, turret;\n\nCreate()\n{\n    turn turret to y-axis <90> now;\n    return (0);\n}\n'
def laboratory():
    """Bounded, authored scheduler traces from pinned research §4.2/§4.6.

    No general interpreter or compiler is implied. Only the stated initial
    conditions, positive quarter-turn and normal delta=1 drain are modeled.
    """
    motions={}
    for mode,speed in [('90',16384),('180',32768)]:
        for wait in (False,True):
            angle=0; busy=0; done=False
            states=[dict(tick=0,phase='Before the first drain',angle=0,busy=0,done=False,line=0,
                         action='The turret starts at 0°. The script has not issued its turn yet.')]
            for tick in range(34):
                if tick==0:
                    busy=speed//30
                    done=not wait
                    action=f'turn stores target 16384 and step {busy} raw units/tick. The piece has not moved yet.'
                    action+=(' The following show runs now; the script returns.' if done else
                             ' wait-for-turn sees a nonzero speed word and blocks this thread.')
                elif not done and busy==0:
                    done=True
                    action='The next drain sees speed 0. The waiting thread resumes, shows the beacon and returns.'
                else:
                    action=('The script has already returned. Piece motion is independent of its thread.' if done else
                            'The early wait guard still sees a nonzero speed word. This thread remains blocked.')
                states.append(dict(tick=tick,phase='1 / Script drain',angle=angle,busy=busy,done=done,
                                   line=3 if done else 2,action=action))
                if busy:
                    angle=min(16384,angle+busy)
                    if angle==16384: busy=0
                    action=('The piece reaches 90° and clears the speed word. There is no second script scan in this drain.' if not busy else
                            'The piece advances after every script slot has been visited. The waiting thread does not run here.')
                else:
                    action='No positional turn remains to interpolate.'
                states.append(dict(tick=tick,phase='2 / Piece interpolation',angle=angle,busy=busy,done=done,
                                   line=3 if done else 2,action=action))
                if done and busy==0: break
            motions[f'{mode}-{int(wait)}']=states
    # Boundary evidence: 90°/s truncates to 546. After 30 passes it is still
    # short; pass 31 snaps and only the following script drain can wake.
    slow=motions['90-1']
    assert next(s for s in slow if s['tick']==29 and s['phase'].startswith('2'))['angle']==16380
    arrival=next(s for s in slow if s['tick']==30 and s['phase'].startswith('2'))
    assert arrival['angle']==16384 and arrival['busy']==0 and not arrival['done']
    assert next(s for s in slow if s['tick']==31)['done']
    assert motions['90-0'][1]['done'] and motions['90-0'][1]['angle']==0
    faster=next(s for s in motions['180-1'] if s['tick']==15 and s['phase'].startswith('2'))
    assert faster['angle']==16384 and not faster['done']
    threads={}
    for call in (False,True):
        for full in (False,True):
            name='call-script' if call else 'start-script'
            background=['Occupied']*7 if full else ['Free']*7
            def state(phase,slots,action,parent=False,child=False,stack='[42]',line=0):
                return dict(phase=phase,slots=slots,action=action,parent=parent,child=child,stack=stack,line=line)
            rows=[state('Before tick 0', ['Ready']+background,
                        'Parent occupies slot 0. Its argument 42 is ready on the stack. '+
                        ('The other seven slots are occupied by unrelated blocked threads.' if full else 'Slots 1–7 are free.'))]
            if full:
                rows.append(state('Tick 0 / slot 0 / start attempt',
                                  ['Blocked: −1' if call else 'Running']+background,
                                  f'{name} cannot allocate. Argument 42 stays on the parent stack. '+
                                  ('The caller blocks on slot −1; no child exists to release it.' if call else 'The parent continues after the failed start.'),line=1))
                rows.append(state('Tick 0 / end of slot 0', ['Blocked: −1' if call else 'Free']+background,
                                  'No child ran. '+('The parent remains blocked; matching signal termination can release it.' if call else
                                  'The parent sets parentDone, then returns. With no completion receiver, neither its return value nor the retained argument is popped; the slot is released.'),
                                  parent=not call,stack='[42]' if call else 'slot released',line=1 if call else 2))
            else:
                rows.append(state('Tick 0 / slot 0 / start attempt',
                                  ['Waiting: 1' if call else 'Running','Ready']+['Free']*6,
                                  'The first free slot is 1. It receives argument 42 and inherits mask 1. '+
                                  ('Parent waits for slot 1.' if call else 'Parent can continue in its current slot visit.'),stack='[empty]',line=1))
                rows.append(state('Tick 0 / end of slot 0',
                                  ['Waiting: 1' if call else 'Free','Ready']+['Free']*6,
                                  'Worker has not had its slot visit yet. '+('Parent is blocked.' if call else 'Parent sets parentDone and returns before Worker runs.'),
                                  parent=not call,stack='[empty]' if call else 'slot released',line=1 if call else 2))
                rows.append(state('Tick 0 / slot 1', ['Running' if call else 'Free']+['Free']*7,
                                  'Worker reads local argument 42, sets childDone, and returns 7. Its slot is released. '+
                                  ('Parent wakes, but slot 0 has already been visited. No completion receiver consumes or pops the returned 7.' if call else 'The child finishes independently; no completion receiver consumes or pops the returned 7.'),
                                  parent=not call,child=True,stack='[empty]' if call else 'slot released',line=3))
                if call:
                    rows.append(state('Tick 1 / slot 0', ['Free']*8,
                                      'The next drain visits the now-runnable parent. It sets parentDone and returns. call-script supplied no expression result.',
                                      parent=True,child=True,stack='slot released',line=2))
            threads[f'{int(call)}-{int(full)}']=rows
    assert threads['0-0'][2]['parent'] and not threads['0-0'][2]['child']
    assert threads['1-0'][3]['child'] and not threads['1-0'][3]['parent']
    assert threads['1-0'][4]['parent']
    assert threads['1-1'][-1]['slots'][0]=='Blocked: −1'
    return dict(motion=motions,threads=threads)

def generate():
    code=struct.pack('<8I',*WORDS)
    # Tables occupy 0x4c..0x5b; all names are independently addressed.
    names=b'Create\0base\0turret\0'
    blob=struct.pack('<11I',4,1,2,8,0,0,76,80,84,44,92)+code+struct.pack('<4I',0,92,99,104)+names
    h=struct.unpack_from('<11I',blob)
    codewords=struct.unpack_from('<%dI'%h[3],blob,h[9])
    def name_at(p): return blob[p:blob.index(0,p)].decode('ascii')
    def names_at(p,n): return [name_at(struct.unpack_from('<I',blob,p+i*4)[0]) for i in range(n)]
    assert h[0]==4 and h[3]==8 and codewords[0]==0x10021001
    assert names_at(h[7],h[1])==['Create'] and names_at(h[8],h[2])==['base','turret']
    stack=[]; states=[{'word':0,'stack':[],'angle':0,'action':'Ready: Create starts at code word 0.'}]; pc=0; angle=0
    while pc<len(codewords):
        start=pc; op=codewords[pc]; pc+=1
        if op==0x10021001:
            value=struct.unpack('<i',struct.pack('<I',codewords[pc]))[0];pc+=1;stack.append(value);action=f'Push {value} onto the stack.'
        elif op==0x1000C000:
            piece,axis=codewords[pc:pc+2];pc+=2; angle=stack.pop();assert(piece,axis)==(1,1);action='Pop target 16384. Turn piece 1 (turret), axis 1 (Y), immediately to 90°.'
        elif op==0x10065000:
            # Create has no completion receiver: retail frees the slot without a pop [04 §4.2].
            action='Return without a completion receiver. No value is popped; the slot is released.'
        else:raise AssertionError(hex(op))
        states.append({'word':start,'nextWord':pc,'stack':stack.copy(),'angle':angle,'action':action})
    manifest={'provenance':'Original hand-assembled example, not output claimed from a recovered compiler. The BOS is equivalent illustrative source.','bytes':len(blob),'codeOffset':h[9],'entryWords':[0],'scripts':names_at(h[7],h[1]),'pieces':names_at(h[8],h[2]),'words':[f'0x{x:08X}' for x in codewords],'states':states}
    return {'example.cob':blob,'example.bos':BOS.encode(),'example.json':(json.dumps(manifest,indent=2)+'\n').encode(),
            'laboratory.json':(json.dumps(laboratory(),indent=2)+'\n').encode(),
            'motion-demo.bos':b'''// Original illustrative source; no compiled output is claimed.
// Begin with turret at encoded angle 0 and no earlier turn or spin.
piece turret, beacon;
AimDemo()
{
    hide beacon;
    turn turret to y-axis <90> speed <90>;
    wait-for-turn turret around y-axis;
    show beacon;
    return (0);
}
''',
            'thread-demo.bos':b'''// Original illustrative source; no compiled output is claimed.
// Parent begins in slot 0; slots 1..7 are initially free.
static-var parentDone, childDone;
Parent()
{
    parentDone = 0;
    childDone = 0;
    call-script Worker(42); // compare: start-script Worker(42);
    parentDone = 1;
    return (0);
}
Worker(value)
{
    childDone = value == 42;
    return (7);
}
'''}
def main():
    check=argparse.ArgumentParser();check.add_argument('--check',action='store_true');args=check.parse_args()
    for name,data in generate().items():
        path=ROOT/name
        if args.check: assert path.read_bytes()==data,f'Stale fixture: {path}'
        else:path.write_bytes(data)
    print('COB fixture and decoded walkthrough verified.' if args.check else 'Wrote original COB fixture.')
if __name__=='__main__':main()
