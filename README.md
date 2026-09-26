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

The build packages the brand kit before running Hugo. All verification scripts use
only the Python standard library. The check verifies required pages,
internal links, anchors, local assets, the custom-domain file, and every format's
authored examples. Pull requests
build and validate without deploying. Pushes to `main` deploy through GitHub
Actions; generated `public/` output is not committed.

## Content and maintenance

Use American English for site copy, including headings, captions, accessibility
text, and documentation (for example, armor, color, behavior, and defense). Keep
verbatim source snapshots, quotations, and technical identifiers unchanged.

- `hugo.toml`: engine repository, branch, and site metadata.
- `content/`: page titles, descriptions, and route selection.
- `layouts/`: the homepage and page content for this first release.
- `data/references.yaml`: the complete v0 directory of format and behavior docs.
- `data/brand.json`: shared palette, typography, asset inventory, and project
  positioning (engine description and README banner tagline).
- `assets/css/tokens.css`: Hugo template that turns the brand data into site CSS.
- `assets/css/site.css`, `assets/css/brand.css`, `assets/js/site.js`: layout and interactions.
- `brand/`: design guide, artwork prompts, and page patterns.
- `static/brand/`: reusable logos, icons, avatars, and PNG exports.
- `static/CNAME`: `nanolathe.gg`.

Engine links and clone commands target `https://github.com/nanolathe-gg/nanolathe`.

### Player references

`content/docs/keyboard-shortcuts.md` and `content/docs/strategic-icons.md` use the
shared `guide` layout and appear under “Playing Nanolathe” in the documentation
directory. Keep keyboard bindings aligned with the pinned engine dispatcher,
host controls, and authored command panels; modern-only controls have their own
section. Icon examples are described in `data/strategic-icons.json`, with PNGs in
`static/images/strategic-icons/`. Their generator uses the exact pinned engine
atlas geometry and preview sampler, with no retail artwork:

```sh
python3 scripts/strategic-icon-examples.py --engine ../nanolathe --check
```

This optional regeneration check requires Go and a matching engine checkout;
ordinary builds use the checked-in images. Update the source revision, geometry
hash, descriptions, and examples together when the icon vocabulary changes.

### Format documentation

All 15 researched formats have illustrated references at `/docs/formats/<slug>/`,
with Markdown and authored assets in the matching `content/docs/<slug>/`
bundles. The documentation directory links to each guide. Every page pins its
research to an engine commit and includes original downloadable examples.
Examples range from sprite and model inspectors to map layers, bytecode stepping,
palette and scanline comparisons, text parsing, and playable audio.

New format pages reuse the `format` layout, semantic table renderer, callouts,
figure/demo shortcodes, and automatic contents list. Start with:

```sh
hugo new content --kind format docs/new-format/index.md
```

Replace the source revision and placeholder copy before building. A corresponding
`/docs/<slug>` page automatically replaces that format's GitHub link in the
documentation directory. See [the format authoring guide](brand/FORMAT_PAGES.md)
for the complete pattern and component examples. Keep behavioral corrections in
the engine's owning research document and update the website's pinned snapshot.

Examples are reproducible with the Python standard library. Each format has a
`scripts/<slug>-example.py` generator; use `--check` to verify without writing:

```sh
python3 scripts/gaf-example.py
python3 scripts/gaf-example.py --check
python3 scripts/check-format-examples.py
```

The checks decode authored binaries or text, verify worked example states, and
compare generated assets. All 15 generators run in `make check`. They do not
require retail game data or a checkout of the engine repository.


The Resources page intentionally has no entries. Future curated metadata and
release-hosted downloads can be added when the collection is ready. Signed
engine downloads are deferred; Get started offers source installation commands.

### Source installer releases

`static/install.sh` and `static/install.ps1` resolve the latest commit on the
engine repository's `main` branch at the start of every installation. They
fetch that exact commit's archive over HTTPS and record it in the installed
release's `source-revision` file. Launchers compare that commit with current
`main` and offer an update; failed checks or builds preserve the installed game.
Existing users should rerun the install command once to adopt main tracking.

`static/install/release.txt` still supplies pinned official Go toolchain and
public installer checksums. Its source revision and archive hashes describe a
legacy snapshot for older installers; they do not select or verify current-main
source. Current source downloads trust GitHub HTTPS and the resolved commit ID.
The private Go version must still be updated when main requires a newer compiler.

Refresh toolchain/legacy snapshot metadata after engine checks pass:

```sh
python3 scripts/prepare-source-release.py --revision FULL_COMMIT --version RELEASE_LABEL --go-version 1.26.8
make check
```

Preparation hashes the website's current installer scripts. Importing scripts
from an engine snapshot requires `--sync-installers --engine ../nanolathe`;
review their main-tracking behavior before publishing. After editing either
public installer, refresh its `installer_*_sha256` field in the manifest.
`make check` verifies published copies, checksums, and offline installer behavior.
Native Windows installation should also be checked before publishing.

### Mod catalogue

The engine's *Get more mods* dialog reads `https://nanolathe.gg/mods/manifest.json`
(`static/mods/manifest.json`). The archives are not in this repository: each
mod version is one asset, `<id>-<version>.zip`, on this repository's single
[`mods` release](https://github.com/nanolathe-gg/nanolathe-gg.github.io/releases/tag/mods),
which the manifest names by URL. The engine accepts release assets of
`nanolathe-gg` repositories, follows GitHub's redirect to its asset host, and
refuses any archive whose size or SHA-256 differs from its manifest entry.

Each version has a recipe, `mods/<id>-<version>.json`: the upstream archive's
name, size and SHA-256, the members to keep, and the `nanolathe-mod.json`
metadata to embed. To add a version, download the upstream archive and run
(the upload needs the GitHub CLI, logged in with write access):

```sh
python3 scripts/package-mod.py mods/prota-4.8.json ~/Downloads/ProTA4.8.zip --upload
make check check-mods-remote
```

Packaging verifies the upstream file, copies only the included members (never
executables, libraries, ddraw wrappers or launcher settings), embeds the
metadata, and writes `.cache/mods/<id>-<version>.zip` uncompressed with fixed
timestamps in sorted order, so the same upstream file always yields the same
bytes. `--upload` publishes it to the `mods` release, creating the release if
needed, and the manifest entry is added or replaced. `make check` verifies the
manifest against the recipes offline; `make check-mods-remote` also downloads
every release asset and checks it as the engine would.

TA Zero uses a multipart recipe: Base, Alpha 5 and Map Pack 1f are pinned
separately and combined into one content root. Pass their paths in recipe order:

```sh
python3 scripts/package-mod.py mods/ta-zero-alpha5-20241224.json \
  ~/Downloads/TA_Zero_Base.zip ~/Downloads/TA_Zero_Alpha_5.zip \
  ~/Downloads/TA_Zero_Map_Pack_v1f.zip
```

Each `sources` item has its own `upstream`, `include` and optional `stripPrefix`.
The packager rejects duplicate destination names across sources. Before upload,
compare the original layered roots with the extracted ZIP using the engine VFS
and compiled catalog: combining archives can change mount precedence even when
no filenames collide. This release preserves the verified Base/Alpha 5/1f
content; its metadata marks support experimental, selects the `zero` content
profile and controls, and requires Community 3.9 or Modern. Windows binaries,
launcher settings and local installation receipts are omitted. Append `--upload`
to the command after verification, then deploy the catalogue.

A published asset is never replaced: clients resume and verify downloads
against the published hash, so a mistake is corrected with a new version. To
withdraw a version, remove its manifest entry and recipe; delete the asset
once nothing needs it.

## About page

`content/about.md` supplies metadata and `layouts/_default/about.html` tells the
project’s story, research process, technology choices, and current priorities.
Creator-supplied retail research captures live in `static/images/about/`; their
provenance is recorded in `ASSETS.md`. Keep status claims aligned with the engine.

## Renderer features page

`data/renderer.json` supplies the visual feature explanations and capture metadata.
The features template uses lossless screenshots, accessible before/after sliders,
and opt-in camera/effect animations with matched off/on playback. The short TA
introduction opens a detailed gameplay dialog; `/gameplay/` serves the same
server-rendered guide for direct links, search and a no-JavaScript fallback.
`data/gameplay.json` owns its content. Media lives in `static/images/renderer/`;
`scripts/renderer-capture/README.md` records reproducible staged capture commands
and per-scene validation evidence. The metallic materials section also includes
a draggable WebGL study with finish toggles, tilt, and optional unit or light
rotation. Reset restores the engine’s fixed light direction. Its
single-pose display assets and shader provenance are documented in
`scripts/renderer-capture/live-materials/`; the original clip remains available.
The ordinary website build
requires neither a GPU nor retail game data.

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
Petch font uses the SIL Open Font License in `static/fonts/OFL.txt`. The features
page includes engine screenshots and clips displaying original Total Annihilation
artwork; those underlying game assets remain the property of their respective
owners and are not covered by the website code license. Playable game data is not
included and must be obtained separately. See `ASSETS.md` for capture provenance.
