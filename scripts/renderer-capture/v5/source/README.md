# Features capture v5

Capture-only diagnostics for the local website refresh. Engine production source
is pinned at `279f7af159a7d33ffd16358d1133434d9d48c7b9` (main inspected on
2026-10-04 UTC). Only this directory is added to the engine checkout. No renderer
or runtime defaults, coefficients, production packages, or retail archives change.

This adapts the website's v4 real Session/Classic/Modern harness, v2 camera fixture,
and v3 water/material controls. `common/detail_art.go` follows the pinned command
loader's map-bank coverage, example exclusions, and shadow fallback, using the
normal `internal/upscale.Cache.Tiles2x` and `Bank2x` APIs. Changes to that loader
copy are direct filesystem/cache arguments, Workers=2, and diagnostic cache flags.

## Run

From this isolated engine checkout with mounted retail content at
`/Users/daniel/TotalAnnihilation`, an active macOS display, Go, Python/Pillow,
ffmpeg, and ffprobe:

```sh
bash cmd/website-features-capture/run.sh /absolute/artifact/directory
```

Run sequentially on Metal. The hidden window still needs a real display. The
bounded `caffeinate -u -t 60` assertion wakes the display temporarily and changes
no persistent OS setting. All frames are rendered inside one Draw callback to
avoid the known hidden-window repeated drawable acquisition failure. Native
GPU Execute/ReadPixels and the normal shader/geometry paths are used throughout;
this is offline capture, not a frame-rate or performance measurement.
Each harness checks `ebiten.ReadDebugInfo` in Draw and refuses any actual backend
other than Metal. Positive bounded probes are logged separately and their first
frames are compared byte-for-byte with the original captures.

`run.sh` lists each exact scene command. Builds and encoders use two workers.
`export.py` copies native PNG posters byte-for-byte and encodes movies at30fps,
H.264/yuv420p (CRF18, material CRF12), without any crop, resize, compositing,
generated art, color enhancement, or video image filter. It independently
decodes every movie, checks dimensions/duration/count, and writes frame checksums.
It hashes every raw PNG and selected poster, including RGBA decoded-pixel hashes.

## What is captured

| Asset | Native size | Input and control |
|---|---|---|
| explosion-classic/modern |960×640,90frames/3s | Great Divide seeded Session.Step; staged four units, Jeffy self-destruct at frame30; same presentation-overridden publication and camera. Poster42/tick132. Classic software indexed path versus Metal Modern default effects, real synthesized tiles and foliage. |
| terrain-original/synthesized |960×640 | Greenhaven quiet map, same Modern renderer/default effects/camera, Tiles=nil versus actual synthesized tiles. Synthesized Banks stay held constant. |
| landscape-classic/modern |960×640 | Supplemental quiet whole-renderer pair from the same terrain scene. |
| camera-tactical |960×640,180frames/6s | Staged38-unit outpost/forces, original COB poses, actual camera2×→0.25×. Start centered4100,4340; pan400 world pixels with smoothstep while zoom eases outward. Default tactical view/icons activate. Poster0 shows the outpost; end179 included separately. |
| water-off/on |960×640,180frames/6s | Gods of War shore, real seeded Session.Step. No visible models. Off disables WaterSurface/Motion/Foam/Reflections only. Original map art in both. |
| reflection-off/on |960×640,180frames/6s | Same shore, original ARMtransport, real queued movement and Session.Step. Only WaterReflections toggles. Default waves/foam remain on. |
| materials-off/on |512×512,180frames/6s | Explicit staged original ARM model turntable(armmanni), original COB poses; heading changes through one turn at2×camera. Only Finish/Glint toggle, Scorch=false on both. No synthesis installed. Poster35. |
| aa-classic/modern |960×640 | Supplemental staged five-model tableau, same2×camera/publication, Anti-Alias=true on both. Classic retail structure AA versus Modern Supersample=true on every model. Whole paths also differ in terrain/foliage/materials.1×native pair supplied separately. |

Water and material pairs execute one cloned immutable drawlist off/on. Their
off/on/off checks restore exactly; committed publications are hashed before and
after recording/execution. Core checks the same committed presentation inputs
and camera for Classic and Modern; visibility is overridden only for capture and
restored afterward. AA headings are a staged presentation choice, also restored.
Features inside the core fixture use the production lifecycle removal API;
AA also removes the burnt successor so a tree cannot obscure model edges.

## Synthesis proof

Tiles use the real engine's terrain algorithm `nanolathe.upscale.terrain.2`,
32×32→64×64, one tile per source entry. Defaults: Iterations8, Samples100000,
Tone12, Spread16, Deadzone8, Seam0, SeamZone-1, Coherence64, Settle2, Relax=true.
Workers2 affects elapsed time only. The first cold computation and cached read
return identical indexed payloads. The harness checks non-nearest output pixels
and validates the private cache's `NLUPSCALE` header, kind1, version1, tile count,
exact payload, whole cache SHA256, and decoded tile payload SHA256.

Foliage proof is independent: normal named map feature-bank `Bank2x` synthesis,
algorithm `nanolathe.upscale.bank.2`. Default sprite parameters: Iterations8,
Tone64, Deadzone0, Seam8, Coherence32, Coverage200000, Mismatch12288,
Closeness1728, Tie2, Relax=true, ClampEdges=false. Example exclusions are
burn/boom/fire/smoke/rec; they exclude examples, not named query outputs.
Every synthesized nonnil frame has verified2×dimensions and anchor offsets,
indexed pixel hashes, non-nearest pixel counts, and identical cached readback.
Drawlist sprite-pointer audits prove these outputs actually reach the renderer.

Runtime fallback remains for shadow twins, entries the map definitions do not
name, absent variants, and unsupported/empty/composite/overflow-anchor frames.
The tiny geotherm stub is synthesized through the API but has zero pixel changes
versus nearest doubling; the proof does not claim every output adds detail.
At zoom≤1×, production selects original tiles/sprites. Camera zoom is recorded
separately from synthesis scale and is never presented as texture synthesis.

## Controls and limits

Core and camera use AllEffects: WaterSurface/Motion/Foam/Reflections,
HovercraftLandWash, ModelLight, GroundLight, Finish, Glint, BlastRings,
FireShimmer(tree heat), WreckGlow, WreckShimmer, Scorch, SoftShadows, Supersample
all true; glow families and ShadowSoftness100. Glow=true, normal strengths100,
master/vehicle/shading=true, Anti-Alias=true. Modern distortion and tree/wreck
heat are enabled but only draw when the scene supplies a source. Classic uses
its own whole indexed composition and ignores Modern effect choices.
Production CRT is bound through Session.PresentationCRT for session scenes;
staged scenes use the same public SetPresentationCRT API with a private seeded
CRT. No temporary global RNG hook or simulation RNG is used for presentation.

The native finishes/glint, water motion, and reflection are deliberately subtle
at production coefficients. Material and camera scenes are staged displays,
not claims of battle behavior. The AA comparison demonstrates whole paths and
does not isolate supersampling as the only difference. Diagnostic lighting/glow
controls are preserved in raw frames30–42. Full engine landing/performance gates
are outside this capture-only task; focused build/test/vet and capture audits
are the verification. Retail archives, model/sprite source art, derived synthesis
caches, and executables are excluded from the deliverable source bundle.
