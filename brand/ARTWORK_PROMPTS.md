# Nanolathe artwork prompts

Use these prompts for original brand illustrations. Pair them with the
[brand guide](GUIDE.md); use [page patterns](PAGE_PATTERNS.md) when placing an
image in the website. Bracketed fields are intentional fill-in variables.
Replace every field before generating. The prompts describe authored art
direction, not retail behavior or an implemented engine feature.

## Reusable style block

Append this block to a scene brief:

```text
Nanolathe visual language: original industrial construction imagery, clear
angular machine silhouettes, segmented geometry, and restrained crisp square
assembly particles. Tactile weathered dark steel, dusty charcoal basalt, muted
olive-gray metal, and small ivory identification details. Evoke the miniature,
carefully lit character of late-1990s rendered real-time strategy artwork with
fresh original designs. Precise, readable, and atmospheric.

Keep the scene mostly charcoal, near the website background #121516 and panel
colors #1b2021 / #22292a. Use pale construction green near #b6ef63 as the primary
light and focal accent. Ivory near #edf0e7 clarifies selected details. Amber
#e7b66f is a restrained optional secondary annotation color; do not turn the
scene into orange firelight. Image colors are art-direction targets, not a
request for flat swatches or a guarantee of exact pixel values.

Use directional light to explain geometry, limited haze for depth, and a
legible assembly focal point. Let edges fade into dark quiet space where the
layout needs it. Avoid glossy cinematic spectacle, dense neon trim, rainbow
glows, lens flares, rounded sparks, and distracting background objects.

This is original concept artwork. Invent original machinery and environments;
do not copy Total Annihilation or Cavedog models, retail artwork, faction
symbols, interface elements, or any existing logos. No text, letters, readable
markings, watermark, logo, fake UI, or screenshot treatment. Do not generate
the Nanolathe logo: supplied vector assets and final typography will be placed
afterward. The illustration must not imply that its scene or machinery exists
in the running engine.
```

## Hero scene

Choose the subject and the page copy first. The existing homepage image is
`static/images/construction.webp`, derived from a `1536 × 1024` original. A new
hero should reserve similar copy space; a different aspect ratio or crop needs
layout verification.

```text
Create an original Nanolathe website hero illustration.
Scene: [one sentence describing a fresh construction setting].
Primary subject: [original machine or industrial structure].
Visible action: [one readable assembly action].
Setting details: [two or three material/environment details].
Output: [pixel dimensions and aspect ratio], no text or logo.

Composition: place the primary machinery on the right half and near the
center, with the left third open, dark, and low in detail for live website
copy. Use a three-quarter view that makes the structure and its construction
focal point easy to read. Keep the important silhouette inside a crop-safe
central area; avoid essential details at the extreme edges. Let the lower
and outer edges blend gently into charcoal. Keep the copy area quiet even
when the scene is viewed at a small size.

Provide one coherent scene with one dominant focal point. Use a restrained
green construction lattice and a small directed stream of square particles.
The result is a concept illustration, not a captured game frame.

[Append the reusable style block in full.]
```

For a close sibling of the existing hero, use a fresh construction gantry
assembling an original compact tracked machine on dusty basalt. Keep the
silhouette and composition original. For a different subject, retain the
materials, green focal light, quiet margins, and hierarchy rather than forcing
the same machine into every image.

## Supporting illustration

Use this for a feature panel, article opener, or editorial card. Literal
technical diagrams should be authored from verified documentation in SVG,
HTML/CSS, or another editable format; generated artwork cannot establish a
pipeline or algorithm.

```text
Create an original supporting illustration for Nanolathe.
Editorial theme: [the idea the page discusses].
Visual metaphor: [one original object or assembly arrangement].
Placement: [card, article opener, or feature panel].
Output: [pixel dimensions and aspect ratio].
Composition: [centered object, subject on the left, or subject on the right].
Reserve [location and amount] of quiet space for surrounding layout.

Use one clear industrial form and at most a few secondary elements. Reduce
detail enough that the image reads at [final displayed width] pixels. Give
the object a distinct silhouette with pale green construction light, dark
steel surfaces, and small square assembly particles. Keep the background
quiet and charcoal. No labels, arrows, numbers, UI, logos, or text; those will
be authored separately if needed. This visual metaphor is conceptual and
must not look like engine output or claim a technical implementation.

[Append the reusable style block in full.]
```

## Preserve an image while editing

Attach the original image and specify a narrow change. If a supplied logo is
already composited into a source, retain an unmodified logo layer for final
assembly rather than depending on generation to reproduce it accurately.

```text
Edit the attached original Nanolathe concept illustration.
Change only: [specific object, region, material, lighting, or crop adjustment].
Required result: [plain description of the visible change].

Preserve the image dimensions and composition except where the requested
change explicitly requires otherwise. Preserve the camera angle, original
machine identity, silhouette, scale relationships, construction focal point,
dark copy-safe region, material texture, charcoal palette, and restrained
pale green light. Keep all other objects in their current positions. Do not
introduce extra machinery, new saturated hues, rounded sparks, fake UI,
lettering, watermarks, or logos. Do not reinterpret the whole scene.

Keep this clearly original concept artwork. Do not borrow retail game
artwork or familiar faction symbols. Final typography and Nanolathe vector
assets will be placed afterward.
```

## Finish and verify

1. Inspect the image against the brief: one clear focal point, original
   silhouette, restrained light, usable negative space, and no accidental
   lettering or logos. Fix visible defects before publishing.
2. Preserve a source master. Export a web derivative in an appropriate format;
   the current hero uses WebP. Record the source, date, tool, prompt, edits,
   dimensions, and output path in `ASSETS.md`.
3. Add supplied logos and live typography in the layout or a separate design
   layer. Check that the final logo colors are exact and its clear space is
   intact. Do not ask an image generator to reproduce outlined wordmarks.
4. Caption concept art as **Original concept artwork**. Keep engine screenshots
   separately identified with their capture context. Never describe generated
   artwork as a screenshot, benchmark, retail evidence, or proof of a feature.
5. Inspect the image in its actual page at `320`, `390`, `768`, `1440`, and
   `1920px` viewport widths. Check both the subject crop and text contrast.
   If the hero changes, update any decorative particle emitter alignment in
   `assets/js/site.js`; it is tied to the current illustration's geometry.

The original homepage prompt and provenance are available in
[`ASSETS.md`](../ASSETS.md). The artwork brief can evolve; the distinction
between a designed illustration and observed engine output stays explicit.
