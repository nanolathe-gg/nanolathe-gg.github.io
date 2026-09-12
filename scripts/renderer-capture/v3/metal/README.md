# Native metallic glint turntable

Presentation capture at engine commit `774f79c69288d1fe706d3a4bb2769e5814045331`,
branch `docs/feature-v3-metal`, isolated worktree
`/private/tmp/nanolathe-feature-v3-metal`. Production engine files are unmodified.
No benchmarks, commits, merges, or publication were performed.

The selected subject is ARM mobile Annihilator (`armmanni`), using original retail
model/texture assets. Eighteen candidate units/buildings were inspected at sixteen
headings each. Its broad sloped neutral armor produces a clearer rotating native
highlight than Krogoth's small shoulder glint. The production effect is described
in `docs/DESIGN_GPU_RENDERER.md` §23.7 and implemented by `metal_glint.go`.

This is an explicitly staged turntable, not live combat or simulation motion.
The original COB Create/Activate pose is settled for 300 ticks before activation
and another 300 after activation, then frozen. Only the copied UnitView heading
changes: `uint16(12288 + frame * 65536 / 240)`. Piece slices are deep-copied for
every frame. The original unit never receives simulation orders or fabricated
piece transforms. The subject completes one constant-speed 360-degree turn in
8 seconds at 30 fps; the last-to-first heading step completes the loop.

The scene uses original Comet Catcher terrain at world `(512,512)`, ground height
55. Features are omitted for this staged material display. There is one unit,
no combat, no additional lights, and no image treatment to increase the effect.
Enhanced AA, native shadow settings and the production renderer are used.
Both views execute the same recorded draw list, changing only SetMetalGlint.
The off setting uses the existing native production comparison control.

Capture is 512×384 at native engine 2× zoom. Delivery is a pixel-exact crop
`(96,96)-(416,352)`, yielding 320×256, with no spatial resizing. The full rotation's
changing object/shadow pixels occupy `(178,134)-(343,301)` in the raw frame, so the
crop preserves all model, cannon, and shadow extents. The H264 video has ordinary
lossy encoding (CRF 12, YUV420p); the PNG posters are lossless native crops.

The hidden Metal runner does every bounded readback inside one Draw to avoid the
known host drawable acquisition failure. An initial off submission/readback warms
the renderer before paired capture: without it, a cold first-frame off/on/off
check was not exact. With warm-up, off/on/off restores byte-identically. This
capture harness does not diagnose or change production cache behavior.

## Reproduce

From the pinned worktree, with installed original assets at
`/Users/daniel/TotalAnnihilation`:

```sh
GOMAXPROCS=2 go build -p 2 -o /private/tmp/nanolathe-feature-v3-metal-media/capture ./.capture-metal
GOMAXPROCS=2 EBITENGINE_GRAPHICS_LIBRARY=metal /private/tmp/nanolathe-feature-v3-metal-media/capture -units armmanni -frames 240 -heading 12288 -map 'Comet Catcher' -out /private/tmp/nanolathe-feature-v3-metal-media/final
python3 .capture-metal/export.py
```

The installed Ebitengine v2.10.1 headless skill was read before rendering. This
isolated direct-GPU harness uses the same hidden-window approach and preserves
production renderer source. Build and H264 encoding use at most two threads.

## Artifacts and verification

Outputs live at `/private/tmp/nanolathe-feature-v3-metal-media/`:

- `metal-off.mp4`, `metal-on.mp4`: 240 frames, 8 seconds, 30 fps, H264/YUV420p.
- `metal-off.png`, `metal-on.png`: matching first-frame posters.
- `qa-raw.png`, `qa-decoded.png`: native-size QA pairs at frames 0/60/120/180/239.
- `final/armmanni/`: all 480 original GPU-readback PNGs.
- `final/metadata.json`: heading and GPU model census for every frame.
- `manifest.json`: ffprobe results, all-frame quantitative differences and SHA256
  hashes for final media and raw frames; supplemental verification records source
  hashes and visual inspection.
- `scout/`, `scout2/`: all 18 candidates, heading sweeps, native crop contact sheets
  and measured differences; investigation artifacts, not final media.

Visual inspection of raw and decoded start, quarter, middle, three-quarter, and
end frames shows the armor highlight brightening and fading as the model turns.
The gun and body remain wholly inside the crop. Original texture, blue paint,
and background remain legible. The static poster is intentionally chosen at a
clear native highlight orientation; the actual effect does not depend on time.
All frames use one GPU subject with no skipped/overflow model. No performance
claims are made from capture readbacks or these files.
