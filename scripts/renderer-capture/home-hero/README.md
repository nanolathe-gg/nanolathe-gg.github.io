# Homepage hero: ARM base and battle

The hero is a native modern GPU capture from production engine
`e2ac78cda2a19ff77fb8ee04a6ed32fc8f2e8819`. The isolated local branch is
`capture/homepage-modern-hero`; final capture-only fixture/diagnostics are saved
at `02f9fa6b416542b23d1ae9071751663d5d00bb83`. The attached patch adds only the
explicitly selected staging fixture and read-only capture evidence. Production
renderer, shaders, simulation rules, coefficients and defaults are unchanged.

## Composition

A smaller ARM base defends against CORE units on Greenhaven, seed 7:

- Original ARM Kbot Lab, solar plant, radar and light laser tower.
- Commander, Bulldog, Stumpy, Flash and Zeus, with space between silhouettes.
- Original CORE Raider, Leveler, Reaper and Storm across the front.
- Normal factory production supplies the green construction effect and an
  actual produced unit. One original ARM fighter follows ordinary patrol orders;
  its visibility depends on the simulation moment and camera.

No Maverick is staged. The capture-only `NANOLATHE_HERO_COMPOSITION=base` selector
uses the layout in `hero_capture_scene.go`, overriding the standard film roster,
formation and extra-unit fields. Map, anchor, seed, lead-in ticks, reveal and
camera still use the production film controls. Placement searches honor each
original unit's terrain class and add spacing. Exact accepted coordinates are
in `manifest.json` and `capture.log`.

The fixture stages 14 units and prepares nine small destructible-feature
clearings around their footprints through the feature lifecycle, removing
successors too. This makes the base and silhouettes readable; it is scene
staging, not a claim that units automatically clear trees during gameplay.
Indestructible map features, including deposits, remain. Surrounding original
healthy trees stay in place and use real synthesized sprites. The captured
census contains zero burning features; no tree artwork is substituted.

The ordinary Session runs combat, COB scripts, construction and effects. After
150 lead-in ticks, the film publishes tick 151 and records frame 0 at fraction
0 in the 150–151 presentation interval. The census/state hash describe current
publication 151; interpolation can sample the prior pose. The camera is 2×,
centered at `(4280,4230)` plus `(0,-75)`.

## Native rendering and export

Actual Metal, AA, enhanced rendering, interpolation, feature/unit shadows, all
modern effects and normal 100% strengths are enabled by the production film
route. The input-keyed synthesis cache supplies 2347 real 64×64 terrain tiles;
the recorded drawlist uses 38 synthesized feature-sprite commands. Shadow and
missing sprite variants retain the ordinary fallback. Actual execution records
14 model subjects, 16 battle lights, 4 ground-light discs and 5 glow passes.
Full statistics, source/binary hashes and controls are in `manifest.json`.

The production clean-film crop copies the native 1280×880 world viewport from
surface 1408×944 at `(128,32)`, removing interface chrome; messages are silenced.
There is no additional crop, resampling, retouching or compositing.
`hero-modern-base-e2ac78cd.webp` exactly matches the captured PNG's decoded RGBA:
`c32eeb071060fffe08f2bc8cd12728c3f2ebd4535dbce27ea0f9b34fcbd41342`.
The raw PNG remains in the task's `capture-home-hero/base-final-150/` directory.
The responsive image crop is anchored right so narrow screens retain the base.

The previous crowded hero and its metadata remain in Git history at website
commit `98f5529` and in the task's capture directory. Its unused served image
has been retired. The initial review hero's provenance remains in
`../initial-review/media-manifest.json`.

## Reproduce locally

Use an isolated engine checkout at the production revision, apply
`capture-diagnostics.patch`, and read the engine's `AGENTS.md`,
`docs/FILM_CAPTURE.md` and installed Ebitengine headless-running skill. A macOS
display context is needed even though the film hides its window.

```sh
GOCACHE=/tmp/nanolathe-capture-gocache GOMAXPROCS=2 \
  go build -p 2 -o /tmp/nanolathe-home-hero ./cmd/nanolathe
caffeinate -u -t 60 &
XDG_CACHE_HOME=/tmp/nanolathe-home-hero-cache \
XDG_CONFIG_HOME=/tmp/nanolathe-home-hero-config \
EBITENGINE_GRAPHICS_LIBRARY=metal \
NANOLATHE_HERO_COMPOSITION=base \
  /tmp/nanolathe-home-hero \
  --root "$HOME/TotalAnnihilation" --renderer modern --auto-remaster=true \
  --film /path/to/website/scripts/renderer-capture/home-hero/hero.json \
  --film-out /tmp/nanolathe-home-hero-frames --film-frames 1
cwebp -lossless -exact -q 100 -m 6 \
  /tmp/nanolathe-home-hero-frames/frame000000.png \
  -o hero-modern-base-e2ac78cd.webp
```

The cache is optional; a fresh loader synthesizes the same installed art. The
producer was built before its source-only commit and stamps prior diagnostic
revision `25e956d1` with `modified=true`; its recorded binary/source hashes
identify the exact producer. No retail archives, caches, binaries or raw
sequences enter the website repository or a deliverable bundle.

## Local verification

Native output and desktop/mobile screenshots were inspected. Five homepage
widths (320, 390, 768, 1024 and 1440) pass image dimensions/served hashes, eager
loading, overflow, image completeness, direct demo CTA and home comparison
mouse/touch/keyboard checks. `browser-verification.json` records the results;
review screenshots are in the sibling local `../qa/` directory.

Strict Hugo build and all 30-page internal destination/asset checks pass after
this refresh. The preceding hero update passed full `make check`; PowerShell
was unavailable for Windows-specific offline tests. Capture diagnostic build
and `go vet ./cmd/nanolathe` pass. Physical Safari/mobile tests were not repeated.
The preview remains `http://127.0.0.1:1313/`. Nothing is pushed or published.
