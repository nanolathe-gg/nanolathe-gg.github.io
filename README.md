<picture>
  <source media="(prefers-color-scheme: dark)" srcset="static/brand/wordmark.svg">
  <img src="static/brand/wordmark-light.svg" alt="Nanolathe" width="420">
</picture>

The homepage and documentation gateway for **[nanolathe.gg](https://nanolathe.gg)**.
Built with Hugo, maintained in `nanolathe-gg/nanolathe-gg.github.io`, and deployed
as the organization's default GitHub Pages site.

## Run locally

Install [Hugo Extended 0.160.0 or newer](https://gohugo.io/installation/), Python 3,
and Make, then:

```sh
make serve
```

No Node packages or Go web server are required. Font and image assets are served
locally. Production builds use Hugo 0.160.0, pinned in the Pages workflow.

## Build and verify

```sh
make check
```

The build packages the brand kit before running Hugo. Both Python scripts use
only the standard library. The check verifies required pages,
internal links, anchors, local assets, and the custom-domain file. Pull requests
build and validate without deploying. Pushes to `main` deploy through GitHub
Actions; generated `public/` output is not committed.

## Content and maintenance

- `hugo.toml`: engine repository, branch, and site metadata.
- `content/`: page titles, descriptions, and route selection.
- `layouts/`: the homepage and page content for this first release.
- `data/references.yaml`: the complete v0 directory of format and behavior docs.
- `data/brand.json`: shared palette, typography, and brand asset inventory.
- `assets/css/tokens.css`: Hugo template that turns the brand data into site CSS.
- `assets/css/site.css`, `assets/css/brand.css`, `assets/js/site.js`: layout and interactions.
- `brand/`: design guide, artwork prompts, and page patterns.
- `static/brand/`: reusable logos, icons, avatars, and PNG exports.
- `static/CNAME`: `nanolathe.gg`.

Engine links and clone commands target `https://github.com/nanolathe-gg/nanolathe`.

### Documentation rollout

- **v0:** this website links to the maintained documents on GitHub.
- **v1:** import a pinned revision of the engine's research corpus into readable
  pages, preserving citations, stable anchors, and confidence labels. Keep
  behavioral corrections in the owning engine research document.
- **Later:** add authored examples, diagrams, screenshots, and interactive
  explanations, starting with PAL, GAF, 3DO, and TNT.

The Resources page intentionally has no entries. Future curated metadata and
release-hosted downloads can be added when the collection is ready. Signed
engine downloads are also deferred; current guidance is for source builds.

## Brand assets

Browse **[the brand kit](https://nanolathe.gg/brand/)** or download its ZIP and open
`START-HERE.html` for an offline catalog. The kit includes outlined SVG wordmarks,
transparent PNGs, light/dark and monochrome marks, square avatars, favicons,
ten utility icons, the font and its license, CSS/JSON tokens, and editable examples.
Wordmark PNGs are 1000 px wide; avatars are 512 px, with a 1024 px dark export.

- [Design guide](brand/GUIDE.md): logo use, colors, font roles, spacing, and motion.
- [Artwork prompts](brand/ARTWORK_PROMPTS.md): copyable style and scene briefs.
- [Page patterns](brand/PAGE_PATTERNS.md): Hugo components and layout examples.
- [Asset provenance](ASSETS.md): authorship, font license, and original hero prompt.
- [README header](brand/README_HEADER.md): new illustration with the exact
  wordmark, ready-to-paste Markdown, and editable source.

For a new design, give a designer or agent the kit and this brief:

> Read brand/GUIDE.md first, then brand/ARTWORK_PROMPTS.md for artwork or
> brand/PAGE_PATTERNS.md for a page. Reuse the supplied logos and color tokens.
> Create: [describe the asset, audience, placement, and dimensions].

`make brand` rebuilds the ZIP, guide downloads, and CSS/JSON exports. Generated
downloads are ignored by Git. Edit `data/brand.json` to update shared palette or
font metadata; keep the written guides aligned with intentional design changes.

The checked-in SVG and PNG assets are ready to use. To change their geometry or
export colors, the optional authoring tools need FontTools and Sharp:

```sh
python3 -m venv /tmp/nanolathe-brand-tools
/tmp/nanolathe-brand-tools/bin/pip install fonttools
/tmp/nanolathe-brand-tools/bin/python scripts/brand.py
/tmp/nanolathe-brand-tools/bin/python scripts/readme-banner.py
npm install --prefix /tmp/nanolathe-brand-tools sharp
NODE_PATH=/tmp/nanolathe-brand-tools/node_modules node scripts/export-brand.cjs
make check
```

These authoring dependencies are separate from the website build. Inspect the
updated SVG and PNG exports, then commit them along with their source changes.

## Deployment

The repository name `nanolathe-gg.github.io` makes this the organization's default
site. GitHub Pages must use **GitHub Actions** as its publishing source, with
`nanolathe.gg` set as the custom domain and HTTPS enabled once GitHub provisions
the certificate. The custom domain also lives in `static/CNAME` for portability.

## License

Website code and original brand geometry: [MIT](LICENSE). The bundled Chakra
Petch font uses the SIL Open Font License in `static/fonts/OFL.txt`. No original
Total Annihilation game assets are included. Game data must be obtained separately.
