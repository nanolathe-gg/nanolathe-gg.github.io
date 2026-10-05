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

The build packages the brand kit before running Hugo. Content and installer checks use the Python standard library. When Node is
available, `make check` also runs the browser-platform selection assertions. The check verifies required pages,
internal links, anchors, local assets, the custom-domain file, and every format's
authored examples. Pull requests
build and validate without deploying. Pushes to `main` deploy through GitHub
Actions; generated `public/` output is not committed.

## Browser build

`/play/` is the engine's browser launcher, not a Hugo page. `make build` runs
`scripts/fetch-play.py`, which downloads the engine's newest complete
[`browser-<run>` release](https://github.com/nanolathe-gg/nanolathe/releases)
(an asset-free `tools/browser-build` output of every main commit, published
immutably per run), checks the archive and `build.json` against the release's
`SHA256SUMS`, verifies the content-hashed Wasm against `build.json`, adds the original demo archive
and readme from this repository's `demo` release, checked against the digests
pinned in `data/play.json`, and places everything under the ignored
`static/play/`. `scripts/style-play.py` applies the website header and styles to
the root launcher, preserving the content-hashed host modules and engine runtime.
The website starts the demo directly at `/play/`, focuses the game and accepts
local folder drops over the running viewport. The launcher landing section and
Back to launcher button are removed; a small recovery panel offers retry, folder
selection and native installation if the demo cannot start.
Hugo serves the files at the same origin as the launcher requires. The one build
that is live at nanolathe.gg/play/ is kept
beside the new one so an open launcher can still restart. `make check` then
runs `scripts/check-play.py` against `public/play`.

The engine's CI sends a `browser-build` repository dispatch after each publish
when its `WEBSITE_DISPATCH_TOKEN` secret is configured; otherwise the Pages
workflow checks for a changed build every six hours and deploys only then. Every
CI build requires a verified engine build and demo assets (`PLAY_REQUIRED=1`),
so a failed fetch cannot publish a demo button leading to a placeholder. Local
builds can use a placeholder when no verified build is available.

To preview a local engine build: `python3 scripts/fetch-play.py --local
../nanolathe/build/browser --demo-root ~/TotalAnnihilationDemo`, then
`make serve`; later builds keep that preview until `PLAY_REFRESH=1 make play`
fetches the release again. Use `--required` when preparing a release preview.
See `BROWSER_REVIEW.md` for the current local integration, build provenance and
the engine publishing dependency.

## Local beta redesign review

The beta redesign remains a Hugo site. Shared templates keep the existing
technical reference pages, installer scripts, mod catalogue and brand kit.
`assets/css/redesign.css` adapts the private prototype for marketing pages;
`redesign-native.css` integrates the shared shell and existing Hugo components.
`assets/js/platform.js` detects desktop OS hints locally, while `redesign.js`
handles the ownership choices, manual override, copy command, matched slider,
and matched comparisons. No installation commands execute in the page.

The prototype source is Library item
`libfile_ad4a04f3f9dc81919104b804d8d0c50c`,
`Nanolathe-prototype-beta-handoff.zip`, received October 3, 2026. Its seven-route
beta draft was the design reference. It was integrated into native Hugo routes;
full technical docs and renderer studies remain available locally.

The homepage comparison and Features use real v6 native captures from
production engine
`617540c5`, with the initial diagnostic harness at `33ee2ed8` and local follow-up at
`6c0cfd98`. The matched
Greenhaven blast includes healthy, genuinely synthesized tree sprites alongside
2× synthesized terrain, lighting and glow. `scripts/renderer-capture/v6/README.md`
records exact scenes, controls, source/binary hashes and pixel/export verification.
Modern/default and beta remain website positioning; engine runtime defaults are
unchanged. The playable browser demo uses the independently verified Wasm build.

The opening hero is a silent 12-second, 60 FPS native modern GPU film of a
staged ARM base and battle from engine `e2ac78cd`. Actual Metal, AA, lighting,
glow and genuinely synthesized 2× terrain and feature sprites accompany normal
patrols, factory production, commander construction and combat. It plays in view,
pauses offscreen or in a hidden tab, and includes a pause/play control. Reduced
motion and data-saving preferences keep the lossless still until explicit play;
JavaScript, video loading and autoplay failures retain the still fallback.
The exact script, source/binary hashes, native frame evidence, export and browser
verification are in `scripts/renderer-capture/home-hero-video/README.md`.

The Features page reads `data/features.json`. Its nine chapters include a slider
through 26 actual camera captures (starting at 1×), a larger original/synthesized
terrain-and-foliage comparison, matched lighting, a transport/submarine
live water study with independent effect controls, the restored live WebGL material study,
a nine-model lineup, fire shimmer, real wreck cooling and aircraft soft shadows. Native videos play on request
and paired controls preserve playback position. Water animates continuously in
view, pauses offscreen and starts still for reduced-motion preferences. The material study retains its
801c8b2 provenance and a v5 native recording as fallback. Native captures and the
browser studies are explicitly distinguished. Historical v4/v5 evidence remains
available but no longer supplies the home comparison or the refreshed scenes.

For a loopback-only preview:

```sh
hugo server --bind 127.0.0.1 --port 1313 --disableFastRender --disableLiveReload --renderToMemory
```

Do not push, merge into main, deploy, publish, or change DNS as part of this local review.

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


Signed engine downloads are deferred; Get started offers source installation commands.

### Source installer releases

`static/install.sh` and `static/install.ps1` resolve the latest commit on the
engine repository's `main` branch at the start of every installation. They
fetch that exact commit's archive over HTTPS and record it in the installed
release's `source-revision` file. Launchers compare that commit with current
`main` and offer an update; failed checks or builds preserve the installed game.
Existing users should rerun the install command once to adopt main tracking.

The Mac app in `~/Applications` and Windows Start Menu shortcut use the green N
icon and are refreshed on every successful update. Mac app updates show a native
progress window with the current installation stage. The public scripts are
byte-for-byte copies of the engine's `tools/installer/install.sh` and
`install.ps1`; keep their mirrored offline tests and source fixtures aligned.

`static/install/release.txt` still supplies pinned official Go toolchain and
public installer checksums. Its source revision and archive hashes describe a
legacy snapshot for older installers; they do not select or verify current-main
source. Current source downloads trust GitHub HTTPS and the resolved commit ID.
The private Go version must still be updated when main requires a newer compiler.

Refresh toolchain/legacy snapshot metadata after engine checks pass:

```sh
python3 scripts/prepare-source-release.py --revision FULL_COMMIT --version RELEASE_LABEL --go-version 1.27.1
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
(`static/mods/manifest.json`). This is the single catalogue for the latest
unreleased test builds. Its root stays schema 1, with one current entry per
mod. Each entry contains only `id`, `name`, `version`, `summary`, `homepage`
and `archive` (`url`, `size`, `sha256`). All package configuration belongs in
the ZIP's root `nanolathe-mod.json`, a complete schema 2 config; the catalogue
does not select content profiles, controls, rules or settings.

The archives are not tracked in this repository: each mod version is one
asset, `<id>-<version>.zip`, on this repository's single
[`mods` release](https://github.com/nanolathe-gg/nanolathe-gg.github.io/releases/tag/mods).
The engine follows GitHub's redirect to its asset host and refuses an archive
whose size, SHA-256 or embedded identity differs from its catalogue entry.
Versions use the original mod's version, without a Nanolathe packaging suffix.
A packaging update replaces the same named ZIP and changes its catalogue
SHA-256. The engine compares that hash with the installed receipt to offer
updates, and partial downloads are kept separately for each hash. Saves record
the installed archive hash; a packaging update does not retain the old bytes
under the same version.

Each current package has a recipe, `mods/<id>-<version>.json`: the upstream
archive's name, size and SHA-256, the members to keep, and the full config to
embed. The configs come from the engine repository's
`modconfigs/<release>/nanolathe-mod.json`, preserving the curated summaries
and homepages here. The configs carry the mod's content layout, limits,
Community feature table, recommended rules, settings, keys and locks. The
engine validates these declarations when installing the ZIP.

ZIP input is the default. RAR recipes specify `upstream.format: "rar"` and
need `bsdtar` (libarchive), provided by the system `tar` on macOS. This is a
packaging dependency only. An optional `stripPrefix` selects a content
directory inside the source archive; include patterns match paths relative
to that directory, which becomes the hosted ZIP root.

To prepare the current packages from their pinned upstream archives:

```sh
python3 scripts/package-mod.py mods/prota-4.8.json ~/Downloads/ProTA4.8.zip
python3 scripts/package-mod.py mods/escalation-10.2.0.json ~/Downloads/TAESC_GOLD_10_2_0_FULL.rar
python3 scripts/package-mod.py mods/ta-zero-alpha5-20241224.json \
  ~/Downloads/TA_Zero_Base.zip ~/Downloads/TA_Zero_Alpha_5.zip \
  ~/Downloads/TA_Zero_Map_Pack_v1f.zip
python3 scripts/package-mod.py mods/mayhem-11.3.0.json ~/Downloads/TotalM1130.zip
python3 scripts/package-mod.py mods/twilight-2.0-beta98.json \
  ~/Downloads/"TAT Drop in b91.zip" ~/Downloads/"TAT-v2.0 Beta 98.zip"
python3 scripts/test-package-mod.py
python3 scripts/test-package-multipart.py
make check
python3 scripts/check-mods.py --local
```

Packaging verifies each input, copies only the included members, embeds the
complete config, and writes `.cache/mods/<id>-<version>.zip` uncompressed with
fixed timestamps in sorted order. The same sources and recipe produce the
same bytes. The catalogue projection is explicit, so adding a config field
cannot accidentally publish it in the feed. Preparation replaces the mod's
current catalogue entry while preserving its position in the list.

Escalation's upstream download is listed on its
[downloads page](https://taesc.tauniverse.com/?p=downloads). Its recipe takes
all eight authored content archives (including `TADEMO.ufo`), `Icon/`,
`Music/`, the active `data/1.ZRB` intro, and the Gold release notes from the
Step 2 directory. `TADEMO.ufo` contributes authored unit and feature
definitions. The backup intro, executables, launcher settings and optional
shaders are excluded. Its config carries the Escalation content layout and
Community table, with no keyboard preset.

TA Zero uses a multipart recipe: Base, Alpha 5 and Map Pack 1f are pinned
separately and combined into one content root. Each `sources` item has its
own `upstream`, `include` and optional `stripPrefix`; pass input paths in
recipe order. The packager rejects duplicate destination names across
sources. Before publishing a changed selection, compare the original layered
roots with the extracted ZIP using the engine VFS and compiled catalog:
combining archives can change mount precedence even when no filenames
collide. This packaging revision preserves the verified Base/Alpha 5/1f
content and carries its complete config, including the Zero keyboard preset.
Compatibility remains experimental while historical gameplay and controls
remain incomplete.

Total Mayhem 11.3.0 uses the official single ZIP. The Nanolathe archive keeps
only `mayhem.gp3`, `TADemoM.ufo`, `Icon/` and the two changelogs. Its config
maps the renamed content directories and carries the Mayhem Community table.
Compatibility remains experimental while full gameplay and controls parity
with the shipped runtime is unverified. None of the hosted packages includes
executables, libraries, wrappers, launcher settings or base-game archives.

TA: Twilight 2.0 Beta 98 uses the TAF Base Beta 91 and Beta 98 ZIPs. The
update replaces `rev31.gp3` entirely in the original installation. Its recipe
keeps that replacement and the base's companion archives, icons and original
unit guide, plus the summaries, updated changelog and license. Comparing the
original installed directory with the cleaned package preserves all archive
winners and the compiled catalog hash. Mounting the old archive as another
root would introduce fallback content absent from the original installation.
The complete config carries authored limits and the pinned source's Twilight
Community profile. Historical patch gameplay and controls remain unverified,
so compatibility is labelled experimental.

Keep the recipes and catalogue on a branch until engine compatibility is
verified. After review, append `--upload` to each preparation command to
publish its ZIP with the GitHub CLI, logged in with write access. Upload all
new ZIPs before deploying the catalogue, then run:

```sh
make check check-mods-remote
```

An upload skips an asset whose size and SHA-256 already match, and replaces
one whose bytes changed. Keep the original mod version when correcting its
package; publish the new archive before deploying its updated manifest hash.
`make check`
compares the catalogue with each recipe's identity and display fields and
checks any available local ZIP's size, SHA-256 and full embedded config.
`--local` requires all current ZIPs to be available; `make check-mods-remote`
downloads and checks every current release asset against the same recipe.
The published catalogue copy must also equal its source. To withdraw a mod,
remove its current catalogue entry and recipe. Older original mod versions
may stay hosted, but packaging revisions of the same version are replaced.

## About page

`content/about.md` supplies metadata and `layouts/_default/about.html` tells the
project’s story, research process, technology choices, and current priorities.
Creator-supplied retail research captures live in `static/images/about/`; their
provenance is recorded in `ASSETS.md`. Keep status claims aligned with the engine.

## Renderer features page

`data/features.json` supplies nine chapters and a concise renderer overview.
Still comparisons support mouse/touch, keyboard and whole-view presets. The zoom
slider chooses freshly rendered camera stops rather than scaling a screenshot;
it fetches only requested/neighboring views. The live material study supports
rotation, tilt, light orbit and finish controls, with poster/native-movie fallback.
The live water study uses original transport/submarine geometry, textures, native
terrain and the real shoreline field, with four independent WebGL treatments.
The final aircraft chapter compares native ordinary/soft shadows at two heights.
`assets/css/features-refresh.css` scopes the marketing layout to this page.

`/gameplay/` remains the server-rendered player guide, supplied by
`data/gameplay.json`. Current media lives in `static/images/renderer/v6/`;
`scripts/renderer-capture/v6/README.md` records engine pins, reproduction and audit
evidence. Material-study provenance remains in
`scripts/renderer-capture/live-materials/README.md`. Water and aircraft provenance
live in `scripts/renderer-capture/live-water/README.md` and
`scripts/renderer-capture/aircraft-shadows/README.md`. The ordinary website build
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
