# Renderer feature captures

All screenshots and silent clips are actual Nanolathe output using a separate
retail Total
Annihilation installation. No extracted playable game assets are bundled.
Classic CPU examples use Nanolathe's indexed software renderer; none are captures
of the retail executable. Captions identify exact controls and scene staging.

The Features page uses native engine captures throughout. `live-materials/`
preserves the earlier browser material study and its provenance; that study is
no longer loaded by the Features page.

## Refreshed Features captures

`v5/` records engine `279f7af1`, with fresh native camera, terrain, explosion,
water, reflection, material and model-edge captures. The same-Modern terrain
control changes only terrain detail; full Classic/Modern comparisons are
labeled separately. Terrain and feature artwork use the actual runtime
synthesis path. Captured PNGs export losslessly, and MP4s copy unchanged.
`data/features.json` owns the six current page chapters; `v5/README.md` and its
separate website-media inventory document reproduction and verification.

## Beta redesign matched captures

`v4/` records engine `ac32756e`: native 960×640 Classic CPU / Modern GPU
explosion and landscape captures at the same 2× camera and committed state.
Modern uses verified real 2× synthesized terrain, lighting and glow, with
production CRT binding and full default presentation controls. Foliage is
explicitly the nearest-doubled fallback. Lossless WebP exports exactly decode
to raw captured pixels. The homepage retains this pair; Features uses v5.
See `v4/README.md` for exact reproduction and assertions.

## Earlier capture studies retained for provenance

- `v2/land/`, engine `9e61946`: approved terrain and foliage without units,
  actual camera zoom to 2× and out to 0.25× across a staged base and opposing
  squads. Camera movies retain fixed locations and activated retail COB poses.
- `v2/effects/`, `9e61946`: approved single-unit shockwave and three burning-tree
  animations, using normal simulation events and paired renderer controls.
- `v3/cpu/`, `774f79c`: four mobile units and one building compare genuine CPU
  rendering with modern GPU SSAA, both Anti-Alias enabled. Lighting compares
  the same paths without distortion; optional GPU + glow adds bloom. Native
  1× crops are enlarged 4× with nearest-neighbour sampling. These compare full
  renderer paths, including their baseline raster/compositing differences.
- `v3/water/`, `774f79c`: empty coast, zero models throughout, and a separate
  tall ARM transport for clearer native reflections. No opacity or model-height
  changes; the ship follows normal movement orders and COB wakes.
- `v3/trails/`, `774f79c`: ARM Hammer and Bulldog movement across a prepared Comet
  Catcher clearing, producing normal footprints, paired tracks and fading.
- `v3/finishes/`, `801c8b2`: one original ARM mobile Annihilator in a staged
  360° rotation, selected after 18 model scouts. Native metal/paint finishes
  and glints toggle together; 320×256 pixel crop, no resampling.
- `v3/wrecks/`, `801c8b2`: actual Stumpy death and successful corpse placement.
  Known birth metadata produces a cooling glow and heat plume. The 13-second
  comparison uses a magnified native 2× crop; other modern effect families are
  disabled. Paired raw pixels match after both treatments expire.

The earlier v2 terrain study offered 4× browser pixel inspection: CSS enlarged
both 2× captures equally with nearest-neighbor sampling. Its label distinguished
inspection from that capture's engine camera zoom. The refreshed page presents
the native images at their natural aspect ratio without this magnification.

Site media lives in `static/images/renderer/`, including v2–v5. The root
`media-manifest.json` inventories the earlier media; v4 and v5 have separate
`website-media.json` inventories of the files they serve. Each capture folder
has its harness, exact commands, controls and validation. Raw frames stay
in the outputs recorded by those manifests. The website build needs
neither a GPU nor retail data. Reproduction needs an isolated engine checkout at
the listed revision and installed content; follow its GPU/headless instructions.

Still images are lossless WebP, with no recolouring or artificial highlights.
Clips use normal-speed H.264 at 30 FPS, fast-start metadata, opt-in muted playback
and native controls. Paired controls preserve playback position; offscreen clips
pause. Camera, effect, material and terrain staging is documented explicitly.

## Earlier capture history

The opening `hero-battle.webp` remains an illustrative live Great Divide benchmark
capture from the initial review. Its original path, crop and hash are recorded
in `initial-review/media-manifest.json`; it is not a toggle pair.

`initial-review/`, `v2/`, and `v3/` preserve earlier source evidence and media.
`data/renderer.json` retains the prior twelve-study page inventory; the active
Features page reads `data/features.json`. The old media is not labeled as a fresh
capture. Retained player and format documentation keeps its substantive content.
