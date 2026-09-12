# Renderer feature captures

All screenshots and silent clips are actual Nanolathe output using a separate
retail Total
Annihilation installation. No extracted playable game assets are bundled.
Classic CPU examples use Nanolathe's indexed software renderer; none are captures
of the retail executable. Captions identify exact controls and scene staging.

The metallic materials section also has a live WebGL study; `live-materials/`
documents its single-pose display mesh, atlas, shader port, and differences from
the game. The paired in-game material clips remain available below the viewer.

## Current examples and source evidence

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

The approved terrain images also offer 4× browser pixel inspection: CSS enlarges
both 2× captures equally with nearest-neighbour sampling. The control is labelled
separately from engine camera zoom, whose maximum is 2×. No screenshot pixels or
engine zoom limits were changed for this inspection setting.

Site media lives in `static/images/renderer/v2/` and `v3/`. The root
`media-manifest.json` records all shipped sizes and SHA256 hashes. Each capture
folder has its harness, exact commands, controls and validation. Raw frames stay
in the temporary outputs recorded by those manifests. The website build needs
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

`initial-review/`, the unused portions of `v2/`, and `v3/metal/` preserve earlier
source evidence. Superseded screenshots and movies are no longer shipped.
`v3/finishes/` replaces the initial glint-only turntable with current materials.
Consult `data/renderer.json` for the twelve current examples and pinned sources.
