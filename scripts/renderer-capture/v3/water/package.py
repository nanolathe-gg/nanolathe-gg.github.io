#!/usr/bin/env python3
"""Package the capture's raw paired frames; requires ffmpeg, ffprobe, Pillow."""
import hashlib
import json
import shutil
import subprocess
import sys
from pathlib import Path
from PIL import Image, ImageChops

root = Path(sys.argv[1] if len(sys.argv) > 1 else '/private/tmp/nanolathe-feature-v3-water-media')
variants = {'water-on': ('coast', 'on'), 'water-cpu-or-off': ('coast', 'water-off'),
            'reflection-on': ('reflection', 'on'), 'reflection-off': ('reflection', 'reflections-off')}
for stem, (scene, prefix) in variants.items():
    subprocess.run(['ffmpeg', '-hide_banner', '-loglevel', 'error', '-y', '-threads', '2',
        '-framerate', '30', '-i', str(root/scene/(prefix+'-%04d.png')), '-frames:v', '180',
        '-c:v', 'libx264', '-threads', '2', '-crf', '17', '-preset', 'slow',
        '-pix_fmt', 'yuv420p', '-movflags', '+faststart', str(root/(stem+'.mp4'))], check=True)
    shutil.copyfile(root/scene/(prefix+'-0000.png'), root/(stem+'.png'))

manifest = {'engine_revision': '774f79c69288d1fe706d3a4bb2769e5814045331',
    'map': 'Gods of War', 'camera_center': [2719,704], 'zoom': 2,
    'size': [960,640], 'frames': 180, 'fps': 30, 'duration_seconds': 6,
    'tick_range': [31,210], 'poster_frame': 0, 'seeds': [7,7],
    'same_recorded_state': 'Each off/on pair executes the same list instance before another Session.Step.',
    'water_control': {'renderer': 'modern', 'on': {'SetWaterEffects': True, 'SetWaterReflections': True},
                      'off': {'SetWaterEffects': False, 'SetWaterReflections': False},
                      'label': 'Modern water effects off (not a CPU capture)'},
    'reflection_control': {'SetWaterEffects': True, 'on': {'SetWaterReflections': True},
                          'off': {'SetWaterReflections': False}, 'strength': 'unaltered native 25 percent'},
    'reflection_ship': {'definition': 'armtship', 'model_top_world_units': 82.5,
                        'initial_position': [2759,55,704], 'initial_heading': 49152,
                        'ordinary_move_destination': [2859,734], 'spawned_count': 1},
    'scene_setup': 'Authored placement and normal move command; session handles later movement, COB, wind and effects. Distant normal skirmish participants remain outside camera.',
    'files': {}, 'census': {}, 'verification': {}}
for scene, off in [('coast','water-off'), ('reflection','reflections-off')]:
    census = json.loads((root/scene/'census.json').read_text())
    assert len(census) == 180
    assert [r['tick'] for r in census] == list(range(31,211))
    model_counts = sorted(set(r['model_commands'] for r in census))
    assert model_counts == ([0] if scene=='coast' else [1])
    wind_states = []
    for r in census:
        if r['wind'] not in wind_states: wind_states.append(r['wind'])
    rows = []
    for n in [0,60,120,179]:
        a = Image.open(root/scene/f'on-{n:04}.png').convert('RGB')
        b = Image.open(root/scene/f'{off}-{n:04}.png').convert('RGB')
        d = ImageChops.difference(a,b)
        vals = [max(v) for v in d.get_flattened_data()]
        rows.append({'frame': n, 'changed_pixels_above10': sum(v>10 for v in vals), 'maximum_channel_difference': max(vals), 'difference_bbox': d.getbbox()})
    manifest['census'][scene] = {'model_command_counts': model_counts, 'wind_states': wind_states, 'sample_differences': rows}
    sheet = Image.new('RGB',(960,1280))
    for i,n in enumerate([0,60,120,179]):
        for col,prefix in enumerate([off,'on']):
            im = Image.open(root/scene/f'{prefix}-{n:04}.png'); im.thumbnail((480,320));sheet.paste(im,(col*480,i*320))
    sheet.save(root/(scene+'-qa.png'))
for stem in variants:
    p=root/(stem+'.mp4')
    info=json.loads(subprocess.check_output(['ffprobe','-v','error','-count_frames','-show_entries','stream=width,height,r_frame_rate,nb_read_frames,duration','-of','json',str(p)]))['streams'][0]
    assert (info['width'],info['height'],info['r_frame_rate'],info['nb_read_frames'],float(info['duration'])) == (960,640,'30/1','180',6.0)
    manifest['verification'][p.name]=info
for p in sorted(root.glob('*')):
    if p.suffix in ['.mp4','.png']: manifest['files'][p.name]={'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'bytes':p.stat().st_size}
for scene in ['coast','reflection']:
    for p in sorted((root/scene).glob('*')):
        if p.is_file():manifest['files'][str(p.relative_to(root))]={'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'bytes':p.stat().st_size}
for p in sorted(Path(__file__).parent.glob('*')):
    if p.is_file():manifest['files']['harness/'+p.name]={'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'bytes':p.stat().st_size}
(root/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
print(json.dumps({'verification':manifest['verification'],'census':manifest['census']},indent=2))
