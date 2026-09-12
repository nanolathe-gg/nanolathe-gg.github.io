# Asset provenance

## Brand geometry

The segmented N, assembly squares, avatar frame, ten utility icons, and layout geometry were authored
for Nanolathe. They are distributed under this repository's MIT license.

Palette and font metadata live in `data/brand.json`. The reusable design language,
artwork prompts, and page patterns live in `brand/`. SVG source geometry is in
`scripts/brand.py`; `scripts/export-brand.cjs` exports the raster variants.
The same assets and guides are available in the site's downloadable brand kit.

The wordmark is set in Chakra Petch SemiBold and exported to outlined SVG paths.
The source font is from the [Google Fonts Chakra Petch directory](https://github.com/google/fonts/tree/main/ofl/chakrapetch).
Its SIL Open Font License is included at `static/fonts/OFL.txt`. Both text and
font assets are served locally; the website makes no Google Fonts requests.

## Construction illustration

`static/images/construction.webp` is original conceptual artwork created with
the built-in OpenAI image generation tool on 2026-09-07. It is not a screenshot,
retail asset, or statement of implemented game behavior. The production image
is a WebP encoding of the generated 1536×1024 PNG. No retail references were
supplied to the generator.

Prompt:

> Use case: stylized-concept. Asset type: wide landscape editorial hero image for an open-source real-time strategy engine website, 1536x1024 or larger. Primary request: Original conceptual artwork of a large dark steel robotic construction gantry on a rugged charcoal basalt planetary surface, assembling a compact angular tracked combat machine from a pale green luminous lattice. Scene/backdrop: Dusty rocky basalt ground fading into a moody near-black background. Far left is dark open smoky terrain with generous clean negative space for website copy. Edge areas softly disappear into black. Subject: Dramatic angular industrial gantry, with an arm directing tiny crisp square green nano particles into the unfinished tracked machine. Restrained square particles in seven shades of green; no rounded sparks. Fresh original machine silhouettes and original scene. Style/medium: Elevated isometric-like three-quarter view, evocative of late-1990s pre-rendered real-time strategy art, tactile rendered game aesthetic, highly legible geometry with intricate miniature detail. Sophisticated technical open-source meets vintage RTS, not glossy blockbuster concept art. Composition/framing: Wide landscape. Main machinery occupies the right half and center; keep the left third open and dark. All machinery and the construction process clearly visible in a cohesive scene. Lighting/mood: Restrained lime-green construction light as the sole saturated hue, subtle directional light to clarify angular massing. Color palette: Weathered dark olive and gray metal, charcoal ground, small ivory identification stripes, pale green luminous construction lattice. Materials/textures: Tactile weathered steel, rugged dusty rocks, intricate miniature machine details. Text: None. Constraints: This is original conceptual art, not a game screenshot. No existing Total Annihilation or Cavedog models, logos, or copyrighted artwork. No text, letters, watermark, logos, orange glow, planets in sky, human figures, modern neon sci-fi city, or rounded sparks.

## README illustration and banner

`brand/sources/readme-construction.png` is a new 2048 × 768 original fabrication
scene generated with the built-in image generation tool on 2026-09-07. No retail
image inputs were supplied. It depicts a concept reactor core and fabrication
cradle; it is not an engine screenshot or evidence of an implemented feature.

`static/brand/readme-header.svg` combines that image layer with the existing
outlined wordmark and outlined Chakra Petch lettering. PNG and WebP exports
are provided for embedding. The original master, composition script, and
exports are included in the downloadable kit. The complete prompt and usage
instructions are in [brand/README_HEADER.md](brand/README_HEADER.md).

## Technical content

Engine commands and status were checked against `cmd/nanolathe/flags.go`,
`go.mod`, `README.md`, `docs/DESIGN_SESSIONS_AI_SAVE.md`, and
`docs/DESIGN_GPU_RENDERER.md` in the public engine repository at commit
`dd9cd05` on 2026-09-09. These describe Nanolathe's implementation, not independent
retail evidence. The modern renderer is experimental.

The GAF format page adapts `research/formats/gaf.md` at engine commit
`11ae6adaf16d446f0b4292fb045267a5b784ffb2`. Its complete plain-text source snapshot
is included beside the page; all research links use that pinned revision.
The other 13 format pages also include complete pinned source snapshots;
behavior entries remain a directory of the owning references.

## GAF teaching assets

The files in `content/docs/gaf/` named `pulse-*.svg`, `mask-*.svg`,
`composition-*.svg`, `contact-sheet.svg`, `example.gaf`, `example.json`, and
`example-palette.json` are original MIT-licensed teaching fixtures, authored in
`scripts/gaf-example.py`. They contain no retail art or extracted palette. The
sprite SVGs and offset manifest are generated by decoding the authored binary.
The composition images are schematic illustrations of ordinary child ordering
and clipping, not decoded fixture frames or ALP blend simulations. The worked
RLE row is a separate authored example using the same custom palette.

Run `python3 scripts/gaf-example.py` to regenerate or add `--check` to verify
without writing. Python's standard library is the only dependency.


## 3DO teaching assets

The 3DO guide adapts `research/formats/3do.md` at engine commit
`1ef7b9193452752fca3e8ea75da8c38dfa318268`, with the complete source snapshot in
`content/docs/3do/research-source.txt`. Runtime texture-corner and span-writer
claims also use the rendering specification at that same revision.

`content/docs/3do/example.3do`, `model.json`, `model.svg`, `exploded.svg`, and
`texture.svg` are original MIT-licensed teaching assets, authored by
`scripts/3do-example.py` without retail geometry, textures or palette inputs.
The 3,750-byte crawler contains 5 pieces, 85 vertices and 61 flat-color
primitives. The inspector and model illustrations use geometry independently
decoded from that fixture. Projection, neutral face contrast, depth ordering,
origin markers, selection overlay and exploded separation are explanatory
presentation, not a recreation of retail rasterization. The separate corner
texture is a schematic of UV assignment; the fixture itself has no textures.

Run `python3 scripts/3do-example.py` to regenerate, or use `--check` to validate
committed outputs and signed fixed-point quantization without writing. The
Python standard library is the only authoring dependency; the viewer uses
native WebGL depth testing with Canvas 2D annotations and ships no third-party
rendering library. The static SVG remains available when WebGL is unavailable.

## Additional format teaching assets

PAL, FNT, PCX and WAV adapt their corresponding `research/formats/<slug>.md`
documents at engine commit `c1b934071e15fc3156d9aa92ba91db26368768ac`.
HPI, COB, GUI, TDF, FBI, TNT, OTA and TAD use
`72dcc024de8e6abb3b2f83137a292f566f13b63f`. Each bundle contains the exact pinned
document as `research-source.txt`.

All teaching fixtures, diagrams and audio in these bundles are original,
MIT-licensed assets, generated by `scripts/<slug>-example.py`. They contain no
extracted game art, palettes, scripts, recordings or audio. Schematic diagrams
and isolated reader fixtures are labeled on their pages; they are not claims of
playable game content or retail rendering.

| Format | Original assets and derivation |
| --- | --- |
| PAL | Two 1,024-byte palettes, palette grid and day/night beacon comparison using the same procedural pixel indices. SVG colors come from the authored palette bytes. |
| FNT | A 468-byte font containing space, A and B; diagrams show the decoded continuous bitstream, a deliberately incorrect row-aligned interpretation, and pen advances. |
| PCX | Two calibration images and palettes encoded as PCX. Decoded SVGs compare stored row stride with the retail visible-width walk; the padded example intentionally exposes divergence. |
| WAV | A mathematically synthesized 400 ms chirp in 8-bit and 16-bit RIFF, raw and DIGI containers. The waveform comes from the 8-bit samples. The DIGI reader fixture intentionally leaves unused size fields zero. |
| HPI | Plain and obfuscated stored-file archives, decoded pointer diagram and byte decryption inspector. The required trailing copyright literal is a format marker, not attribution for the original payload. |
| COB | A hand-assembled 110-byte program, illustrative equivalent BOS, decoded manifest and instruction/stack walkthrough. No compiler provenance is claimed. |
| GUI | Authored GUI text, parsed manifest and interactive 640 × 400 panel schematic with original gadget labels. |
| TDF | Original schema snippets and duplicate-key fixture, with parsed insertion states and typed-value comparisons. |
| FBI | Original unit-definition text, decoded yard maps and resource-contract schematic. The linked resource names are illustrative. |
| TNT | Original binary island, procedural tiles and palette, heights, feature words and decoded layer diagrams. The example does not supply the external feature catalog. |
| OTA | Original two-schema text, parsed positions and resource settings over a schematic basin; no paired playable map. |
| TAD | Original 20-byte Smartpak stream, 26-byte match-record wrapper and 29-byte reconstructed stream, with JSON and diagram. These are isolated protocol fragments, not a complete recording. |

Run a generator without arguments to regenerate its assets, or with `--check`
to verify them without writing. `python3 scripts/check-format-examples.py`
checks all completed pages; the same checks run in `make check`.

The COB page also contains three original runtime laboratories: a schematic
turret/beacon, an eight-slot thread display and a signal-mask comparison.
`motion-demo.bos` and `thread-demo.bos` are illustrative source, not claimed
compiler output. `laboratory.json` contains bounded motion and scheduler traces
generated and checked by `scripts/cob-example.py`, using the page's pinned
runtime specification (§4.2, §4.3 and §4.6). They do not interpret arbitrary
scripts or use retail geometry. Playback is an explicitly slowed presentation
of normal delta-1 drains; the diagram uses the positive encoded angle.

## Modern renderer feature captures (2026-09-12 local review)

`static/images/renderer/` contains actual Nanolathe screenshots and silent clips
rendered with the user's original Total Annihilation installation. The user
explicitly requested retail-data scenes for a visual features page, with review
before publication. These are not AI illustrations or retail-executable captures.
The screenshots contain underlying game artwork belonging to its respective
owners; that artwork is not covered by this website's MIT code license. No raw
archives, palettes, models, sprite banks or playable game data are included.

The opening shows a live Great Divide benchmark battle from the initial review.
Approved terrain, camera, shockwave and tree-fire captures remain at `9e61946`.
SSAA, lighting, water, reflection and ground-mark captures use `774f79c`.
The current metal/paint finish and smoldering-wreck examples use `801c8b2`. Their sources and validation evidence are under
`scripts/renderer-capture/v2/` and `v3/`; the root media manifest hashes the
actual files shipped by the page.

SSAA now compares the genuine classic indexed CPU framebuffer with modern GPU
geometry for four mobile units and one building. Lighting compares the same
paths without distortion, with optional bloom. The coast has no units; a separate
tall transport shows reflections. A staged mobile Annihilator rotation shows native metal/paint finishes and
glints. Real ARM Hammer and Bulldog movement lays footprints and tracks. A real
Stumpy corpse shows cooling glow and heat fading over its committed lifetime.
Captions identify staging, normal simulation, controls and renderer differences.

Still images are lossless WebP. Documented native crops and nearest-neighbour
enlargement make small effects readable; no colours or renderer effects are
altered. Terrain's 4× inspection enlarges the original 2× captures in the browser;
it is explicitly separate from engine camera zoom. Silent clips play on request
at normal speed. Superseded media is removed, with earlier capture provenance
retained. No raw playable retail data is included.

Renderer explanations in `data/renderer.json` link to the owning sources at each
capture revision. The gameplay guide in `data/gameplay.json` retains its pinned
`9e61946` sources and is server-rendered both in the features popup and at
`/gameplay/`, providing direct links and a no-JavaScript fallback.
