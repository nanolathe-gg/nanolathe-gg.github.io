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

## Technical content

Engine commands and status were checked against `cmd/nanolathe/flags.go`,
`go.mod`, `README.md`, and `docs/DESIGN_GPU_RENDERER.md` in the engine checkout
on 2026-09-07. These describe Nanolathe's implementation, not independent retail
evidence. The current renderer is experimental.

Format and behavior entries are a directory of the owning references, not copies
of the research. The directory preserves the split between file-format layouts,
clean-room engine behavior, and Nanolathe implementation design.
