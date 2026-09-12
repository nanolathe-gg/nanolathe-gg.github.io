"""Export identical nearest-neighbor crops; two-thread H.264 encoding."""
import hashlib,json,pathlib,subprocess
from PIL import Image,ImageChops
root=pathlib.Path('/private/tmp/nanolathe-feature-v3-cpu-media')
crop=(120,70,360,230)
rows=[json.loads(s) for s in (root/'raw-lighting/events.jsonl').read_text().splitlines()]
assert len(rows)==150 and [r['tick'] for r in rows]==list(range(90,240))
assert all(r['cpu_indexed_bytes']==480*320 and r['cpu_classic_model_planes']>0 and r['gpu_classic_planes']==0 for r in rows)
assert all(r['gpu_stats'][k]==0 for r in rows for k in ['BlastWaves','HeatPlumes','WreckHeatPlumes','GlowPasses','ReflectionVertices'])
assert max(r['gpu_stats']['LitModelFaces'] for r in rows)>0
for mode in ['cpu','gpu']:
    Image.open(root/'raw-aa'/f'{mode}-0000.png').crop(crop).resize((960,640),Image.Resampling.NEAREST).save(root/f'aa-{mode}.png')
metadata={'source_commit':'774f79c69288d1fe706d3a4bb2769e5814045331','native':[480,320],'crop_xywh':[120,70,240,160],'enlargement':'4x nearest neighbor','output':[960,640],'fps':30,'frames':150,'poster_frame':34,'videos':{}}
for mode in ['cpu','gpu','glow']:
    dest=root/f'lighting-{mode}.mp4'
    cmd=['ffmpeg','-y','-loglevel','error','-threads','2','-filter_threads','2','-framerate','30','-i',str(root/'raw-lighting'/f'{mode}-%04d.png'),'-vf','crop=240:160:120:70,scale=960:640:flags=neighbor','-c:v','libx264','-threads','2','-preset','slow','-crf','18','-pix_fmt','yuv420p','-movflags','+faststart',str(dest)]
    subprocess.run(cmd,check=True)
    Image.open(root/'raw-lighting'/f'{mode}-0034.png').crop(crop).resize((960,640),Image.Resampling.NEAREST).save(root/f'lighting-{mode}.png')
    probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(dest)]))
    metadata['videos'][mode]=probe
    assert probe['streams'][0]['nb_frames']=='150' and probe['streams'][0]['r_frame_rate']=='30/1' and float(probe['format']['duration'])==5
(root/'media.json').write_text(json.dumps(metadata,indent=2)+'\n')
# Same modern draw list with lighting off gives evidence beyond renderer AA differences.
a=Image.open(root/'raw-lighting/gpu-0034.png').convert('RGB')
b=Image.open(root/'raw-lighting/gpu-no-light-0034.png').convert('RGB')
diff=ImageChops.difference(a,b)
proof={'frame':34,'light_only_changed_bbox':diff.getbbox(),'receiver_crop_xyxy':[187,128,228,180],'receiver_changed_pixels':sum(p!=(0,0,0) for p in diff.crop((187,128,228,180)).getdata()),'peak_lit_faces':max(r['gpu_stats']['LitModelFaces'] for r in rows),'cpu_path':'Client.ComposeFrameSnapshot -> composeCurrentFrame -> list.Replay(classicSink) -> indexed framebuffer -> palette-expanded RGBA','modern_classic_planes':0}
assert proof['receiver_changed_pixels']>0
(root/'verification.json').write_text(json.dumps(proof,indent=2)+'\n')
print(json.dumps(proof))
