# Features feedback: current native captures

Engine production source is pinned to `617540c587e1b75d6d8ba7bf5243d24bea3f3bc2`
(local main at capture start, October 4, 2026). The isolated diagnostic worktree
is `../nanolathe-features-v6`, branch `capture/features-feedback-v6`.
The final diagnostic harness is committed locally at
`33ee2ed83a21763f58668c39a2b4709e62179cb3`. Binaries were built before that
source-only save; their recorded hashes and Go source hashes identify the exact
producer. That initial batch adds only `cmd/website-features-capture`; production simulation, renderer,
shaders, coefficients, defaults and game data are untouched.

The harness adapts v5, retaining the actual Session/Classic/Modern paths and
normal terrain/sprite cache APIs. It refuses any graphics backend other than
actual Metal in Draw. macOS requires a display even with the window hidden;
the installed Ebitengine headless-running skill was read before captures.
A bounded `caffeinate -u -t 60` assertion wakes the display for each run without
changing persistent settings. GPU execution/readbacks complete in one Draw
callback, following the known hidden-window Metal workaround. These captures
are visual diagnostics, not performance measurements.

## Scenes and controls

- **Greenhaven explosion/home comparison:** staged center `(4280,4230)`, Jeffy
  self-destruct beside a Bulldog, Maverick and Zeus. Both renderers use the same
  committed publication and 2× camera. Poster frame42/tick132; 90 frames/3seconds.
  The fixture clears burn successors and authored crispy dead stumps through the
  feature lifecycle; surrounding healthy tree sprites remain. Modern includes
  genuine 2× synthesized tiles and sprite banks, AA, light/glow and default
  effects at native strengths. No tree artwork is substituted or composited.
- **Terrain + foliage close-up:** Greenhaven center `(4440,4130)`, native480×320
  at the 2× camera. Same Modern path, camera and committed state; `DetailArt=nil`
  versus real synthesized Tiles **and** Banks. The audit requires zero synthesized
  commands on Original and positive synthesized tile/sprite commands on Modern.
  This smaller viewport makes actual leaves and ground detail readable. Original
  tree shadows or missing variants keep the ordinary production fallback.
- **Interactive camera:** 26 freshly rendered native960×640 frames, whole-map
  minimum0.078125× plus 25 stops0.25×–2×. Default stop17 is exactly1×; stop25 is2×.
  Each stop uses the real camera/presentation view, with wide-end panning. The
  base has39 staged original models with settled COB poses; the solar formerly
  placed over metal moves to clear ground and an ARM extractor occupies the
  deposit. Placements remain fixed, visibility is supplied for presentation,
  and tactical team icons activate naturally. This is a camera study, not live
  combat or a resampled image posing as zoom.
- **Water:** Gods of War, transport `armtship` plus submerged `armsub`, ordinary
  movement orders and Session.Step. Six seconds/180frames/native960×640.
  Five executions of the same cloned drawlist at each tick: all effects off,
  all on, motion/refraction off, foam off, reflections off. Native wave strengths,
  model height and reflection opacity remain unchanged. The census proves two
  model commands, positive underwater commits/reflection vertices and exact
  off/on/off restoration. COB wakes, committed wind and shoreline are preserved.
- **Fire:** three original `architree01` palms placed through Features.PlaceAt
  and ignited at frame30 through Features.Ignite. Session.Step supplies their
  actual flames/smoke. Native480×320/2×camera,150frames/5seconds. Modern off/on
  toggles only FireShimmer; all other treatments stay constant. Three genuine
  heat plumes are verified. Poster90.
- **Wreck:** original Stumpy, ordinary damage during warmup followed by ordinary
  lethal damage at frame30. COB Killed chooses the real `armstump_dead` corpse,
  born tick120. Native480×320/2×camera,390frames/13seconds, poster80. Off/on toggles
  WreckGlow and WreckShimmer together, retaining explosion, materials and other
  effects. The full clip includes cooling/shimmer expiry. Before death and after
  expiry, selected native off/on frames match exactly. Eight first-frame/poster
  replays across heat, wreck and terrain match the final core binary byte-for-byte.
- **Model edges:** nine original units with identical poses and 2× camera in
  Classic/Modern; both have AA enabled. Classic retains structure coverage;
  Modern records nine supersampled model subjects. Vegetation is cleared from
  the tableau so no unit is obscured. Native960×640, whole renderer paths.

The material chapter restores the original interactive WebGL study, exported
from801c8b2. It is clearly distinguished from native captures; its model/light
controls, projection and browser AA differ from the game. The disclosure retains
the native v5 material turntable (279f7af1). That chapter is not represented as a
new617540c5 native export. Its original provenance is in `../live-materials/README.md`.

## Reproduction and evidence

Copy `source/` to the pinned engine checkout's `cmd/website-features-capture/`,
then run `bash cmd/website-features-capture/run.sh /absolute/artifacts /private/cache`.
From the website, run:

```sh
python3 scripts/renderer-capture/v6/prepare-web-media.py /absolute/artifacts
```

The local run reuses the verified v5 private synthesis cache. The normal cache
API checks its algorithm/parameters/content key; terrain and bank payloads,
2×dimensions, non-nearest pixel counts and cached equality are independently
recorded in `verification.json`. Camera magnification and synthesis scale are
separate properties; at zoom≤1× the runtime chooses original art.

`website-media.json` records every served file's bytes, hash, native dimensions,
frame count/duration and WebP pixel proof. WebP uses lossless/exact encoding;
PNG and WebP decoded RGBA hashes must match. MP4 uses H.264/yuv420p,30FPS,CRF18,
two encoder workers and native dimensions. No crop, resample, generated art,
compositing, color enhancement, interpolation or retiming is used. Every movie
is fully decoded independently and has its expected frame count. Browser layout
scales media naturally, with close still comparisons retaining pixel edges.

`verification.json` holds synthesis and scene audits, source/binary hashes,
committed-publication hashes and effect counters. Raw frames, full event logs,
replay evidence and private caches stay outside the website in
`../capture-features-v6/` and `/tmp/nanolathe-features-v5-cache`.
Focused diagnostic packages build and Go vet passes. Production engine landing,
performance gates and benchmarks are outside this media-only task.
No retail archives, raw sequences, synthesized banks or executable binaries are
included in the website or source deliverables. No push, merge to main, deploy
or publication is authorized by this capture work.

## Latest local follow-up

The final follow-up diagnostic sources are saved locally at
`6c0cfd983f2d082b69fbdda0027811432a07a10f`. The two read-only export helpers are isolated and
called only by the capture command.

The extractor in the zoom tableau was moved from z-offset60 to76 (one map cell
down); all26 native camera views were regenerated and pixel-audited. The revised
Go source hash and camera binary hash are in `verification.json`. Historical
core/water movies retain their original producers. `--reuse-movies` skips encoding
only when a movie’s SHA-256 matches the previous audited inventory, then still
fully decodes and verifies its frames/dimensions. Lossless WebP compression now
uses level6; decoded pixel equality remains mandatory.

Water’s primary widget is now the independent, automatically animated WebGL
study documented in `../live-water/README.md`, with one native recording retained
as a disclosure/fallback. Four older water variant movies remain as capture
evidence but are no longer the primary controls. Two new native aircraft stills
are documented separately in `../aircraft-shadows/README.md`. Its command and
water export helpers exist only in the isolated diagnostic engine worktree. No
production shader arithmetic, runtime defaults or simulation behavior changed.
