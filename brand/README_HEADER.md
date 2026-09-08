# Nanolathe README header

An original fabrication scene for the engine project's README. The existing
outlined wordmark is placed over a new illustration; no logo lettering is
generated or redrawn.

The tagline is **An open-source 2.5D RTS engine.** Keep the Total Annihilation
relationship in the README's explanatory prose, where the independent engine
and original-data requirement can be stated clearly.

## Use it

Paste this at the top of the engine README:

```markdown
[![Nanolathe — Open-source 2.5D RTS engine](https://nanolathe.gg/brand/readme-header.png)](https://nanolathe.gg/)
```

Or copy `static/brand/readme-header.png` into the engine repository and use a
relative image URL. Keep the introductory prose as ordinary README text.

## Files

- `static/brand/readme-header.png`: 2048 × 768 PNG for GitHub and general use.
- `static/brand/readme-header.webp`: smaller web export.
- `static/brand/readme-header.svg`: editable, self-contained composition with
  an embedded image layer and exact outlined wordmark and secondary lettering.
- `static/images/readme-construction.webp`: illustration layer without text.
- `brand/sources/readme-construction.png`: original generated master.
- `scripts/readme-banner.py`: composition source; requires FontTools only when
  regenerating the SVG. Export the SVG with `scripts/export-brand.cjs`.

The image is original concept artwork, not a game screenshot. Its caption is
part of the composition. The engine introduction provides the accessible
description independently of the image.

## Generation prompt

Created on 2026-09-07 using the built-in image generation tool, with no retail
image inputs. The 2048 × 768 output is preserved as the master. The PNG master
is embedded in the SVG; the supplied vector wordmark and outlined text are
separate layers. The PNG and WebP headers are raster exports of that composition.

```text
Use case: stylized-concept.
Asset type: ultra-wide background illustration for the GitHub README header of Nanolathe, an independent open-source Total Annihilation engine project. Generate a new image, 2048 x 768 pixels, landscape, approximately 8:3.
Primary request: an original miniature industrial fabrication scene with a low circular construction cradle assembling a faceted angular reactor core, late-1990s rendered real-time strategy atmosphere.
Composition: machinery occupies the rightmost 55% of the wide image; the leftmost 42% is very dark quiet charcoal negative space for a large supplied logo that will be placed afterward. One cohesive three-quarter view. Keep the entire central fabrication subject inside the canvas with margin above and below; no tall cropped machine. The left side should feel like the same dark workshop atmosphere, not a flat black rectangle. The construction focal point sits around x=1550 y=390 on the 2048x768 canvas.
Subject: an original squat hexagonal armored reactor housing floating slightly above its industrial cradle, one half solid weathered olive-gray steel with small ivory plates, the other half a crisp pale-green structural wire lattice being assembled. A slim articulated fabrication arm reaches inward from the far right. Its visible tool nozzle emits a tight directed stream of tiny square green assembly particles directly toward the unfinished lattice. Exactly one clear fabrication action. Keep the square particles restrained and their source physically attached to the tool. A few supporting rails and machined cradle details create depth.
Materials and lighting: tactile weathered dark steel, dusty charcoal basalt, restrained fine mechanical detail, subtle haze, a shallow pool of pale construction-green light on the core and cradle. Near-black charcoal #121516; dark steel #1b2021; muted olive-gray materials; green focal light near #b6ef63. Tiny amber #e7b66f equipment indicators as a secondary accent, with no orange firelight. Carefully lit original 3D concept-art quality, precise and readable at small sizes, tangible miniatures rather than glossy cinematic spectacle.
Constraints: this is original concept artwork, not a game screenshot. Invent a fresh original machine silhouette. Do not copy Total Annihilation or Cavedog models, factions, artwork, logos, or interfaces. No tank, no large overhead gantry, no repeat of a tank being built under an arch. No humans, stars, planets, explosions, fire, lens flare, rainbow neon, rounded sparks, fake UI, text, numbers, letters, watermark, or logos. Absolutely no text or logo—the existing Nanolathe vector wordmark will be added afterward. Preserve the broad dark empty region on the left.
```
