# Reddit showcase button

Send `static/brand/reddit-button-288x32.png` to the moderator and use
https://nanolathe.gg/ as its destination. It is an opaque, exactly 288 × 32 PNG.

The 576 × 64 PNG is an optional double-density export; the requested upload is
the 288 × 32 file. `static/brand/reddit-button.svg` is a self-contained editable
composition containing the artwork and the original outlined logo and wordmark.

## Artwork and composition

Original concept artwork generated on 2026-09-26 (America/Los_Angeles) with the
built-in OpenAI image generation tool, using
`static/images/construction.webp` as a style reference. It is not an engine
screenshot or retail artwork. The unmodified generated master is
`brand/sources/reddit-button-construction.png` (1881 × 836).

The composition crops the master to a 9:1 strip at (0, 310), 1881 × 209 pixels,
adds a charcoal gradient behind the logo, places the supplied brand geometry
without redrawing or stretching it, and adds a subtle one-pixel frame. The
description in the SVG identifies the background as original concept artwork.
No new typography or generated lettering is used.

Rebuild with Node.js and the optional Sharp authoring dependency:

```sh
node scripts/reddit-button.cjs
```

The exports were visually inspected at 288 × 32 and 576 × 64. The composition
script checks their exact dimensions and opaque PNG output.

## Generation prompt

```text
Use case: ads-marketing.
Asset type: original background illustration for a tiny Nanolathe Reddit sidebar button, final displayed dimensions exactly 288 by 32 pixels (9:1 aspect ratio).
Input image: the supplied website hero is a STYLE REFERENCE only. Make a fresh composition designed for a very shallow banner.
Generate a single panoramic image, ideally 2304 by 256 pixels, with edge-to-edge artwork and NO mockup, surrounding page, text, letters, logo, border, watermark, or typography.
Composition: left 64 percent is very dark quiet charcoal #121516, with barely visible basalt dust and faint industrial texture, reserved for a supplied logo added afterward. All recognizable machinery and construction action live in the right 34 percent. Near the far right edge, a close-up original angular weathered dark steel robotic construction nozzle points diagonally down-left toward the center-right. It emits an energetic yet restrained widening spray of small luminous lime-green SQUARE nano particles, flowing leftward through the right third. Make the spray clearly visible at 32 pixels tall, with several bold square particles and a pale green core; let a few tiny particles drift toward the center but keep the left 60 percent quiet and free of bright shapes. Keep the green spray within the central vertical band. Crop into machinery boldly to suit the thin strip, rather than shrinking an entire scene into it. Show a hint of green wireframe assembly along the bottom right.
Style: match the reference's tactile miniature late-1990s rendered RTS industrial construction art, muted olive-gray machinery, dusty dark steel, angular forms, restrained pale construction green #b6ef63, and dark charcoal background. Use directional light to clarify the nozzle silhouette and green reflected light on metal. No rounded sparks, orange firelight, colorful neon, glossy lens flares, generic abstract swooshes, or bright fog across the text area.
This is original concept artwork. No retail game models, faction symbols, copied game assets, or existing logos. Strong readable visual masses suitable for severe downscaling.
```
