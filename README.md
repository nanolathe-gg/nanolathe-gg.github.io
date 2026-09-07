<picture>
  <source media="(prefers-color-scheme: dark)" srcset="static/brand/wordmark.svg">
  <img src="static/brand/wordmark-light.svg" alt="Nanolathe" width="420">
</picture>

The homepage and documentation gateway for **[nanolathe.gg](https://nanolathe.gg)**.
Built with Hugo, maintained in `nanolathe-gg/nanolathe-gg.github.io`, and deployed
as the organization's default GitHub Pages site.

## Run locally

Install [Hugo Extended 0.160.0 or newer](https://gohugo.io/installation/), then:

```sh
hugo server
```

No Node packages or Go web server are required. Font and image assets are served
locally. Production builds use Hugo 0.160.0, pinned in the Pages workflow.

## Build and verify

```sh
hugo --gc --minify --panicOnWarning
python3 scripts/check-site.py
```

The Python check uses only the standard library and verifies required pages,
internal links, anchors, local assets, and the custom-domain file. Pull requests
build and validate without deploying. Pushes to `main` deploy through GitHub
Actions; generated `public/` output is not committed.

## Content and maintenance

- `hugo.toml`: engine repository, branch, source availability, site metadata.
- `content/`: page titles, descriptions, and route selection.
- `layouts/`: the homepage and page content for this first release.
- `data/references.yaml`: the complete v0 directory of format and behavior docs.
- `assets/css/site.css`, `assets/js/site.js`: styling and progressive enhancement.
- `static/brand/`: reusable marks and wordmarks, including PNG exports.
- `static/CNAME`: `nanolathe.gg`.

The engine is moving to `https://github.com/nanolathe-gg/nanolathe`. Links and
clone commands already target that destination. **Set `sourcePending = false`
in `hugo.toml` once the engine repository is public** to remove the temporary
publication notices. Website work does not change the engine repository's origin.

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

`wordmark.svg` and `wordmark-light.svg` have outlined lettering, so they render
without installed fonts. `avatar.png` is a 512-pixel square for GitHub.
`wordmark.png` is a transparent 2× raster export. Favicon and Apple touch icons
are included. The geometric N has separated construction segments and three
assembly particles. Read [ASSETS.md](ASSETS.md) for font and artwork provenance.

To regenerate the SVG brand assets, install `fonttools` in a temporary Python
environment and run `python scripts/brand.py`. The checked-in exports are ready
to use; rebuilding them is not part of the site build.

## Deployment

The repository name `nanolathe-gg.github.io` makes this the organization's default
site. GitHub Pages must use **GitHub Actions** as its publishing source, with
`nanolathe.gg` set as the custom domain and HTTPS enabled once GitHub provisions
the certificate. The custom domain also lives in `static/CNAME` for portability.

## License

Website code and original brand geometry: [MIT](LICENSE). The bundled Chakra
Petch font uses the SIL Open Font License in `static/fonts/OFL.txt`. No original
Total Annihilation game assets are included. Game data must be obtained separately.
