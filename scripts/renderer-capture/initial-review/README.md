# Features page capture sources

The features page is an unpublished local review until the user approves publication.
It uses real Nanolathe rendering of an independently installed retail game.
These screenshots are presentation evidence, not redistributable game data or
captures of the retail executable.

## Fresh staged tableau

`main.go` is a diagnostic driver; `detail_art.go` copies the production detail-art
loader at renderer revision `72dcc024de8e6abb3b2f83137a292f566f13b63f`.
Neither changes the engine's renderer. `manifest.json` records the original
capture settings, controls, image hashes, staged unit roster, and pixel checks.
All scene positions, headings, visibility and explosion placement are prescribed;
unit geometry, terrain, tree sprites and activated COB poses use real assets.
The overview deliberately spreads the same roster to explain the icon vocabulary.

To reproduce, create an isolated engine worktree at that revision, copy these two
Go files into a `.featurecapture` directory inside it, then run from that worktree:

```sh
go build -o /tmp/nanolathe-feature-capture ./.featurecapture
/tmp/nanolathe-feature-capture -root /path/to/TotalAnnihilation \
  -map 'Great Divide' -out /tmp/nanolathe-feature-main-media -remaster
```

A working GPU/display environment is required even though the capture window is
hidden. Follow the engine's Ebitengine headless instructions for the host.
The website build does not run this driver or require retail data.

## Existing reviewed captures

`media-manifest.json` records original local source paths, exact crops, output
SHA256 values, and renderer revisions. Those paths are provenance for this authoring
session, not build dependencies. Original PNGs remain outside this repository.

- **Heat:** `tree-heat-{before,after}-modern/battle.png`, Great Divide, seed 7,
  native zoom, final tick 540. Full scene metadata and all per-frame censuses
  match. Initial heat prototype `0c2c1d7`, based on `72dcc02`. The separate live
  clip is three seconds at 30 fps, from `nanolathe-tree-heat-preview.mp4`; crop
  x=480, y=120, width=720, height=640. No retiming. Later shared-pass integration
  deliberately changes overlap priority where blast distortion meets heat.
- **Water:** `nanolathe-coastal-v5-timed/coast-2x-t140-{before,after}.png`,
  reviewed coastal v5 tuning on Coast to Coast, staged ARMPT/CORPT/ARMSH/ARMTIDE.
  `water-shore-v5.mp4` is the reviewed motion comparison, left off and right on,
  with normal tick timing and a deliberate wind reversal. Unit movement is
  prescribed; original COB wake emission is not simulated by this driver.
  Integrated design is documented at `c4b61e6`, GPU design §26.
- **Reflections:** `nanolathe-reflections-25-visual/coast-2x-t140-{before,after}.png`,
  same coastal tableau, matched tick and all other coastal effects enabled.
  `6b5a99d` includes corrected hull direction and 25% reflection opacity.
- **Metal glints:** `glint-{off,on}-native-1/battle.png`, matching Great Divide
  benchmark tick 450. Crop x=400, y=300, width=640, height=640. Renderer control
  `SetMetalGlint` toggles the highlight. Integrated implementation: `72dcc02`.
- **Opening image:** `nanolathe-lighting-detail-after/battle.png`, Great Divide,
  seed 7, 2× benchmark view, crop x=160, y=100, width=1280, height=880. This is
  an illustrative live battle capture from lighting review, not a toggle pair.

Images are lossless WebP encoded with `cwebp -lossless`; no colours or renderer
effects were edited. Specified crops remove UI or focus the example. Videos are
silent H.264 with normal-speed playback. The water clip is copied unchanged;
heat is cropped and encoded at CRF 18, yuv420p, with fast-start metadata.

For a new capture, update source evidence, compare matching states, visually inspect
both sides, regenerate the lossless image, and update the manifests and ASSETS.md.
Never label an effects-off modern frame as a screenshot of retail TA.

For the SSAA example, the final website uses a 360 × 240 crop at x=420, y=395
with CSS nearest-neighbour enlargement so browser smoothing cannot hide the
edge-coverage comparison. The original uncropped PNG hashes remain in
`manifest.json`; final WebP hashes and crops are in `media-manifest.json`.
Identical enabled-state images share a URL: zoom reuses `remaster-on.webp`, and
bloom/distortion reuse `lighting-on.webp`. This avoids redundant transfers while
retaining separate, accurately controlled before images.
