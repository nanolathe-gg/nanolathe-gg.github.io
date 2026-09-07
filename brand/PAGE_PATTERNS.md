# Nanolathe page patterns

Use the existing Hugo layouts and CSS as the starting point for new pages.
The [brand guide](GUIDE.md) explains the palette and asset usage;
[artwork prompts](ARTWORK_PROMPTS.md) cover illustrations. This document describes
the current website structure and recommends how to extend it consistently.

## Where a page lives

`content/` supplies front matter such as the title, description, eyebrow, and
layout name. `layouts/_default/` contains the interior layouts. The homepage
uses `layouts/index.html`. The first-release pages keep their detailed content
in templates; adding Markdown body text will display it only if its selected
layout renders `.Content`.

[`layouts/_default/baseof.html`](../layouts/_default/baseof.html) owns the page
shell: metadata, local assets, header, navigation, skip link, `<main id="main">`,
and footer. An interior template defines `main`; it should not duplicate those
elements. [`page-heading.html`](../layouts/partials/page-heading.html) renders
the eyebrow, one `<h1>`, and description from the page's front matter.

For example, a contribution landing page can use
`content/contribute.md`:

```toml
+++
title = 'Build with the project'
description = 'Find the engine source, website source, and contribution guidance.'
layout = 'contribute'
eyebrow = 'Contribute'
+++
```

and `layouts/_default/contribute.html`:

```html
{{ define "main" }}
  {{ partial "page-heading.html" . }}
  <section class="section wrap">
    <div class="article">
      <span class="eyebrow">Choose a starting point</span>
      <h2>Help build Nanolathe.</h2>
      <p>Read the contribution rules before changing the engine. The website
        has its own source repository and build instructions.</p>
      <div class="actions">
        <a class="button primary" href="{{ site.Params.engineRepo }}/blob/{{ site.Params.engineBranch }}/AGENTS.md">
          Engine contribution guide {{ partial "arrow.html" . }}
        </a>
        <a class="button secondary" href="{{ site.Params.websiteRepo }}">
          Website source <span aria-hidden="true">↗</span>
        </a>
      </div>
    </div>
  </section>
{{ end }}
```

Use a real, specific title and description. Add a page to the header only when
it belongs in primary navigation; the navigation list is in `baseof.html`.
Keep the selected link's `aria-current="page"` behavior. Hugo's raw Markdown
HTML rendering is disabled in `hugo.toml`; use templates for structural HTML
instead of disabling that setting to make an isolated page work.

## Long reference or guide page

Use `docs-layout wrap` for an anchor index beside an `article`. Match every
navigation fragment with one unique section ID. This example is an alternative
body for a page using the same front matter and shell:

```html
{{ define "main" }}
  {{ partial "page-heading.html" . }}
  <div class="docs-layout wrap">
    <aside class="side-nav">
      <span class="eyebrow">On this page</span>
      <nav aria-label="Contribution sections">
        <a href="#engine">Engine</a>
        <a href="#website">Website</a>
      </nav>
    </aside>
    <article class="article">
      <section id="engine">
        <h2>Engine contributions</h2>
        <p>Start with the
          <a href="{{ site.Params.engineRepo }}/blob/{{ site.Params.engineBranch }}/AGENTS.md">contribution rules</a>
          and the owning design document.</p>
      </section>
      <section id="website">
        <h2>Website contributions</h2>
        <p>Read the <a href="{{ site.Params.websiteRepo }}">website README</a>
          for local build and validation commands.</p>
      </section>
    </article>
  </div>
{{ end }}
```

At full width the index is `230px`, the column gap is `70px`, and the article
is capped at `830px`. These dimensions step down at `1100px` and `820px`.
At `650px` and below the layout becomes one column and the index becomes a
wrapping list above the article. Reuse this behavior rather than adding a
second mobile navigation pattern.

## Component choices

| Need | Existing classes or partial | Usage |
| --- | --- | --- |
| Centered content | `wrap` | Apply once per horizontal container |
| Standard vertical section | `section` | Pair with `wrap`, or put a `wrap` inside a full-width section |
| Short category label | `eyebrow` | Amber monospace; keep it concise |
| Section title with adjacent link | `section-heading`, `text-link` | Pair a heading group with one useful destination |
| Primary next step | `actions`, `button primary` | Green filled action; use an anchor for navigation |
| Secondary next step | `button secondary` | Amber outline action |
| Arrow | `partial "arrow.html" .` | Decorative `24 × 24` geometry, `1.6` stroke, displayed at `18px` |
| Process steps | `steps-grid`, `step`, `step-number` | Use when there is an actual sequence |
| Linked editorial panels | `research-grid`, `research-card`, `card-visual`, `card-body` | Entire card may be one link; never nest links or buttons inside it |
| Copyable command | `command-panel`, `command-title`, `copy-button` | Unique code ID plus matching `data-copy` value |
| Short explanatory note | `inline-note` | Relevant context adjacent to the affected instruction |
| Optional detail | Native `details` and `summary` inside `article` | Label the topic clearly; keep essential instructions visible |
| Experimental state | `experimental` | Use with a positioned containing component, as in `feature-band` |

Example command panel for a website build:

```html
<div class="command-panel">
  <div class="command-title">
    From the website checkout
    <button class="copy-button" data-copy="website-build">Copy command</button>
  </div>
  <pre><code id="website-build">hugo --gc --minify --panicOnWarning</code></pre>
</div>
```

`site.js` reads the associated code element's text and gives copy feedback.
Keep the command selectable even when clipboard access is unavailable. Use
buttons for state-changing controls and anchors for destinations. Pair status
colors or dots with words; a green square alone cannot communicate a state.

## URLs and content

Use Hugo's URL handling and normal template escaping. These patterns match
the current site:

```html
<!-- Local route or a fragment on another local page -->
<a href="{{ "docs/" | relURL }}">Documentation</a>
<a href="{{ "docs/#formats" | relURL }}">File formats</a>

<!-- Local static asset; omit the repository's static/ prefix -->
<img src="{{ "brand/wordmark.svg" | relURL }}" alt="Nanolathe" width="300">

<!-- Maintained external source, from hugo.toml -->
<a href="{{ site.Params.engineRepo }}">Engine source</a>
<a href="{{ site.Params.websiteRepo }}">Website source</a>

<!-- A Hugo page object obtained while ranging pages -->
<a href="{{ .RelPermalink }}">{{ .Title }}</a>
```

Keep URLs quoted. Use configured repository parameters rather than scattering
copies of the repository URL through templates. Do not apply `safeURL` or
`safeHTML` to bypass escaping for arbitrary content. Use the base template's
canonical URL and metadata rather than adding competing tags in a page body.

Make every action lead to a useful destination. Use concrete labels such as
“Build & run,” “Engine source,” and “File formats.” Source links point to the
available [engine repository](https://github.com/nanolathe-gg/nanolathe) and
[website repository](https://github.com/nanolathe-gg/nanolathe-gg.github.io).
Describe the actual current state of a feature or resource collection; do not
invent entries, release dates, implementation claims, benchmarks, or activity
counts to fill a layout. Read implementation status from the owning engine
documentation and preserve research evidence labels when citing it.

## Layout and type

The default `.wrap` is `min(1280px, calc(100% - 112px))`. Side gutters become
`32px` at widths up to `1100px`, `22px` at up to `820px`, and `20px` at up to
`650px`. Standard sections have `92px` vertical padding, reducing to `65px`
at `820px` and `55px` at `650px`. Use these existing rules rather than making
nearby pages subtly different.

Palette and font values come from `data/brand.json`, rendered through
`assets/css/tokens.css`; use `assets/css/site.css` for component and layout rules.
Use Chakra Petch `600` for headings, the system sans-serif stack for reading,
and the monospace stack for labels and code. Preserve the `16px` base reading
size and existing heading hierarchy. An interior title already comes from
`page-heading.html`; section headings start at `<h2>`. Let normal copy wrap,
use manual line breaks sparingly in short display headlines, and avoid fixed
heights for new text blocks. Reuse thin borders and rectangular panels. Introduce
new component CSS only when an existing pattern cannot serve the content.

## Motion and accessibility

The homepage's `.nano-spray` canvas is decorative original artwork enhancement.
It follows the construction illustration's focal point. Its animation has a
pause/play control, respects `prefers-reduced-motion`, and stops while the
document or hero is not visible. It is not a simulation or a retail behavior
demonstration. Changing the hero image or its positioning requires checking
the emitter alignment in `assets/js/site.js` as well as the CSS crop.

Keep the reduced-motion CSS, visible keyboard focus, skip link, meaningful
heading order, and mobile menu's `aria-expanded` state. The menu closes with
Escape and returns focus to its toggle; preserve this when changing navigation.
Decorative arrows, grids, and canvases use `aria-hidden="true"`. Give informative
images useful alt text and icon-only controls an accessible name. Label original
concept artwork visibly. Do not add essential instructions only inside an
image, animation, hover state, or color distinction.

As an authoring guideline, keep motion limited to a purposeful small area and
make static content sufficient to understand the page. Check keyboard use,
reduced motion, zoom, and behavior with JavaScript unavailable. Ensure primary
tasks remain reachable when enhancing the layout.

## Build and look at the result

From the website checkout, use the version of Hugo named in `README.md` and run:

```sh
hugo --gc --minify --panicOnWarning
python3 scripts/check-site.py
hugo server
```

The first two commands build and validate pages, links, anchors, and assets.
The final command serves the site for visual inspection. Do not commit generated
`public/` output. A successful build does not establish that a page looks right.

| Viewport width | Inspect |
| --- | --- |
| `320px` | Long headings, button wrapping, command wrapping, menu, horizontal overflow |
| `390px` | Typical narrow layout, hero crop, caption, touch controls, section rhythm |
| `768px` | Tablet navigation fit, remaining multi-column layouts, article width |
| `1440px` | Desktop hierarchy, content alignment, line lengths, image/text balance |
| `1920px` | Maximum content width, whitespace, large-screen hero placement and particle alignment |

Capture and inspect screenshots at all five widths for a new visual pattern.
Also test real links and downloads, keyboard focus and Escape behavior, the
motion toggle, reduced-motion mode, and text zoom. Fix clipping, overlap,
unreadable text, and broken assets before publishing. Check updated content
against the actual implementation separately from the visual review.
