# V3 native water and reflection captures

Renderer revision: `774f79c69288d1fe706d3a4bb2769e5814045331`.
Worktree: `/private/tmp/nanolathe-feature-v3-water` (`docs/feature-v3-water`).
Output: `/private/tmp/nanolathe-feature-v3-water-media`.
Retail assets: `/Users/daniel/TotalAnnihilation`.
Only this presentation capture harness is added; no engine production files are modified.

Four MP4s and matching PNG posters: `water-cpu-or-off`, `water-on`, `reflection-off`, `reflection-on`. All are 960×640, 180 frames, 30 fps, 6 seconds, committed ticks 31–210. Posters use frame 0. No color processing, extra opacity, synthetic reflections, amplified effects, image scaling or cropped enlargement is applied. Engine Enhanced 2× zoom renders the native model and original map art; no synthesized DetailArt.

## Scenes and controls

The water pair is terrain only: no units are spawned and every recorded frame must contain exactly zero model commands. The real Gods of War shoreline is framed at world center (2719,704). Session seed pair 7/7 supplies normal committed wind, which changes during the clip. The normal skirmish's distant participants remain outside the camera. No unit, wake or model is visible in this water example.

`water-cpu-or-off` is **modern water effects off**, not CPU footage. It sets `SetWaterEffects(false)` and `SetWaterReflections(false)`. `water-on` enables both; with no models or projectile bodies, there are no reflected subjects. All other renderer settings are identical.

The reflection pair uses exactly one ARM transport (`armtship`) at (2759,55,704), initial heading 49152. The native 82.5-world-unit model is taller than Millennium (55.08), Warlord (47.91) and carrier (58.75), all visually probed. Its broadside loading deck and crane create a broader native reflection than the prior low cruiser. After 30 warmup ticks the fixture issues a normal movement order toward (2859,734). Subsequent position, heading, piece animation and wakes come from ordinary Session.Step and COB; no prescribed per-frame poses. Normal blue/white script wake particles remain present. Water waves and shoreline are identical in each off/on pair; only `SetWaterReflections` differs. Its native 25 percent opacity is untouched.

Both scenes use the same camera, normal fog-disabled skirmish configuration, no HUD, antialiasing, shadows, glow, lighting, blast distortion and metallic glints. Each paired image executes the exact same committed draw-list instance before another simulation step. Water and reflection are separate sessions: their RNG histories and committed wind can differ because one creates a transport and the other creates no units.

## Reproduce

Read the Ebitengine `run-ebitengine-app-headless` skill in the module before running. This capture uses the existing hidden-window workaround: all bounded captures/readbacks occur within one Draw callback because intermediate hidden Metal window presentation can fail on this host. macOS graphics access is required. Playback remains one committed tick per video frame regardless of capture wall time. These captures are not performance benchmarks.

From the worktree root:

```sh
GOCACHE=/private/tmp/nanolathe-feature-v3-water-media/go-cache GOMAXPROCS=2 go build -p 2 -o /private/tmp/nanolathe-feature-v3-water-media/capture ./.capture-water
GOMAXPROCS=2 /private/tmp/nanolathe-feature-v3-water-media/capture -scene coast -frames 180 -out /private/tmp/nanolathe-feature-v3-water-media/coast
GOMAXPROCS=2 /private/tmp/nanolathe-feature-v3-water-media/capture -scene reflection -ship armtship -heading 49152 -frames 180 -out /private/tmp/nanolathe-feature-v3-water-media/reflection
python3 .capture-water/package.py /private/tmp/nanolathe-feature-v3-water-media
```

The packaging script needs Pillow, ffmpeg and ffprobe, uses two encoding threads, creates paired 0/60/120/179-frame QA contact sheets and asserts frame counts, timing and model counts. `manifest.json` records exact toggles, unit placement, census summaries, ffprobe results and SHA-256 hashes for all raw frames, posters, videos and harness files. `-probe` captures every thirtieth tick plus the last; `-catalog` prints installed floating unit heights; `-move=false` supports stationary native heading probes. Probe outputs remain outside the deliverable set.

## Visual limits

Native reflections remain faint, rippled screen-space geometry. The hull hides some of its own reflection and the renderer never reveals offscreen or unseen faces. The transport's broad loading deck gives a clearly larger reflected footprint, while its crane reflection is still quiet against this textured water. This is an honest native example, not a claim of mirror-like water or exact physical reflections. It is a staged presentation scene with ordinary session movement, not a gameplay benchmark.

## Completed verification

The final build succeeded. Packaging verified all four streams at 960×640, 30/1 fps, 180 decoded frames and exactly 6 seconds. Every coast frame has zero model commands; every reflection frame has one. Inspected full-size off/on posters and paired animation keyframes 0/60/120/179. The shoreline remains unit-free, the ship and its reflected geometry stay in frame, and normal wake particles appear as it moves. The reflection poster changes 9,674 pixels by more than 10 channel levels (maximum 50); inspected later frames change 5,908–8,645 such pixels as the vessel turns. The reflection remains softer at diagonal headings. No engine benchmarks, commits, merges, pushes, publishing or website edits were performed.
