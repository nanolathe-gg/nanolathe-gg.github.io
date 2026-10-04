# Local beta redesign review — October 3, 2026

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

The new comparison is a matched native 960×640 explosion pair at committed
tick 132 and the same 2× camera. Modern uses verified real 64×64 terrain tiles
synthesized from original 32×32 tiles, default modern lighting/glow and other
presentation effects. Foliage is explicitly nearest-doubled fallback. Both
renderers bind the production presentation CRT and consume the same unchanged
publication. Lossless WebP pixels equal the original PNG pixels exactly.
Features also provides matched 2-second, 30 FPS opt-in clips. Exact settings,
hashes, cold/warm cache proof and reproduction commands are in
`scripts/renderer-capture/v4/README.md` and its JSON evidence. No retail
archives, derived tile cache or engine binary were bundled.

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

Machine-readable browser results, build log, full-page/viewport screenshots,
comparison close-ups, preview process details and restart logs are in
`/Users/daniel/Documents/Codex/2026-10-03/task/qa/`. Raw captures and controls
remain in `../capture-output/`; no captures were retouched or composited.

## Review boundaries

Both original main checkouts remain clean. No unrelated local work was changed.
No push, merge, deploy, DNS change or publication was performed. Those actions
require Daniel's later approval. The local preview is left running for review.
To restart it if necessary, run the loopback Hugo command documented in README.
