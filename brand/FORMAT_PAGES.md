# Format documentation pages

All 15 guides under `/docs/formats/` share the integrated reference layout,
introduced with GAF and 3DO. Use the same layout for subsequent formats.
Content belongs in Markdown, reusable presentation in
shortcodes/CSS, and format-specific interactions in a small partial and script.

## Start a page

```sh
hugo new content --kind format docs/new-format/index.md
```

The archetype supplies front matter and a section outline. Set a real title,
format label, extension, description, useful facts, and the **full engine commit**
whose document you adapted. The route is `/docs/formats/<slug>/`; the content
bundle is `content/docs/<slug>/`. The documentation directory automatically links
to an existing `/docs/<slug>` page rather than the upstream Markdown. There is no
need to edit the directory template per format.

| Front-matter key | Purpose |
| --- | --- |
| `type = 'format'` | Selects `layouts/format/single.html` and the scoped table renderer |
| `url` | Stable public route |
| `format`, `extension` | Breadcrumb, monogram, and compact identity |
| `facts` | Repeated `{label, value}` records for the header facts |
| `sourcePath`, `sourceRevision` | Owning engine research and full pinned commit |
| `demoScript` (optional) | Asset path of a per-format JavaScript file |
| `demoCSS` (optional) | Asset path for format-specific styles, such as the 3DO inspector |

Keep headings semantic: one layout-owned H1, Markdown H2 sections, H3 subsections.
Give major headings stable IDs using `{#byte-layouts}`. The table of contents
comes from Hugo; no hand-maintained anchor list is required. Byte-layout
subsections also appear in the desktop sidebar. Small screens get a collapsible
contents list above the article.

## Reusable components

### Byte tables

Use ordinary Markdown tables. The format render hook adds real `table`, `thead`,
`tbody`, and `th scope="col"` elements, with a keyboard-focusable horizontal
scroll region. Five-column byte layouts keep a readable minimum width on mobile.

```markdown
| Offset | Bytes | Type | Field | Meaning |
| --- | --- | --- | --- | --- |
| `+0x00` | 2 | `u16` | `width` | Pixel width. |
```

Explain whether offsets are file-relative or record-relative in nearby prose.
Separate fixed header bytes from trailing variable-length tables. Preserve the
source's unsigned/signed distinctions and consumer-specific field widths.

### Admonitions

```text
{{< callout kind="warning" title="Do not infer timing from this field" >}}
The playback delay lives in the frame reference. See the owning evidence.
{{< /callout >}}
```

Kinds: `note`, `established`, `warning`, `policy`, `unknown`. Each has a visible
text label, title, and semantic `aside`; color is supplementary. Invalid kinds
fail the build. Do not turn host choices or open questions into established
retail rules when adapting prose.

### Static pictures

Place assets in the page's leaf bundle. Relative links work at the page route.

```text
{{< figure src="comparison.svg" alt="Describe the meaningful difference" width="720" height="300" >}}
Explain the picture and identify whether it is authored, measured, or schematic.
{{< /figure >}}
```

Use native SVG for diagrams and crisp pixel examples. Include the image's
intrinsic dimensions, useful alt text, and a visible caption. Keep the original
and annotated variants distinguishable. Do not replace publication-omitted
retail examples with invented retail-looking evidence.

### Interactive examples

```text
{{< format-demo name="pal-comparison" id="palette-example" title="One index, different colors" >}}
Explain what changes, and link the underlying data.
{{< /format-demo >}}
```

Provide `layouts/partials/formats/pal-comparison.html` and set
`demoScript = 'js/formats/pal.js'` if interaction is needed. The wrapper supplies
the heading, figure and caption. An unknown partial fails the build. Shared
presentation classes live in `assets/css/format.css`: `.comparison-grid`,
`.checkerboard`, `.demo-controls`, `.control-line`, `.check-label`.

Render a useful static state in HTML. Hide interactive controls until their
handlers exist; keep downloads and explanatory text available without scripts.
Use native labeled controls, alt text for changing images, and meaningful state
labels. Start motion paused, stop when hidden/offscreen, and honor reduced motion.
Do not mark rapidly changing playback text as a live announcement.

### Pinned citations

```text
[Owning research]({{< research >}})
[Palette reference]({{< research "research/formats/pal.md" >}})
```

The shortcode resolves against the page's pinned commit. Its optional second
argument is an explicitly verified anchor including `#`. Preserve evidence IDs
and section numbers when exact upstream anchors are unavailable. Keep complete
source snapshots as `.txt` resources so Hugo serves them as downloads instead of
interpreting them as additional content pages.

Use `format-link` for navigation between guides, keeping `research` for pinned
evidence citations:

```text
[Palette guide]({{< format-link "pal" >}})
```

This resolves to a local guide when available, or to the corresponding research
at the current page's pinned revision while a guide is still being written.

### Examples to copy

| Need | Existing pattern |
| --- | --- |
| Playback and layered sprite comparisons | GAF |
| Geometry, hierarchy and before/after transforms | 3DO |
| Byte-derived static image comparisons | PAL, FNT, PCX |
| Step through decoding or state changes | HPI, COB, TDF, TAD |
| Inspect layers, positions or authored cells | TNT, OTA, FBI |
| Toggle visibility and disabled states | GUI |
| User-triggered native audio | WAV |

Keep fixtures original and small. Add `scripts/<slug>-example.py` with a
read-only `--check` mode; `make check` discovers it once the page's `index.md`
exists. Generate resources first and add the page last so the local preview
stays usable while several authors work. The checker uses only the Python
standard library and does not need engine or game data.

## Verification and handoff

1. Run `make check` (Hugo build, links/assets/anchors, all format fixture checks).
   In a sandbox that cannot write the default Hugo cache, use
   `HUGO_CACHEDIR=/private/tmp/nanolathe-hugo-cache make check`.
2. Run `make serve`, open the new route, and inspect wide/narrow screens.
3. Exercise keyboard controls, comparisons, animation pause, table scrolling,
   anchor links, and downloads. Static HTML must remain useful without scripts.
4. Update `ASSETS.md` with source revision and visual provenance. Behavioral
   corrections belong in the engine's owning research before refreshing the page.

Do not commit generated `public/` output. Starting Hugo locally does not deploy;
pushing to the publishing branch does. Leave publishing to the user's request.
