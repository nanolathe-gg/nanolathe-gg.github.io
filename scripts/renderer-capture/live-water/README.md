# Live water study

This is a WebGL browser adaptation, using a frozen, activated
ARM transport (`armtship`) and submarine (`armsub`), original palette textures,
a native terrain view and the engine's actual projected shoreline field. It is
not a game simulation or a replacement for the native renderer.

Engine source: `617540c587e1b75d6d8ba7bf5243d24bea3f3bc2`. The isolated diagnostic
worktree is `../nanolathe-features-v6`, branch `capture/features-feedback-v6`.
The export uses actual Metal at committed tick31, Gods of War, camera `(2479,517)`
and native960×640 at2×. Transport world `(2739,55,649)`, submarine `(2809,0,769)`;
both heading49152. No movement orders are issued for this frozen export. Pose
pieces come from the real committed publication after the original COB scripts
activate. SHA-256 and a before/after publication check identify the producer.

The helper exports the unchanged CPU water mask (coverage, inward coast distance,
dry/void gate and damp ring). Its alpha lane is split into a separate opaque PNG
so browser image decoding cannot destroy channels under zero alpha. Meshes retain
original geometry, the visible projected faces, original UVs and palette colors;
an additional atlas uses the engine's actual Blue table for submerged hulls.
The first SHD row is baked per face. Padding repeats edge texels without changing
the original texels. These two flattened poses/atlases are display derivatives;
no retail archive, full unit/script bundle or terrain cache is distributed.

`assets/js/water-viewer.js` adapts `water_field.go`, `water.go`, `underwater.go` and
`water_reflections.go`. It retains the field/shore/depth math, native surface and
foam strengths, half-strength hull refraction, reflection ripple, tint and25%
opacity. The sampled wind direction, energy and tidal rate remain fixed; there
is no authoritative time, evolving wind, movement or COB wake simulation here.
Browser triangle/depth rasterization, flat SHD baking, linear resolve and reflected
mesh occlusion/height fading differ from the native height-key screen-space
pipeline. Models are rasterized once at2× output dimensions, then reused while
water animates. Original pixels/geometry are never replaced with generated art.

Surface shading, motion/refraction, shoreline foam and reflections are independent
switches. Water animates continuously when in view; offscreen/hidden tabs suspend
rendering and phase advancement. It starts paused for reduced-motion preferences.
Users can pause, inspect a phase, change effects or reset. The inspection range
expands with elapsed time so animation has no discontinuous loop reset. Context
loss preserves a native poster/recording fallback; restoration rebuilds the scene.
JavaScript/WebGL/asset failures also retain the native poster and one optional
real engine recording. The recording includes ordinary movement, real COB wakes
and evolving session wind; its v6 provenance remains separate.

## Reproduce

In an isolated checkout of the pinned engine, copy v6 source into
`cmd/website-features-capture/`. Add `source/client_export.go` as
`internal/client/website_water_export.go`, `source/mask_export.go` as
`internal/platform/gpurender/website_water_export.go`, and replace only the
capture command's `water/main.go` with `source/main.go`. Build and run on a logged-in
Mac with installed retail data:

```sh
go build -o /tmp/nanolathe-water-study ./cmd/website-features-capture/water
EBITENGINE_GRAPHICS_LIBRARY=metal caffeinate -u -t 60 /tmp/nanolathe-water-study \
  -scene fleet -map 'Gods of War' -frames 1 -move=false -export-study -out /absolute/output
python3 scripts/renderer-capture/live-water/package.py /absolute/output/study
cwebp -lossless -exact -z 6 /absolute/output/on-0000.png -o static/models/water/poster.webp
```

`manifest.json` holds source/binary/shader and served-file hashes, mesh face counts,
atlas sizes and native-poster pixel proof. Raw outputs stay outside the website
at `../capture-water-study/`. Do not land the diagnostic export helpers into engine
main as part of this website task.

The final isolated diagnostic sources are saved locally at
`6c0cfd983f2d082b69fbdda0027811432a07a10f`; binary/source hashes identify the exact pre-commit builds.
