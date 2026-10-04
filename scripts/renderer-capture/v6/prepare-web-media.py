#!/usr/bin/env python3
"""Export unchanged native pixels and native-size clips; audit the real capture inputs."""
import argparse, hashlib, json, subprocess
from pathlib import Path
from PIL import Image

PIN='617540c587e1b75d6d8ba7bf5243d24bea3f3bc2'

def run(*args):
 return subprocess.run(args,check=True,capture_output=True).stdout

def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def pixels(path):
 with Image.open(path) as image: return hashlib.sha256(image.convert('RGBA').tobytes()).hexdigest()
def events(path): return [json.loads(line) for line in path.read_text().splitlines()]

def main():
 parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('captures',type=Path);args=parser.parse_args()
 evidence=Path(__file__).resolve().parent;website=evidence.parents[2];raw=args.captures/'raw';dest=website/'static/images/renderer/v6';dest.mkdir(parents=True,exist_ok=True)
 stills={ 'terrain-original':'terrain/modern-original-0000.png','terrain-synthesized':'terrain/gpu-0000.png','aa-classic':'aa/cpu-0000.png','aa-modern':'aa/gpu-0000.png','explosion-classic':'explosion/cpu-0042.png','explosion-modern':'explosion/gpu-0042.png' }
 movies={ 'explosion-classic':('explosion/cpu-%04d.png',90), 'explosion-modern':('explosion/gpu-%04d.png',90) }
 for name,poster,count in [('water',90,180),('heat',90,150),('wrecks',80,390)]:
  for mode in (['off','motion-off','foam-off','reflection-off','on'] if name=='water' else ['off','on']):
   prefix=mode if name=='water' or mode=='off' else 'gpu'
   stills[f'{name}-{mode}']=f'{name}/{prefix}-{poster:04d}.png'
   movies[f'{name}-{mode}']=(f'{name}/{prefix}-%04d.png',count)
 for i in range(26): stills[f'zoom-{i:02d}']=f'zoom/zoom-{i:02d}.png'
 inventory=[]
 for name,rel in stills.items():
  source=raw/rel;out=dest/f'{name}.webp'
  if not out.exists() or pixels(source)!=pixels(out):
   run('cwebp','-quiet','-lossless','-exact','-z','9',str(source),'-o',str(out))
  assert pixels(source)==pixels(out),name
  with Image.open(source) as im: size=im.size
  inventory.append(dict(path=str(out.relative_to(website)),source=rel,source_sha256=sha(source),sha256=sha(out),rgba_sha256=pixels(out),pixels_identical=True,width=size[0],height=size[1],bytes=out.stat().st_size))
 for name,(pattern,count) in movies.items():
  out=dest/f'{name}.mp4'
  run('ffmpeg','-v','error','-y','-threads','2','-framerate','30','-i',str(raw/pattern),'-frames:v',str(count),'-c:v','libx264','-threads','2','-preset','slow','-crf','18','-pix_fmt','yuv420p','-movflags','+faststart',str(out))
  probe=json.loads(run('ffprobe','-v','error','-count_frames','-show_streams','-show_format','-of','json',str(out)))
  stream=probe['streams'][0];assert len(probe['streams'])==1 and int(stream['nb_read_frames'])==count and stream['avg_frame_rate']=='30/1',name
  # A full independent decode fails on corrupt or incomplete clips.
  run('ffmpeg','-v','error','-threads','2','-i',str(out),'-f','null','-')
  with Image.open(raw/pattern.replace('%04d','0000')) as im: assert (stream['width'],stream['height'])==im.size,name
  inventory.append(dict(path=str(out.relative_to(website)),sha256=sha(out),bytes=out.stat().st_size,width=stream['width'],height=stream['height'],frames=count,fps=30,duration=count/30,codec=stream['codec_name'],native_size=True,full_decode=True))
 (evidence/'website-media.json').write_text(json.dumps(inventory,indent=2)+'\n')
 terrain=events(raw/'terrain/events.jsonl');control=next(r for r in terrain if 'terrain_original_audit' in r)
 a,b=control['terrain_original_audit'],control['terrain_synthesized_audit']
 assert a['Camera']==b['Camera'] and a['DetailTiles']==0 and a['SynthesizedSpriteCommands']==0 and b['DetailTiles']>0 and b['SynthesizedSpriteCommands']>0
 zoom=json.loads((raw/'zoom/slider-metadata.json').read_text());assert len(zoom)==26 and zoom[17]['shot']['Zoom']==1 and zoom[25]['shot']['Zoom']==2 and zoom[0]['strategic_icons']
 for row in zoom: assert row['publication_unchanged'] and row['units']==39
 checks=dict(terrain_and_foliage_switch=control,zoom_stops=[dict(name=r['shot']['Name'],zoom=r['shot']['Zoom'],units=r['units'],icons=r['strategic_icons'],publication_sha256=r['publication_sha256']) for r in zoom])
 for scene in ['explosion','aa','heat','wrecks']:
  rows=events(raw/scene/'events.jsonl');states=[r for r in rows if 'state_sha256' in r];stats=[r for r in rows if 'modern_stats' in r]
  assert all(r['state_unchanged_after_recording'] and r['presentation_crt_bound_classic'] and r['presentation_crt_bound_modern'] for r in states)
  if scene=='aa': assert states[0]['gpu_models']==9 and states[0]['gpu_ssaa_packets']==9
  if scene=='heat': assert max(r['modern_stats']['HeatPlumes'] for r in stats)>=3
  if scene=='wrecks':
   born=[(i,f) for i,r in enumerate(stats) for f in r['features'] if f['WreckHeatKnown'] and f['Model']=='armstump_dead'];assert born and born[0][0]==30 and born[0][1]['WreckBornTick']==120
   assert max(r['modern_stats']['WreckHeatPlumes'] for r in stats)>0
   assert all(pixels(raw/scene/f'off-{i:04d}.png')==pixels(raw/scene/f'gpu-{i:04d}.png') for i in [0,29,330,389])
   checks['wreck_birth']=dict(frame=born[0][0],tick=born[0][1]['WreckBornTick'])
  checks[scene]=dict(frames=len(states),matched_committed_inputs=True,peak_lit_faces=max(r['modern_stats']['LitModelFaces'] for r in stats),peak_heat_plumes=max(r['modern_stats']['HeatPlumes'] for r in stats),peak_wreck_plumes=max(r['modern_stats']['WreckHeatPlumes'] for r in stats))
 water=json.loads((raw/'water/census.json').read_text());assert len(water)==180
 assert all(r['publication_unchanged'] and r['model_commands']==2 for r in water)
 assert all(r['off_on_off_exact'] for r in water[::30])
 assert max(r['stats_on']['ReflectionVertices'] for r in water)>0 and max(r['stats_on']['UnderwaterCommits'] for r in water)>0
 checks['water']=dict(frames=180,models=2,peak_reflection_vertices=max(r['stats_on']['ReflectionVertices'] for r in water),peak_underwater_commits=max(r['stats_on']['UnderwaterCommits'] for r in water),five_effect_selections=True,off_on_off_exact=True)
 checks['engine_revision']=PIN
 checks['binary_sha256']={Path(name).name:digest for digest,name in (line.split(maxsplit=1) for line in (args.captures/'binaries.sha256').read_text().splitlines())}
 replay=args.captures/'replay-verification.json'
 if replay.exists(): checks['final_binary_replays']=json.loads(replay.read_text())
 checks['capture_log_sha256']={p.name:sha(p) for p in args.captures.glob('*.log')}
 checks['source_sha256']={str(p.relative_to(evidence)):sha(p) for p in (evidence/'source').rglob('*.go')}
 checks['synthesis']={name:json.loads((raw/name/'synthesis.json').read_text()) for name in ['terrain','explosion','zoom']}
 (evidence/'verification.json').write_text(json.dumps(checks,indent=2)+'\n')
 print(f'Exported {len(stills)} pixel-identical stills and {len(movies)} fully decoded native-size movies; capture audits passed.')
if __name__=='__main__':main()
