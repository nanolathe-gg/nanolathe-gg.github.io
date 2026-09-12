from pathlib import Path
from PIL import Image, ImageChops, ImageDraw
import subprocess,json,hashlib
ROOT=Path('/private/tmp/nanolathe-feature-v3-metal-media')
RAW=ROOT/'final/armmanni'
CROP=(96,96,416,352)
SAMPLES=(0,60,120,180,239)
def call(args):return subprocess.check_output(args,text=True)
for mode in ('off','on'):
 subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-y','-threads','2','-framerate','30','-i',str(RAW/f'{mode}-%04d.png'),'-vf','crop=320:256:96:96','-c:v','libx264','-threads','2','-preset','slow','-crf','12','-pix_fmt','yuv420p','-movflags','+faststart','-an',str(ROOT/f'metal-{mode}.mp4')],check=True)
 Image.open(RAW/f'{mode}-0000.png').crop(CROP).save(ROOT/f'metal-{mode}.png')
 for n in SAMPLES:
  subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-y','-threads','2','-i',str(ROOT/f'metal-{mode}.mp4'),'-vf',f'select=eq(n\\,{n})','-frames:v','1','-threads','2',str(ROOT/f'decoded-{mode}-{n:04d}.png')],check=True)
# Exact pixel crops at native size; contact sheets are QA only and are not delivered video.
for kind in ('raw','decoded'):
 sheet=Image.new('RGB',(640,280*len(SAMPLES)),(16,18,23));draw=ImageDraw.Draw(sheet)
 for row,n in enumerate(SAMPLES):
  for col,mode in enumerate(('off','on')):
   im=Image.open(RAW/f'{mode}-{n:04d}.png').crop(CROP) if kind=='raw' else Image.open(ROOT/f'decoded-{mode}-{n:04d}.png')
   sheet.paste(im,(col*320,row*280+24))
  draw.text((8,row*280+6),f'{kind} frame {n} / {n/30:.2f}s        OFF                            ON',fill='white')
 sheet.save(ROOT/f'qa-{kind}.png')
rows=[]
for n in range(240):
 a=Image.open(RAW/f'off-{n:04d}.png').convert('RGB').crop(CROP)
 b=Image.open(RAW/f'on-{n:04d}.png').convert('RGB').crop(CROP)
 diff=ImageChops.difference(a,b);pixels=list(diff.getdata())
 rows.append(dict(frame=n,heading=(12288+n*65536//240)%65536,changed_pixels=sum(max(p)>0 for p in pixels),strong_pixels=sum(max(p)>=16 for p in pixels),peak_channel_delta=max(max(p) for p in pixels),sum_rgb_delta=sum(sum(p) for p in pixels)))
checks={}
for mode in ('off','on'):
 checks[mode]=json.loads(call(['ffprobe','-v','error','-count_frames','-show_entries','stream=codec_name,width,height,pix_fmt,r_frame_rate,nb_read_frames,duration','-show_entries','format=duration','-of','json',str(ROOT/f'metal-{mode}.mp4')]))
manifest=dict(engine_commit='774f79c69288d1fe706d3a4bb2769e5814045331',model='armmanni',map='Comet Catcher',center=[512,512],ground_height=55,staging='original active COB pose frozen; heading rotates 360 degrees at constant speed',native_render=[512,384],camera_zoom=2,crop=list(CROP),output_size=[320,256],fps=30,frames=240,duration=8,initial_heading=12288,unit_count=1,background='original map terrain; map features omitted',differences='only gpurender.SetMetalGlint false/true; identical recorded draw list per paired frame',verification=checks,raw_differences=rows,hashes={})
for f in sorted(ROOT.glob('metal-*')):manifest['hashes'][f.name]=dict(sha256=hashlib.sha256(f.read_bytes()).hexdigest(),bytes=f.stat().st_size)
for f in sorted(RAW.glob('*.png')):manifest['hashes'][str(f.relative_to(ROOT))]=dict(sha256=hashlib.sha256(f.read_bytes()).hexdigest(),bytes=f.stat().st_size)
(ROOT/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
print(json.dumps({'files':{k:v for k,v in manifest['hashes'].items() if k.startswith('metal-')},'frame0':rows[0],'peak':max(rows,key=lambda r:r['strong_pixels']),'min':min(rows,key=lambda r:r['strong_pixels'])},indent=2))
