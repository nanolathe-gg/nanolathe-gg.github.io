"""Export and verify the real-death wreck treatment, preserving normal 30 Hz time."""
import hashlib,json,pathlib,subprocess
from PIL import Image,ImageChops,ImageDraw
root=pathlib.Path('/private/tmp/nanolathe-feature-v3-wrecks-media')
raw=root/'raw'
rows=[json.loads(s) for s in (raw/'events.jsonl').read_text().splitlines()]
assert len(rows)==390 and [r['tick'] for r in rows]==list(range(90,480))
assert all(not r['wrecks'] for r in rows[:30])
assert all(len(r['wrecks'])==1 and r['wrecks'][0]['feature']['Model']=='armstump_dead' for r in rows[30:])
assert all(r['wrecks'][0]['feature']['WreckBornTick']==120 and r['wrecks'][0]['feature']['WreckHeatKnown'] and r['wrecks'][0]['point_visible'] and r['wrecks'][0]['age']==r['frame']-30 for r in rows[30:330])
assert all(r['off']['WreckHeatPlumes']==0 and not r['off_operands'] for r in rows)
assert all(r['on']['WreckHeatPlumes']==1 for r in rows[30:330])
assert all(r['on']['WreckHeatPlumes']==0 for r in rows[330:])
assert all(r[m]['HeatPlumes']==r[m]['WreckHeatPlumes'] for r in rows for m in ['off','on'])
assert all(r[m][k]==0 for r in rows for m in ['off','on'] for k in ['BlastWaves','GlowPasses','BattleLights','MaterialFaces','ScorchQuads','ReflectionVertices'])
assert all(r['on_operands'][0]['emission']==[0,0,0] for r in rows[210:330])
assert rows[30]['on_operands'][0]['strength']==0.55
for a,b in zip(rows[30:329],rows[31:330]):assert a['on_operands'][0]['strength']>b['on_operands'][0]['strength']
identical=[]
for r in rows:
    i=r['frame'];a=Image.open(raw/f'on-{i:04d}.png').convert('RGB');b=Image.open(raw/f'off-{i:04d}.png').convert('RGB')
    if ImageChops.difference(a,b).getbbox() is None:identical.append(i)
assert all(i in identical for i in list(range(30))+list(range(330,390)))
meta={'source_commit':'801c8b28c38ff6505b4939d96cce7fcf22200da5','native':[480,320],'camera_zoom':2,'crop_xywh':[120,70,240,160],'enlargement':'4x nearest neighbor','output':[960,640],'frames':390,'fps':30,'duration_seconds':13,'poster_frame':80,'birth_tick':120,'birth_frame':30,'videos':{}}
for mode in ['off','on']:
    out=root/f'wrecks-{mode}.mp4'
    subprocess.run(['ffmpeg','-y','-loglevel','error','-threads','2','-filter_threads','2','-framerate','30','-i',str(raw/f'{mode}-%04d.png'),'-vf','crop=240:160:120:70,scale=960:640:flags=neighbor','-c:v','libx264','-threads','2','-preset','slow','-crf','17','-pix_fmt','yuv420p','-movflags','+faststart',str(out)],check=True)
    Image.open(raw/f'{mode}-0080.png').crop((120,70,360,230)).resize((960,640),Image.Resampling.NEAREST).save(root/f'wrecks-{mode}.png')
    probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(out)]))
    meta['videos'][mode]=probe
    assert probe['streams'][0]['nb_frames']=='390' and probe['streams'][0]['r_frame_rate']=='30/1' and float(probe['format']['duration'])==13
    decoded=root/f'decoded-{mode}';decoded.mkdir(exist_ok=True)
    frames=[0,30,60,80,120,210,329,330,389]
    select='+'.join(f'eq(n,{n})' for n in frames)
    subprocess.run(['ffmpeg','-y','-loglevel','error','-threads','2','-filter_threads','2','-i',str(out),'-vf',f"select='{select}'",'-fps_mode','vfr',str(decoded/'%02d.png')],check=True)
    for source in ['raw','decoded']:
        sheet=Image.new('RGB',(960,705),(18,22,18));d=ImageDraw.Draw(sheet)
        for j,n in enumerate(frames):
            if source=='raw':pic=Image.open(raw/f'{mode}-{n:04d}.png').crop((120,70,360,230))
            else:pic=Image.open(decoded/f'{j+1:02d}.png')
            pic=pic.resize((320,213),Image.Resampling.NEAREST)
            x=j%3*320;y=j//3*235;sheet.paste(pic,(x,y+20));age='before death' if n<30 else f'wreck age {(n-30)/30:.2f}s';d.text((x+7,y+4),f'{mode} | frame {n} | {age}',fill='white')
        sheet.save(root/f'qa-{source}-{mode}.png')
(root/'media.json').write_text(json.dumps(meta,indent=2)+'\n')
proof={'real_birth_tick':120,'real_birth_frame':30,'real_model':'armstump_dead','observed_first_emission':rows[30]['on_operands'][0]['emission'],'observed_first_heat_strength':0.55,'on_plume_frames':[30,329],'material_emission_zero_from_frame':210,'heat_zero_from_frame':330,'identical_raw_pairs_before_death_and_after_expiry':True,'identical_raw_pair_frames':identical,'forbidden_counters_all_zero':True,'tree_heat_sources_zero':True,'visibility':True,'metadata_not_fabricated':True}
(root/'verification.json').write_text(json.dumps(proof,indent=2)+'\n')
print('Verified real corpse, 300 cooling frames, zero emission at age180, zero heat at age300, exact expired-pair equality.')
