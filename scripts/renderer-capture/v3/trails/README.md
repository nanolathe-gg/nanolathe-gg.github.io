# Footprints and tank tracks

Engine: `774f79c69288d1fe706d3a4bb2769e5814045331`. Harness-only worktree
`/private/tmp/nanolathe-feature-v3-trails`, branch `docs/feature-v3-trails`.
No production engine files changed, no commit/merge/publication or benchmarks.

Original Comet Catcher terrain, camera centred at (512,512), native 2× zoom,
960×640. One ARM Hammer and one ARM Bulldog begin in two lanes. Obstructing
features inside the demonstration clearing are removed via the feature lifecycle
service before setup. Both units receive ordinary move orders toward the right. The Hammer begins
facing east (heading 49152) so its walking starts without a large turn.
Subsequent positions, turns, COB poses, marks and fading use normal Session.Step
and Client.ObserveCommittedTick. Original commanders remain elsewhere so the
normal skirmish session stays alive. Only the two demonstration units are in view.

The clip is 420 frames at 30 FPS: ticks 31–450, 14 seconds. Ground marks come
from the actual modern trail recorder and destination shader; no separate image
or fabricated effect is drawn. The capture records at most 26 footprint marks
and 68 track segments in view. Their native 300-tick lifespan lets early marks
fade before the loop resets. Camera, initial placements and orders are authored.
Simulation seeds are 7/7; fog is disabled through normal skirmish settings.

Run from the isolated worktree with original assets at
`/Users/daniel/TotalAnnihilation` after copying main.go into `.capture-trails/`:

```sh
GOCACHE=/private/tmp/nanolathe-feature-v3-capture-cache GOMAXPROCS=2 go build -p=2 -o /private/tmp/nanolathe-feature-v3-trails-media/capture-small ./.capture-trails
GOMAXPROCS=2 /private/tmp/nanolathe-feature-v3-trails-media/capture-small -walker armham -frames 420 -out /private/tmp/nanolathe-trails-small-final
ffmpeg -framerate 30 -i /private/tmp/nanolathe-trails-small-final/on-%04d.png -c:v libx264 -threads 2 -preset slow -crf 18 -pix_fmt yuv420p -movflags +faststart /private/tmp/nanolathe-feature-v3-trails-media/trails-small.mp4
```

The Ebitengine headless skill was read before execution. As in earlier captures,
a hidden native Metal context performs all bounded readbacks within one Draw
call to avoid the host presentation crash. The final clip is full-frame, with no
crop or spatial resampling; lossless WebP poster uses frame 240. Raw frame and
census output remains under `/private/tmp/nanolathe-trails-small-final/`.
`verification.json` records frame/tick/mark counts, census hash and codec data.
Both mark types were checked in the raw frames and decoded 8-second frame.

The Hammer replaces the original Krogoth after probing Hammer, Storm and Zeus.
Its committed COB leg cycle repeats every 17 ticks at a steady 1.1 world pixels
per tick: approximately 9.35 pixels per alternating step, close to the native
10-pixel footprint spacing. This is a visual fit, not animation-event sync: the
renderer records marks by distance travelled. No gait or trail settings changed.
The census preserves each committed walker pose for the selection evidence.
