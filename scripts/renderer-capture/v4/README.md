# Honest website renderer comparison capture

Engine source: `ac32756e0caffbc37e0fb80b21c03d3c641f1d21` (main at capture start).
This diagnostic executable only adds files in this directory. It changes no
production renderer, simulation, runtime defaults or asset archives.

Both clients read one committed publication from one seeded ordinary session,
with identical cameras and unit/effect poses. Classic calls
`ComposeFrameSnapshot`, which executes the software indexed composer and
palette expansion. Modern calls `RecordModernFrame().Clone()` and executes
that geometry through `gpurender.Renderer` on the actual Metal device.
Separate clients both bind the production `Session.PresentationCRT()` handoff;
each client takes its own private copy as the shipping battle adapter does.
The committed publication is hashed before and after both recordings and must
remain unchanged. Full visibility is a presentation override restored afterward.

## Scene and pixels

Great Divide, simulation seed 12345 and CRT seed 67890. Original commanders
remain at their distant starts. Authored capture staging adds a Bulldog at
(1602,2084), Maverick at (1564,1999), Zeus at (1631,2169), and Jeffy at
(1671,2084). These are the initial placements; every captured pose thereafter
comes from ordinary `Session.Step` and the engine's COB/movement publication.
At frame 30, `ApplySelfDestructDamage` starts Jeffy death. Explosion art,
fragment/debris, light sources and lifetimes come from the production engine.
Nearby feature clearing calls the feature lifecycle service; no replacement
terrain or art is painted. Ninety warmup steps precede the 60 captured ticks
90–149. Camera X=1396, Z=1882, 960×640, Scale=4 (the encoded 2× detail step),
Zoom=2048 (2.0×); the exact camera is logged for both recorders every frame.

Selected explosion PNGs are frame 42 / tick 132; the brighter alternative is
frame 38 / tick 128. Every final PNG is a byte-for-byte copy of its raw capture,
960×640 with no crop, resize, sharpening, colour adjustment, caption or composite.
Two optional MP4s encode the actual same 60 frames at 30fps, exactly 2 seconds,
H.264/yuv420p CRF18, without audio, interpolation or image filters.

Greenhaven landscape: no staged units and no feature clearing. The two original
commanders remain outside the view. Center (4250,4040), tick 90; camera X=4010,
Z=3831 from that point's actual terrain height, Scale=4, Zoom=2048,
960×640. This pair provides a quiet terrain example alongside the explosion.

## Actual terrain synthesis

The harness calls the same `internal/upscale.Cache.Tiles2x` API and default
parameters as `cmd/nanolathe/detail_art.go` / GPU design §14.4. It generates
one 64×64 indexed tile per original 32×32 tile from that map's own authored
pixels, placement map, retail palette and ALP table. Algorithm version
`nanolathe.upscale.terrain.2`; iterations=8, PCA samples=100000, tone=12,
spread=16, deadzone=8, seam=0, seamzone=-1, coherence=64, settle=2, relax=true.
Workers=2 affects parallelism only; the engine contract states output is
independent of worker count.

Fresh cache first calls are computed; second calls must be cached and have
identical output bytes. The cache files are parsed against the engine header,
kind, version, tile count and exact payload. Synthesis metadata includes cache
and payload SHA-256. Great Divide produces 2820 tiles: 8214833/11550720 pixels
(71.1197%) differ from nearest doubling. Greenhaven produces 2347 tiles:
6451478/9613312 pixels (67.1098%) differ. Modern drawlist audits require those
exact detail tile counts at Scale=4; Classic records zero detail tiles and
retains the authored art nearest-doubled at the same 2× camera view.
Camera magnification alone is not counted as texture synthesis.

This comparison specifically synthesizes terrain. Feature sprite banks use
production nearest-doubled fallback; it does not claim full sprite remastering.
Derived terrain cache files stay in `/tmp/nanolathe-website-synthesis-cache-verified`
and are never copied into deliverables. Retail archives stay in the original
`/Users/daniel/TotalAnnihilation` installation and are never copied or modified.

## Lighting, glow and checks

Modern uses `drawlist.AllEffects()` and true glow, all strengths at the tuned
100% defaults (glow, source families, ground light and blast rings). Model and
ground lighting, supersampling, finishes, glints, blast rings and other default
modern effects are enabled. The pair presents the full Modern treatment; it
is not a claim that renderer differences isolate one feature.

Selected tick 132 reports 14 BattleLights, 3 GroundLights, 52 LitModelFaces,
5 GlowPasses, 5 supersampled packets and zero Classic planes in the modern list.
Classic returns 614400 indexed bytes and 16 completed Classic model planes.
Replaying the same cloned modern list with glow off changes 91477 pixels.
Turning ModelLight and GroundLight off too changes another 11576 pixels.
The unmodified control PNGs and exact changed bounding boxes are packaged.
No light radius, shader gain, source art, explosion duration or engine default
is changed. Modern also has its ordinary raster/composition/AA differences.

`verification.json` checks every frame's recorded camera, terrain choice,
software/GPU path, unchanged publication and successful CRT binding. It checks
fresh/warm cache byte identity and native dimensions, and includes ffprobe
metadata and same-list control deltas. `raw-frame-hashes.json` hashes every
raw PNG (including control frames); `manifest.json` hashes final PNGs, logs,
metadata and source. Main/alternate stills, controls, landscape pairs and
movie start/middle/end frames were visually inspected. Hardware is Apple M3 Pro
with 18 GPU cores; backend is explicitly Metal. No performance claim is made.

## Reproduce

Build from the engine revision above with this directory installed at
`cmd/website-comparison-capture`. Use an empty cache directory for a cold proof.
GPU runs need normal macOS display/Metal access; a restricted sandbox blocks
its display-service connection. The hidden capture executes bounded frames
and readback inside one Draw call, then exits, following the established
Ebitengine macOS diagnostic capture pattern. The relevant module skill was
read: `github.com/hajimehoshi/ebiten/v2@v2.10.4/skills/run-ebitengine-app-headless/SKILL.md`.

```sh
GOCACHE=/tmp/nanolathe-capture-gocache GOMAXPROCS=2 go build -p 2 -o /tmp/nanolathe-website-comparison ./cmd/website-comparison-capture
EBITENGINE_GRAPHICS_LIBRARY=metal GOMAXPROCS=2 /tmp/nanolathe-website-comparison -scene lighting -frames 60 -cache /tmp/nanolathe-website-synthesis-cache-verified -out /tmp/nanolathe-comparison-final-lighting
EBITENGINE_GRAPHICS_LIBRARY=metal GOMAXPROCS=2 /tmp/nanolathe-website-comparison -scene landscape -map Greenhaven -x 4250 -z 4040 -cache /tmp/nanolathe-website-synthesis-cache-verified -out /tmp/nanolathe-comparison-final-landscape
python3 cmd/website-comparison-capture/export.py --lighting /tmp/nanolathe-comparison-final-lighting --landscape /tmp/nanolathe-comparison-final-landscape --out /Users/daniel/Documents/Codex/2026-10-03/task/capture-output
GOCACHE=/tmp/nanolathe-capture-gocache GOMAXPROCS=2 go test -p 2 ./cmd/website-comparison-capture
```

Build and focused diagnostic package checks pass. Real GPU captures and export
assertions pass. Whole-engine integration/performance gates were not run:
this adds a capture-only diagnostic, changes no production code, and is not
being landed into engine main. No push, merge, publication or retail archive
packaging was performed. Remaining limitations are the engine's documented
two-recording route (Classic and Modern require different model packets),
feature sprite synthesis outside this diagnostic's scope, and no performance
measurement. Both walks use the same unchanged committed publication.

## Website integration

The selected frame-42 PNGs and landscape PNGs were converted with
`cwebp -lossless -exact -z 9`. FFmpeg decoded both the source PNG and lossless
WebP to RGB24; every pixel is identical. Exact PNG, WebP and decoded RGB hashes
are in `webp-export-verification.json`. Website media is under
`static/images/renderer/v4/`. The MP4s are unchanged copies of the verified
2-second encodes. The website comparison scales naturally to the viewport;
source captures have no enlargement, crop, retouching or compositing.

The prototype source was Library item
`libfile_ad4a04f3f9dc81919104b804d8d0c50c`,
`Nanolathe-prototype-beta-handoff.zip`, SHA-256
`62b680070387479cabd6b5bfbf1e4db9e9f229dc98b8239155e90f696d9eaa18`. It was used as a design reference. Private Site deployment files were
not imported. Neither the website nor capture work changed engine runtime
defaults, retail archives, DNS or any published deployment.

`manifest.json` preserves the original `../capture-output/` package inventory,
including source-relative paths and raw PNG/control/log entries. This website
folder retains a reviewable subset of that package plus the adapted README;
the original report/source and complete raw inventory remain in the task's
`capture-output/` directory. `website-media.json` is the separate inventory
for the six files actually served by this branch.
