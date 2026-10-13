# Nanolathe brand guide

Nanolathe's identity is a machine being assembled: a segmented N, small square
particles, precise type, and a restrained construction green. The website pairs
that industrial character with clear editorial layouts and readable technical
content. Give the work room to breathe; let structure and a few bright details
carry the identity.

This is an authored design system for Nanolathe, not a specification of Total
Annihilation's visuals or behavior. **Current implementation** below describes
the website's source. **Authoring guidelines** are recommendations for making
new work consistent with it.

Start with [artwork prompts](ARTWORK_PROMPTS.md) for illustrations or
[page patterns](PAGE_PATTERNS.md) for Hugo pages. Paths in this guide are relative
to the website repository root unless they are clickable relative links.

## Positioning and naming

Lead with **Nanolathe — an open-source 2.5D RTS engine**. Describe it as an
independent engine written in Go, with Total Annihilation as its current
compatibility focus. The shared tagline and short description live in
`data/brand.json` under `positioning`.

Use the Nanolathe wordmark on banners, avatars, and other identity assets.
The banner tagline is **An open-source 2.5D RTS engine.** Use Total Annihilation
in factual prose about the reimplementation, research, file formats, and
required original game data. Keep that relationship clear; avoid titles or
slogans that suggest an official game release, remake, or endorsement. Do not
promise support for other games or imply a finished general-purpose toolkit.

For discovery, write specific page titles and visible explanations that use the
game name naturally. Keep search metadata consistent with the page. Preserve
the independent-project statement and the separate game-data requirement.
These are editorial guidelines, not a legal clearance opinion.

## Writing voice

Use Daniel's project documentation as the reference: a programmer explaining
something he built and helping you try it. The tone is friendly, specific and
comfortable with technical detail. Explain what happens and why it matters;
then give the reader something to try or a useful example. Nanolathe also has
the perspective of a longtime TA player, grounded in the experience described
on the About page.

The homepage's signed project note and About page use Daniel's first person.
Elsewhere, address the reader directly or describe what the engine does. Do not
invent memories, quotations, team members, promises or a fictional spokesperson.
Keep the disclosure about AI's role in development direct and factual.

- Give headings a subject: “Explosions light nearby units,” “Setup help,” or
  “Why Go?” Avoid pairs of slogans such as “Get closer. See the whole battle.”
- Let each paragraph add information. If a label, heading and first sentence
  repeat the same thought, cut one or two of them.
- Use concrete details: a Jeffy exploding beside a Bulldog, the scripts that
  open factory doors, the game files an installation needs. Avoid vague claims
  about a new chapter, a richer experience or limitless possibilities.
- Use contractions and ordinary sentences. Vary their length where the subject
  calls for it. Do not manufacture informality with typos or forced jokes.
- Give explanations room. Daniel's documentation often follows a short
  introduction with a longer explanation and an example. Do not reduce every
  paragraph to clipped declarations or insist that every section be the same
  size.
- Address practical questions with “you can,” “if you,” and “for example” when
  they fit. A parenthetical should add useful context, such as a platform
  difference or a concrete requirement. Use these habits naturally, not as a
  set of phrases to insert everywhere.
- A little enthusiasm is fine when there is something specific to be pleased
  about. Keep invitations useful: say which control to try and what it shows.
  Do not add a congratulation, joke or exclamation mark to every interaction.
- Number ordered instructions, reference sections and measured values. Do not
  add decorative 01/02/03 labels to unrelated features.
- Use cards for items people need to compare or select. Prefer prose, lists and
  figures for explanations. A section does not need an eyebrow or a call to
  action by default.
- State limitations near the relevant feature. Keep original game assets,
  native engine captures and interactive browser studies clearly distinguished.
- Keep technical terms when they carry information. Explain them in introductory
  copy; retain precise identifiers and evidence in reference material.

After a rewrite, read the rendered headings in order, then the paragraphs. Look
for repeated sentence openings, redundant summaries, unsupported superlatives,
stock invitations (“look under the hood,” “make it your own”), and slogans that
could belong to any software project. Review those patterns in context rather
than treating a punctuation mark or an ordinary three-item list as a defect.
Check the small-screen layout after shortening text.

### Writing references

The October 2026 review compared current project docs with older samples so
recent marketing changes would not be the only reference. These repositories
have multiple contributors; the patterns are editorial guidance, not a claim
that every sentence was written by Daniel.

- [Huma README, September 2022](https://github.com/danielgtaylor/huma/blob/2d1984f84fc0e535404e7dc79435bf066c9f64b6/README.md):
  runnable examples, explanations of defaults, informal tips and caveats close
  to the feature they qualify.
- [Restish guide, May 2022](https://github.com/rest-sh/restish/blob/204e653bc7b81bb0b94d3018c9e9d4899c6a569c/docs/guide.md):
  direct instructions followed by an explanation of the result, real commands,
  platform asides and an occasional enthusiastic aside.
- [API Sprout README](https://github.com/danielgtaylor/apisprout#readme):
  compact feature descriptions with concrete examples and a straightforward
  invitation to contribute.
- [Huma's first API tutorial](https://huma.rocks/tutorial/your-first-api/):
  a worked example that explains each new concept when the reader needs it.

## Color

**Current implementation:**
[`data/brand.json`](../data/brand.json) is the source for palette and font
values; [`assets/css/tokens.css`](../assets/css/tokens.css) renders them for
the site. Layout and component rules live in
[`assets/css/site.css`](../assets/css/site.css).

| Token | Hex | Role |
| --- | --- | --- |
| `--bg` | `#121516` | Charcoal page background |
| `--surface` | `#1b2021` | Section and panel background |
| `--surface-raised` | `#22292a` | Raised surface token |
| `--line` | `#343d3d` | Dividers and panel borders |
| `--text` | `#edf0e7` | Main text and dark-background wordmark lettering |
| `--muted` | `#a8b09e` | Body copy and secondary text |
| `--dim` | `#78836e` | Subordinate labels and details |
| `--green` | `#b6ef63` | Primary actions, links, mark, selected emphasis |
| `--green-dark` | `#27381b` | Dark green support token |
| `--amber` | `#e7b66f` | Eyebrows, secondary actions, supporting labels |
| `--amber-dark` | `#33281c` | Dark amber support surface |
| `--amber-line` | `#715637` | Amber borders and diagrams |

The primary button uses `#192510` lettering and a `#d0ff8c` hover fill. Secondary
buttons use a translucent `#252018b3` fill. Use existing classes to retain these
states instead of recreating them with similar colors.

Dark avatar/favicon backgrounds use `--bg`; avatar framing lines use
`--amber-line`. Light avatar backgrounds use `#f1f0e8`, and the light-background
wordmark uses `#17210f` lettering with `#4c771d` geometry. White variants use
`#ffffff`. These export colors are deliberate adaptations for their backgrounds.

**Authoring guidelines:** keep most of the canvas charcoal and quiet. Green is
the primary signal; amber gives secondary actions and annotations a distinct
role. Use ivory for major text. Do not make every element glow or apply both
accent colors equally to every component. Check text contrast in its actual
size and background; a palette token alone does not guarantee legibility.

## Typography

| Role | Current family and weight | Use |
| --- | --- | --- |
| Display | Chakra Petch SemiBold, `600`; CSS alias `Chakra` | Headings and the live-text site name |
| Reading | Arial, Helvetica, sans-serif; normal body weight, `600` for buttons | Paragraphs and navigation |
| Technical | SFMono-Regular, Consolas, Liberation Mono, monospace | Commands, code, small uppercase labels |
| Wordmark | Chakra Petch SemiBold converted to paths | Use the supplied SVG rather than typing a substitute |

The bundled font is
[`static/fonts/chakra-petch-semibold.ttf`](../static/fonts/chakra-petch-semibold.ttf),
from the [Google Fonts Chakra Petch directory](https://github.com/google/fonts/tree/main/ofl/chakrapetch).
The font's copyright identifies the Chakra Petch Project Authors. Its SIL Open
Font License 1.1 is included in
[`static/fonts/OFL.txt`](../static/fonts/OFL.txt); retain it when redistributing
the font. Website code and original brand geometry use the repository's
[MIT license](../LICENSE). The website serves the font locally.

Headings use tight tracking and a `1.12` line height; body text starts at `16px`
with a `1.65` line height. The homepage title has its own larger, tighter scale.
Use the CSS typography rules rather than forcing the hero scale onto ordinary
pages. Keep uppercase monospace for short labels, not paragraphs. Write the
project name **Nanolathe** in prose; the visual wordmark is lowercase
**nanolathe**.

## Marks, wordmarks, avatars, and icons

The geometric N has separated construction segments and three assembly
particles. Keep its gaps, proportions, and particles intact. The source geometry
and outlined lettering are generated by
[`scripts/brand.py`](../scripts/brand.py).

| Existing file | Use |
| --- | --- |
| [`static/brand/mark.svg`](../static/brand/mark.svg) | Transparent green standalone mark |
| [`static/brand/wordmark.svg`](../static/brand/wordmark.svg) | Green mark with ivory lettering on a dark background |
| [`static/brand/wordmark-light.svg`](../static/brand/wordmark-light.svg) | Dark lettering and deep green mark on a light background |
| [`static/brand/wordmark.png`](../static/brand/wordmark.png) | Transparent raster export for tools that require PNG |
| [`static/brand/wordmark-light.png`](../static/brand/wordmark-light.png) | Light-background raster wordmark |
| [`static/brand/avatar.svg`](../static/brand/avatar.svg), [`avatar.png`](../static/brand/avatar.png) | Framed square identity; the PNG is 512 × 512 |
| [`static/brand/favicon.svg`](../static/brand/favicon.svg), [`favicon-32.png`](../static/brand/favicon-32.png) | Browser icons |
| [`static/brand/apple-touch-icon.png`](../static/brand/apple-touch-icon.png) | Apple touch icon |
| `static/brand/wordmark-white.svg`, `wordmark-dark.svg` | Monochrome wordmarks, with matching PNG exports |
| `static/brand/mark-white.svg`, `mark-dark.svg` | Monochrome marks, with matching PNG exports |
| `static/brand/mark-outline.svg` | Outline mark for larger secondary applications |
| `static/brand/avatar-light.svg`, `avatar-light.png` | Square identity on an ivory background |
| `static/brand/avatar-1024.png` | Larger profile image |
| `static/brand/favicon.ico`, `favicon-16.png`, `favicon-48.png` | Additional browser icon sizes |
| `static/brand/icons/*.svg` | Ten matching utility icons |

Prefer SVG for layout and print work. The wordmark lettering is outlined, so a
recipient does not need to install the font. Use the supplied export for its
intended background. Choose additional monochrome variants, avatars, or the
outline monogram by their intended role. Preserve the supplied
geometry; do not imitate a variant by adding effects to a raster file.

**Authoring guidelines for placement:**

- Reserve clear space of at least one quarter of the visible mark height on
  every side of a mark or wordmark. Measure from visible artwork, including the
  particles, rather than from the outer SVG canvas.
- At normal screen density, use the standalone filled mark at `24px` or larger
  and the full wordmark at `180px` wide or larger. Use an outline-only mark at
  `32px` or larger and inspect its gaps. These are recommended authoring minima;
  dedicated favicon exports are the small-size exception.
- Use the complete square avatar for account/profile images; preview the
  platform's circular crop so the N and particles remain intact.
- Preserve aspect ratio and orientation. Do not stretch, rotate, crop particles,
  close gaps, add bevels or shadows, or replace the lettering with a near-match.
- Place logos on a quiet, contrasting area. On busy artwork, give the logo a
  solid backing or move it into the surrounding page layout. Place the final
  logo asset after generating artwork.

The current arrow partial uses a `24 × 24` SVG viewBox, `1.6` stroke,
`currentColor`, and no fill. Use that as the construction convention for new
utility icons: simple angular geometry, consistent optical scale, and the same
stroke weight. Use supplied icons when available. The logo is a distinct asset;
do not redraw it as a generic utility icon. Decorative icons are hidden from
assistive technology; an icon-only action needs an accessible name.

## Composition and illustration

**Current implementation:** the site uses a centered content width capped at
`1280px`, thin rules, large headings, prose and interactive figures. Rectangular
panels group controls and selectable assets; monospace labels identify technical
details. Green and amber diagrams use restrained grids
and a few geometric elements. See [page patterns](PAGE_PATTERNS.md) for exact
spacing and responsive behavior.

**Authoring guidelines:** use an asymmetrical hero with readable copy on the
left and machinery on the right. Illustration materials are weathered dark
steel, dusty basalt, muted olive-gray metal, and small ivory details. Pale green
construction light and crisp square particles provide the focus. Amber belongs
mainly in surrounding labels and diagrams. Aim for the tangible miniature
character of late-1990s rendered strategy artwork, with original silhouettes
and a clear composition.

[`static/images/construction.webp`](../static/images/construction.webp) is
original generated concept artwork, not a game screenshot or proof of an
implemented feature. Its provenance and original prompt are recorded in
[`ASSETS.md`](../ASSETS.md). New images need the same clear distinction. Label
concept illustrations **Original concept artwork**. Only call an image a
screenshot when it is an actual capture; record the build and scene behind any
implementation claim. Do not include retail game artwork or copied logos in
new brand assets.

## Quick use

**For humans:** choose the correct logo variant, use the palette and font roles
above, start with an existing page or artwork prompt, and inspect the result at
its final size. Record new asset provenance in `ASSETS.md`.

**For agents:** read this guide and the relevant sibling guide first, then
inspect the current CSS, templates, and asset inventory. Reuse those files and
components. Keep new geometry and illustrations original, preserve supplied
logos, and substantiate product claims from the owning engine documentation.
Do not invent capabilities, metrics, or release promises. Verify the rendered
result and update the guides when the authored system deliberately changes.

Project links: [Nanolathe website](https://nanolathe.gg),
[engine source](https://github.com/nanolathe-gg/nanolathe),
[website source](https://github.com/nanolathe-gg/nanolathe-gg.github.io).
