> Latest review: the October 4 feedback pass replaces the current homepage and
> Features scenes with v6 captures, restores the interactive material study,
> adds documentation icons and supports desktop Safari based on Daniel's test.
> See the final section of BROWSER_REVIEW.md and scripts/renderer-capture/v6/README.md.
> The v4/v5 descriptions below are historical.

# Local beta redesign review — October 3, 2026

October 4 update: see [BROWSER_REVIEW.md](BROWSER_REVIEW.md) for the current
playable demo integration, direct launch, engine/source positioning and final
verification. It supersedes the future-demo layout notes below. Resources was
removed and Features retains the native v5 capture refresh.

Preview: http://127.0.0.1:1313/ (loopback only; detached Hugo process).
Website worktree: `/Users/daniel/Documents/Codex/2026-10-03/task/nanolathe-website`.
Branch: `redesign/private-beta-local`, based on `907e1e2`.
Engine capture worktree: `/Users/daniel/Documents/Codex/2026-10-03/task/nanolathe-capture`.
Branch: `capture/private-beta-comparison`, diagnostic commit `0ff16de5`, based on
`ac32756e0caffbc37e0fb80b21c03d3c641f1d21`.

## What is ready

The latest seven-route prototype bundle was integrated into Hugo, using its
homepage, installation flow, dark/lime visual language and interaction design.
Home, Features, Get started, About, Documentation and Brand share
the updated appearance and an obvious Install the beta action. The 15 native
format guides, player references, renderer studies, installer scripts, mod
catalogue and full brand kit remain in the existing architecture. Marketing
CSS is scoped to keep the technical references readable. The source Library
identity and ZIP checksum are recorded in the v4 capture README.

The page uses Public beta and modern GPU rendering as the standard experience;
Classic is optional. Engine runtime defaults were not changed. The future
browser-demo toggle is expressly a layout study with no playable demo.
OS selection uses low-entropy browser hints locally; mobile/tablet, ChromeOS
and unknown hints leave commands unselected. Visitors can manually select
Windows, Mac or Linux. Ownership choices, installer text, copying and the
unsigned beta notice remain visible and accurate. No installation command
was executed during website/browser QA.

The homepage comparison is a matched native 960×640 explosion pair at committed
tick 132 and the same 2× camera. Modern uses verified real 64×64 terrain tiles
synthesized from original 32×32 tiles, default modern lighting/glow and other
presentation effects. Foliage is explicitly nearest-doubled fallback. Both
renderers bind the production presentation CRT and consume the same unchanged
publication. Lossless WebP pixels equal the original PNG pixels exactly.
The initial Features revision used matched 2-second, 30 FPS opt-in clips. Exact settings,
hashes, cold/warm cache proof and reproduction commands are in
`scripts/renderer-capture/v4/README.md` and its JSON evidence. No retail
archives, derived tile cache or engine binary were bundled.

Features has now been rebuilt around six fresh chapters: camera, terrain,
lighting, water, surfaces and model edges. Native captures pin current local
engine source `279f7af159a7d33ffd16358d1133434d9d48c7b9`. Its isolated diagnostic
worktree is `../nanolathe-features-capture`, branch `capture/features-refresh-v5`.
The capture-only harness commit is `bd950b7a73165eb78e3fe7e5c380f7cccefe5295`.
All production engine files and runtime defaults remain unchanged.

The page uses 13 pixel-identical lossless WebP stills and nine unchanged MP4s.
The runtime terrain cache and named-feature-bank loader provide actual 2×
synthesized artwork; shadow and missing variants retain the normal fallback.
The terrain control changes only terrain tiles through the same Modern path.
Classic/Modern explosion and model-lineup comparisons identify the full rendering
paths. Camera and material turntables identify their staging. Most images are
native 960×640; the material turntable is native 512×512. Videos are 30 FPS,
three seconds for the explosion and six seconds for the other scenes.
No image was resampled, cropped, composited or retouched. Exact settings,
source, controls and hashes are in `scripts/renderer-capture/v5/README.md`.
Original capture binary hashes were not retained after diagnostic rebuilds.
The final harness, pinned production sources, original frames and exports have
hash evidence; later guarded binaries are explicitly identified as probes.
Their Metal first-frame replays match the original bytes. The producer report
documents this provenance limitation.
The old browser material study is retained as historical source and no longer
loaded by Features. The homepage retains v4 captures.
The unpublished engine capture revision is recorded exactly in the evidence;
page source links explicitly browse the published engine main to avoid dead
links to a local commit.

## Verification

- Initial `make check` passed with Hugo Extended 0.160.0. Checked 26 HTML pages, internal
  routes/anchors/assets, CNAME, all 15 format generators, installer consistency,
  mod catalogue, 9 packaging tests, 4 multipart tests and 16 offline installer
  tests. All 34 platform detection/selection assertions passed. PowerShell is
  unavailable: native Windows offline tests were skipped by the repository gate.
- Initial isolated Chrome 154.0.8037.97 tested nine routes at 1440×1000 and 390×844:
  seven marketing routes, GAF reference and keyboard shortcuts. All returned
  200; no broken images, duplicate IDs, horizontal overflow or JavaScript errors.
- Pointer and keyboard comparison controls, Classic/Split/Modern taps, dialog
  Escape/close cleanup, future-layout disclosure, mobile navigation/back,
  eight OS-hint scenarios, manual override, clipboard and ownership toggles passed.
- Both new matched H.264 clips actually played locally, including renderer
  switching. JavaScript-disabled installation commands, reel-link fallback
  and full-video download links passed. The prior native water clip also played
  in the initial browser pass. External YouTube reel playback was not verified;
  the iframe URL/open/close and direct YouTube fallback were checked.
- Additional layouts on five main routes at 320, 768, 820 and 1024px showed
  no horizontal overflow. QA uses Chromium emulation; Safari, Firefox and
  physical iOS/Android devices were not tested.
- Capture build, focused diagnostic package checks, go vet, GPU capture/export
  assertions, hashes and visual inspection passed. Whole-engine integration
  and performance gates were not run for this capture-only diagnostic, which
  is not being landed into engine main. No performance claim is made.
- Daniel requested removing Resources. Its page, header/footer links and unused
  styles were deleted. A clean Hugo build and the internal-link gate passed on
  the remaining 25 HTML pages. Desktop/mobile browser checks passed on six
  marketing routes plus GAF, including menu/back navigation and no overflow;
  `/resources/` returns 404 after restarting the local preview. Evidence is in
  `qa/resources-removal-browser-report.json` and `qa/resources-removed-*.png`
  alongside the other QA artifacts below.
- Fresh Features `make check` passed: 25 HTML pages, all format generators,
  platform assertions, installer consistency, mod catalogue and offline fixture
  tests. PowerShell remains unavailable, so native Windows tests were skipped.
- Isolated Chrome 154.0.8037.97 passed ten Features layouts, including 320–1920px,
  desktop/mobile, JavaScript-disabled and reduced-motion contexts. All six
  mouse/touch/keyboard comparison checks, ten actual movie playback checks,
  variant switching, Replay, fallbacks, navigation/back and 22 media requests
  passed. No overflow, duplicate IDs, broken images or JavaScript errors occurred.
  `qa/features-refresh-browser-report.json`, `qa/features-refresh-make-check.log`
  and `qa/features-v5-*.png` hold the evidence. Chrome emulation does not verify
  Safari, Firefox or physical mobile devices.

Machine-readable browser results, build log, full-page/viewport screenshots,
comparison close-ups, preview process details and restart logs are in
`/Users/daniel/Documents/Codex/2026-10-03/task/qa/`. Raw captures and controls
remain in `../capture-output/` (v4) and `../capture-features-v5/` (Features);
no captures were retouched or composited.

## Review boundaries

Both original main checkouts remain clean. No unrelated local work was changed.
No push, merge, deploy, DNS change or publication was performed. Those actions
require Daniel's later approval. The local preview is left running for review.
To restart it if necessary, run the loopback Hugo command documented in README.
