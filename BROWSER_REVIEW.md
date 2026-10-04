# Browser demo integration — October 4, 2026

Local preview: http://127.0.0.1:1313/ · Direct play: http://127.0.0.1:1313/play/.
Worktree: `/Users/daniel/Documents/Codex/2026-10-03/task/nanolathe-website`.
Branch: `redesign/private-beta-local`. Main and other checkouts are preserved.
This review supersedes the earlier future-demo layout notes in `LOCAL_REVIEW.md`.
Nothing was pushed, merged into main, deployed or published by this task.

## Result

The local branch integrates `browser-play`, including its immutable-release
fetcher at `dea48603d9d1eb092fb50467ec752cc47731b989`, with the beta redesign,
Resources removal and fresh native Features captures. The homepage, navigation,
Features and Get started now link directly to `/play/`. A supported desktop
browser downloads/verifies the demo and starts the first ARM mission immediately.
There is no launch page requiring a second button click.

The running game accepts a dropped TotalA folder, including drops onto its
iframe and in fullscreen. The toolbar also offers Choose game folder. Imported
files remain local handles; no upload is performed. The website bridge creates
parent-owned File handles before retiring the old iframe, so reads remain live
after a source switch. Initial pointer coordinates are seeded at the canvas
center until a real pointer event arrives, preventing an uninitialized cursor
from edge-scrolling away from the opening battlefield. This sends no game click
or order. The Back to launcher button and launch landing section are removed.
Only a compact recovery panel appears when startup fails or the browser cannot
play; it offers retry, local folder selection and native installation help.

Missing capabilities, mobile/tablet detection, a missing manifest, download
failure, startup failure or another active game tab expose usable controls and
native installation help. Unsupported mobile/tablet browsers do not automatically
download WASM. The engine's one-runtime-per-origin lock, persistence behavior,
source selection and diagnostics remain in its pinned host modules.

The project identity is an MIT-licensed, open-source RTS engine. Total
Annihilation is its current focus and a concrete way to try it. Homepage engine
cards, About, Features, the documentation directory and brand description retain
both. The technical format documentation and install commands are preserved.
Modern GPU is the standard website presentation; Classic is optional. This task
does not modify engine Go code, renderer/simulation defaults or host launch flags.

## Exact playable build

The engine was pushed and published separately while this work was in progress.
No additional engine-main push is currently needed. The local website now uses
the actual public [browser-210 release](https://github.com/nanolathe-gg/nanolathe/releases/tag/browser-210),
built from `ee99287993e29c8569144e0e37c3f13418c4b6da`, rather than the earlier
local-only `163d8d2f` preview. The newer published host includes browser camera
pan/pinch gestures. It was fetched before the final launcher-removal acceptance
run; all 16 checks below exercise this exact release.

- Build version: `ee99287`; host: `host.3cd7885104e8355c`.
- WASM: `nanolathe.5f30e70c3913b54f.wasm`, 47,988,452 bytes.
- WASM SHA-256: `5f30e70c3913b54ffd78e01dbe3295437102ac1728485b5572d28b16a3de8cc9`.
- Go runtime: `wasm_exec.0c949f4996f9a896.js`.
- Original demo archive: `TADemo.hpi`, 20,474,804 bytes,
  SHA-256 `fd53a2637ecf8fb5ca6d2c02a34b4ef783a4441f8be070137276afc4d5627e1e`.
- Original readme: `TADemoReadme.txt`, 24,279 bytes,
  SHA-256 `193b7e2a0aa3cce48d8554a4a101d55408817f821f184396266e764a0cc5fdfb`.

The verified asset-free snapshot is retained in `../published-browser-210`.
An ignored LOCAL marker keeps this exact tested build in the local preview;
`PLAY_REFRESH=1` fetches the newest public release again. CI ignores that marker
and continues to discover the newest complete published release.

The two original files come from the website's published
[demo release](https://github.com/nanolathe-gg/nanolathe-gg.github.io/releases/tag/demo)
and are pinned in `data/play.json`. The original readme is retained unchanged.
Archive/manifest release checksums, the WASM size/digest, gzip content, host
directory hash, Go runtime hash and both demo file digests are checked. Hashed
engine modules are unmodified; only the root launcher receives the website shell.
CI requires verified engine and demo assets for every build, so it cannot publish
a playable-demo promise with a placeholder. The optional dispatch token speeds
website refresh; a six-hour schedule provides the fallback.

Generated WASM/demo files remain in ignored `static/play/`, `.cache/play/` and
`public/`. No retail archive, game binary or demo archive is committed. Fetching
assets for local review does not publish the website. Engine release publishing
is complete; website publication still requires Daniel's later approval.

## Verification and evidence

`make check` passed with Hugo Extended 0.160.0: 29 HTML documents and their
internal links/anchors/assets, CNAME, 34 platform assertions, eight build/shell
regressions, three release-selection/checksum tests, all 15 format generators,
installer checksums, four catalogue entries, nine mod packaging tests, four
multipart tests and 16 offline installer tests. PowerShell is unavailable;
native Windows offline checks remain skipped by the repository's gate.

Isolated Chrome 154.0.8037.97 passed 16 browser-demo checks and 31 layout checks:
homepage click to actual WASM gameplay without another launch click, fresh local
folder import through the game iframe, the toolbar directory picker, Modern and
Classic restarts, native fullscreen/exit and alert placement, the second-tab lock,
absence of the launcher UI, cached reload without archive requests, three forced acquisition/startup
failures and mobile/tablet/no-locks/no-JavaScript fallbacks. The six engine
sessions reached advancing ticks with 34 units at 800×600. There were no
JavaScript errors or upload requests. Runtime checks use headless software WebGL
and do not establish hardware performance.

Folder-drop QA uses synthetic browser directory entries containing the actual
verified demo bytes, dispatched over the real running iframe. The directory
picker uses real files. Full retail folder import and physical OS drag-and-drop
still need Daniel's manual check. Mission completion, a prolonged playthrough,
real browser save round trips and Edge/Safari/Firefox remain unverified. Mobile
layouts are Chromium emulation. The engine supplies camera gestures; complete
mobile controls and mobile performance remain unverified.

The refreshed Features page passed another 10 layouts, six still comparisons
with mouse/touch dragging, keyboard and presets, 10 movie checks, 22 media
requests, reduced motion/no-JavaScript fallbacks and navigation/back. Its v5
capture files and provenance are unchanged by this integration. The browser uses
original texture detail (`--auto-remaster=false`); synthesized terrain in native
Features and homepage captures is labeled separately. The exact native capture
source/settings/hashes are in `scripts/renderer-capture/v5/README.md` and v4's
README. No browser gameplay screenshot is a substitute for those native captures.

Local evidence is under `../qa/`:

- `browser-demo-final-make-check.log`, `browser-integration-report.json`,
  `browser-integration-check.cjs`, and `browser-demo-artifact-provenance.json`.
- `browser-demo-public-fetch.log`, `browser-ci-status.json`,
  `browser-host-check.log` (34 JS and three Python engine checks), and
  `browser-wasm-build.log` (the earlier asset-free local preview build).
- `browser-install-integration-report.json` and its script: eight OS-hint
  scenarios, manual override, clipboard and ownership; unsupported mobile
  install links do not prefetch WASM.
- `features-refresh-browser-report.json`, `features-refresh-check.cjs` and
  `browser-demo-features-check.log`.
- `integrated-home-desktop.png`, `integrated-home-mobile.png`,
  `integrated-demo-direct-game.png`, `integrated-demo-local-folder.png`,
  `integrated-demo-fullscreen.png`, `integrated-demo-mobile.png` and the
  three forced-error screenshots. Older failed/intermediate test reports and
  screenshots are historical; these final reports define the accepted state.

The detached Hugo preview disables live reload to keep it from interrupting the
WASM session. It remains available on loopback port 1313. To reproduce locally:

```sh
PLAY_REFRESH=1 make check
hugo server --bind 127.0.0.1 --port 1313 --disableFastRender --disableLiveReload --renderToMemory
```

Browser acceptance scripts use Codex's bundled Playwright and an isolated Chrome
process, with no user profile. Run them from this task's `qa` directory while the
preview is active. They create test demo files and screenshots outside the website
repository. Publishing is not part of the reproduction commands.

## Follow-up site cleanup

Get started now has one browser-demo entry and one three-step native setup flow.
The repeated second installation article, duplicate command panels and obsolete
alpha migration note are removed. Detailed requirements, folder selection,
updates, saves, logs, troubleshooting and source builds live in the new
`/docs/native-installation/` player guide. Existing step/help fragments remain
usable; links to collapsed requirements automatically reveal that section.
The native-install heading is visible on phones as well as desktop.

The documentation directory discovers player guides and computes its counts.
About and the homepage distinguish Nanolathe's MIT-licensed code from the demo
and full-game assets, and avoid an unsupported multiplayer roadmap commitment.
Browser help refers to the current game toolbar, and brand page patterns describe
the beta layouts and Markdown player guides. Long technical-reference source
URLs wrap, and narrow comparison diagrams stack, keeping the document viewport
at the requested phone width. Technical reference text and evidence snapshots,
installers, capture files and pinned engine modules are unchanged.

`make check` passed again: 30 HTML files and their internal destinations,
34 platform assertions, browser build/demo integrity and shell regressions,
all 15 format example generators, catalogue/package checks and all 16 offline
installer tests. The final strict build, site-link check and browser-integrity
check passed after the CSS refinements. PowerShell remains unavailable, so
native Windows offline tests remain skipped.

Isolated Chrome 154 passed 135 layout checks: all 27 non-play HTML routes at
320, 390, 768, 1024 and 1440 pixels, with eager image decoding, unique IDs,
one H1, no broken images, no page overflow and no mobile viewport enlargement.
Setup tests cover all platform commands and clipboard values, ownership changes,
old anchors, details expansion, guide TOC/navigation/back, mobile navigation,
brand copy controls and no-JavaScript commands. All eight OS-hint scenarios
passed again, including phone/tablet/ChromeOS/unknown manual selection. There
were no JavaScript errors. Focused checks at 320, 390 and 1440 pixels confirm
the FBI yard preset still produces all 16 cells, the TDF assignment controls
still give 9 → 7 → 9, and wide GAF tables can be scrolled with the keyboard on
phones. These are Chromium layout emulations, not device
performance measurements; the earlier playable-build acceptance and remaining
manual gameplay gaps above still apply.

Current evidence in `../qa/`:

- `site-cleanup-make-check.log`, `site-cleanup-final-build.log`,
  `site-cleanup-check.cjs`, `site-cleanup-report.json`, and
  `site-cleanup-platform-check.log`; `site-cleanup-diagrams-check.cjs` and
  `site-cleanup-diagrams-report.json` cover the interactive diagram checks.
- `cleanup-get-started-1440.png` and `cleanup-get-started-390.png`;
  `cleanup-docs-native-installation-1440.png` and
  `cleanup-docs-native-installation-390.png`.
- `cleanup-home-*`, `cleanup-about-*`, `cleanup-docs-*` screenshots with their
  images decoded. Older overflow diagnosis logs are intermediate evidence;
  the final layout report checks the actual requested viewport widths.

The local preview is still available at http://127.0.0.1:1313/.
Nothing was pushed, merged into main or published during this cleanup.
