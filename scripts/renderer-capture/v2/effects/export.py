import json, pathlib, subprocess, shutil
root=pathlib.Path('/private/tmp/nanolathe-feature-v2-effects')
for scene in ['lighting','shockwave','fire']:
    folder=root/scene
    if not folder.exists(): continue
    rows=[json.loads(x) for x in (folder/'events.jsonl').read_text().splitlines()]
    if len(rows)!=150: continue
    assert [r['tick'] for r in rows]==list(range(90,240))
    for mode in ['off','on']:
        assert len(list(folder.glob(mode+'-*.png')))==150
        subprocess.run(['ffmpeg','-y','-loglevel','error','-framerate','30','-i',str(folder/(mode+'-%04d.png')),'-c:v','libx264','-threads','2','-preset','slow','-crf','18','-pix_fmt','yuv420p','-movflags','+faststart',str(root/(scene+'-'+mode+'.mp4'))],check=True)
        poster={'lighting':39,'shockwave':36,'fire':90}[scene]
        shutil.copyfile(folder/(mode+f'-{poster:04d}.png'),root/(scene+'-'+mode+'.png'))
    key={'lighting':'LitModelFaces','shockwave':'BlastWaves','fire':'HeatPlumes'}[scene]
    assert max(r['on'][key] for r in rows)>0
    assert max(r['off'][key] for r in rows)==0
    print(scene, 'validated frames=',len(rows),'peak',key,max(r['on'][key] for r in rows),flush=True)
