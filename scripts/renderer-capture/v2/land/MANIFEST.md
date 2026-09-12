# Land, camera and SSAA capture revision

Engine revision: `9e61946a64ee96619551579ecddf4786f7865c9d`.
Engine worktree: `/private/tmp/nanolathe-feature-revision-land`.
Retail install: `/Users/daniel/TotalAnnihilation`.
Map: Greenhaven, 8192×8192 world pixels. Enhanced GPU renderer, 960×640 output.
Captured 2026-09-12. No tracked engine files changed. No merge, push or publication.

The tableaux are presentation staging, not a running match. Real retail terrain,
placed trees/rocks, models, textures and stock COB Create/Activate poses feed the
production client and GPU renderer. Unit locations/headings are authored by this
capture driver. All map coverage is visible/explored. No effects, projectile
trajectories or gameplay results are invented. No feature positions are changed.

`source/main.go`, `source/pose.go`, `source/detail_art.go` are the complete driver.
The matching runnable copy is `.feature-capture/` in the engine worktree.

## Deliverables in final/

- `terrain-off.png`, `terrain-on.png`: ZERO units and ZERO model packets. Same
  camera (4250,4040), actual 2× detail view, same terrain and placed foliage. Off
  omits DetailArt; on loads the runtime synthesis of original terrain/sprite art.
- `ssaa-off.png`, `ssaa-on.png`: Krogoth and Annihilator at actual 2× camera zoom,
  same active retail COB poses and terrain. AntiAlias false/true. Native packet
  count 2 in both; `ModelGeometry.Supersample` count 0 off, 2 on. No executor
  override or custom shader. `ssaa-close-off.png`/`ssaa-close-on.png` are native
  pixel crops `(280,210)-(770,490)`, 490×280, without resampling.
- `zoom.mp4`: 150 freshly recorded GPU frames, 30fps, 5s, H.264, 960×640. Actual
  camera Zoom progresses 1024→2048 (1×→2×), with 117 distinct camera zoom values.
  Fixed 12-unit outpost: laboratory, two solar arrays, radar, two perimeter
  turrets, commander, construction kbot and four nearby mobile units. Camera
  center (4100,4340). `zoom-poster.png` is frame75; endpoint stills are
  `zoom-1x.png` and `zoom-2x.png`.
- `tactical.mp4`: 150 freshly recorded GPU frames, 30fps, 5s, H.264, 960×640.
  Actual camera Zoom progresses 1024→256 (1×→0.25×), with 116 distinct values.
  A fixed 38-unit scene extends the outpost with a detached utility site,
  staggered allied squads, opposing squads and an opposing vehicle outpost.
  Camera center (4500,4340), and every unit remains at the same world location
  throughout. Strategic icons and the threshold are production renderer output.
  `tactical-poster.png` is frame149; endpoints are `tactical-start.png` and
  `tactical-overview.png`.
- `zoom-web.mp4` / `tactical-web.mp4`: same exact source frames, more compact
  CRF22 H.264 encodes. The unsuffixed files use CRF16.
- `movies-metadata.json`, `stills-metadata.json`: camera, scene, AA/detail switch,
  units, model/supersample counts and GPU counters for every output frame.
- `zoom/` and `tactical/`: all original PNG frames, numbered 0000–0149.

Camera movies contain only the actual rendered camera traversal. There is no
image scale filter, wipe, interpolation between source screenshots, or crossfade.
Each frame changes camera Zoom and its corresponding production record Scale,
re-records the scene and executes the real GPU renderer. The scene freezes unit
poses; it is a camera presentation, not combat footage. Both movies hold their
endpoints for approximately half a second. Encodes have no audio.

## SSAA investigation and verification

The display toggle is working in the checked revision. In
`internal/client/model_compose.go`, `supersampleGeometry` gates doubled geometry
on AntiAlias plus palette availability. `internal/platform/gpurender/model_direct.go`
selects the doubled packet when it is present. Captured metadata verifies both
branches, independently of image comparison. The off frame has two geometry
packets and zero Supersample packets; the on frame has two of each. Their
21,213 different pixels are confined to the model/shadow area (306,221)-(773,465).
No evidence of the toggle being overwritten or an always-on extra AA pass was
found. Off at 2× already rasterizes native authored model geometry at the higher
camera resolution; a browser downscale can obscure the remaining AA difference.
Use the provided native crops if the page cannot display full-resolution frames.

The terrain pair differs in 401,552 pixels and has no units. See
`verification.json` for counts. Visually inspected both terrain/SSAA states,
movie start/mid/end PNGs and decoded H.264 keyframes. ffprobe confirms both movies
are H.264, 960×640, 30fps, 150frames, exactly5s. Driver builds with stock Go tooling.
No engine behavior changed, so engine integration/performance suites were not run.

Capture harness fixes made during QA: complete valid FogView metadata admits the
staged opposing side; deep-copy each UnitView.Pieces when publishing avoids frame
buffer reset clearing the frozen pose. These were harness defects, not engine
changes. The first multi-Draw hidden-window attempt reproduced the documented
macOS MetalDrawable.Texture crash; final captures use the existing bounded
single-Draw offscreen readback pattern. No benchmark or performance claim.

## Reproduce

From `/private/tmp/nanolathe-feature-revision-land`:

```sh
GOCACHE=/private/tmp/nanolathe-feature-v2-land/go-cache GOMAXPROCS=2 go build -p=2 -o /private/tmp/nanolathe-feature-v2-land/capture ./.feature-capture
GOMAXPROCS=2 /private/tmp/nanolathe-feature-v2-land/capture -mode stills -map Greenhaven -x 4100 -z 4340 -terrain-x 4250 -terrain-z 4040 -remaster -out /private/tmp/nanolathe-feature-v2-land/final > /private/tmp/nanolathe-feature-v2-land/stills.log 2>&1
GOMAXPROCS=2 /private/tmp/nanolathe-feature-v2-land/capture -mode movies -map Greenhaven -x 4100 -z 4340 -terrain-x 4250 -terrain-z 4040 -remaster -out /private/tmp/nanolathe-feature-v2-land/final > /private/tmp/nanolathe-feature-v2-land/movies.log 2>&1
ffmpeg -hide_banner -loglevel error -y -framerate 30 -i /private/tmp/nanolathe-feature-v2-land/final/zoom/%04d.png -c:v libx264 -threads 2 -preset slow -crf 16 -pix_fmt yuv420p -movflags +faststart /private/tmp/nanolathe-feature-v2-land/final/zoom.mp4
ffmpeg -hide_banner -loglevel error -y -framerate 30 -i /private/tmp/nanolathe-feature-v2-land/final/tactical/%04d.png -c:v libx264 -threads 2 -preset slow -crf 16 -pix_fmt yuv420p -movflags +faststart /private/tmp/nanolathe-feature-v2-land/final/tactical.mp4
ffmpeg -hide_banner -loglevel error -y -framerate 30 -i /private/tmp/nanolathe-feature-v2-land/final/zoom/%04d.png -c:v libx264 -threads 2 -preset slow -crf 22 -pix_fmt yuv420p -movflags +faststart /private/tmp/nanolathe-feature-v2-land/final/zoom-web.mp4
ffmpeg -hide_banner -loglevel error -y -framerate 30 -i /private/tmp/nanolathe-feature-v2-land/final/tactical/%04d.png -c:v libx264 -threads 2 -preset slow -crf 22 -pix_fmt yuv420p -movflags +faststart /private/tmp/nanolathe-feature-v2-land/final/tactical-web.mp4
```

GPU commands need normal macOS display/Metal access (outside the restricted
filesystem sandbox). Source and run logs are kept alongside this manifest.
