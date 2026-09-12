# Live browser material study

The features page's metallic materials section renders one frozen ARM mobile
Annihilator in WebGL. This is a browser adaptation, not an engine/Wasm build or a
scrubbed video. The existing paired engine clips remain in a disclosure below it.
Nothing is published by the capture or site build.

## Source and scope

Engine revision `801c8b28c38ff6505b4939d96cce7fcf22200da5`, matching the retained
`v3/finishes` comparison. The export uses the same Create/Activate COB pose helper
(300 ticks before and after activation), blue owner color zero, the compiled
model hierarchy, normal primitive dispatch, resolved texture frames, geometric
normals, and `modelTextureMaterial` annotations. No shader, gait, or simulation
behavior changes are required. The extra client helper is export-only code in
an isolated worktree; it is not part of the production engine.

`static/models/materials/` contains a flattened, single-pose presentation mesh
and a padded RGBA atlas for this one subject. No 3DO, GAF, COB, unit definition,
or game archives are shipped. These derived display assets contain original
Total Annihilation artwork and are not covered by the website's MIT code license.
They contain no hierarchy, script, or animation data for gameplay.

`assets/js/material-viewer.js` ports the arithmetic in
`internal/platform/gpurender/metal_glint.go` and `model_finish.go`:

- Default half vector `(-0.35, -0.15, 0.9246621)` in world X/Z/height axes,
  permuted to X/height/Z for the browser. Normals turn with the unit. The optional
  light orbit rotates this vector around the vertical axis; zero restores the
  exact engine direction. This adjustable direction is a browser study control,
  not an in-game moving light. The projected shadow follows the same direction.
- Power-32 glint, rounded to eight bits; the neutral-color mask applies to all
  faces, before the curated finish, matching `model_direct.go`'s shader order.
- Metal's cool power-four lobe and weaker paint response retain the same
  coefficients, with directional response quantized to three bits.
- The selected mobile unit uses its unshaded palette artwork as the baseline.

WebGL uses continuous orthographic projection, triangle depth testing, nearest
atlas sampling, browser antialiasing and a simple projected shadow on a neutral
backdrop. It does not reproduce the engine's sheared integer projection,
quad rasterization, height-key composition, SSAA resolve, or terrain. The
page describes those differences in “About this example.” The frozen mesh
is only rotated around its vertical axis; vertical dragging adjusts the camera.

The viewer loads its ~63 KB mesh/atlas near the viewport, draws on demand, and
animates only after the user requests it. Rotate unit and Orbit light are
mutually exclusive so one variable moves at a time. Finish switches, manual
controls, offscreen/document-hidden views, and context loss stop both modes.
Reset restores the original unit, camera, and light direction. Pointer capture handles drags; keyboard arrows, labeled range inputs,
and reset provide alternatives. Context loss restores the existing controls and
angle when possible; failed loading/WebGL leaves the original poster and clip.

## Reproduce

Use an isolated engine checkout at the revision above. Copy `export_client.go`
into `internal/client/material_preview_export.go`. Copy `main.go` and
`../v3/finishes/pose.go` into `.export-materials/`.

```sh
GOCACHE=/private/tmp/nanolathe-feature-v3-capture-cache GOMAXPROCS=2 go build -p=2 -o /private/tmp/nanolathe-material-export ./.export-materials
GOMAXPROCS=2 /private/tmp/nanolathe-material-export --root /Users/daniel/TotalAnnihilation --out /private/tmp/nanolathe-material-preview
```

Then from the website checkout, with Python and Pillow installed:

```sh
python3 scripts/renderer-capture/live-materials/package.py
```

The exporter performs no GPU readbacks. It reads normal compiled presentation
geometry and resolved texture pixels, then reverses triangle winding when
mirroring model Z into world Z. Padding and half-texel UVs avoid atlas seams.
`manifest.json` records the source hash, bounds-independent counts, output hashes
and sizes. Raw export textures stay in the temporary directory. The website
build requires neither retail data, Go, nor Pillow.

API references: [pointer capture](https://developer.mozilla.org/en-US/docs/Web/API/Element/setPointerCapture),
[WebGL guidance](https://developer.mozilla.org/en-US/docs/Web/API/WebGL_API/WebGL_best_practices).
