## Voice and layout review — October 12, 2026

Preview this checkout at [127.0.0.1:1314](http://127.0.0.1:1314/). The existing
server on 1313 serves an older checkout. To restart this preview from the current
repository:

```sh
hugo server --bind 127.0.0.1 --port 1314 --disableFastRender --disableLiveReload --renderToMemory
```

This pass responds to the [numbered-card feedback](https://news.ycombinator.com/item?id=50046607)
and the [broader presentation feedback](https://news.ycombinator.com/item?id=50046424).
Replies also called out repeated two-part phrasing, excessive cards and labels,
and tiring prose. These are editorial observations, not a reliable test of how
a site was produced.

The writing reference is Daniel's existing project documentation, with the
perspective of a longtime TA player explaining a spare-time project. The
homepage has a signed project note; About uses Daniel's first person, based on
the personal history already in that page. Elsewhere, copy describes the game,
the controls and the current limitations directly. The AI-development disclosure
remains explicit. The reusable rules and source links live in
[the brand guide](brand/GUIDE.md#writing-voice).

The homepage now goes from the game footage to the renderer comparison, then
the project note, beta status and questions. The numbered benefits, three
engine pitch cards and repeated install/research pitches are removed. Features,
Get started, About, the documentation index, Gameplay and Brand also have
rewritten headings and introductions. Technical format references and research
snapshots retain their precise language.

### Second editorial pass

- Read all rendered headings in sequence and checked their supporting text.
  Removed repeated slogan pairs and labels that restated their headings.
- Removed decorative feature/brand numbering. Installation steps remain
  numbered because they have an order. Research URLs keep their original IDs.
- Replaced generic phrases with specific descriptions: “A blast. A wreck. A
  slow cool.” became “Wrecks cool after a kill”; “Your first battlefield starts
  here” became “Play Nanolathe.”
- Checked captions, metadata and accessibility text as well as visible headings.
  Updated leftover video labels and shortened the duplicated camera caption.
- Kept the distinctions between native captures and browser studies, original
  artwork and synthesized detail, the demo and full-game data, and beta support
  and known limitations. First-person copy does not add biographical events.
- Retained the established green palette, logo, actual engine footage and
  functional comparison controls. Reduced repeated marketing sections rather
  than replacing the visual identity.

### GitHub writing samples and independent review

The follow-up used Huma, Restish and API Sprout as writing references. In
addition to current READMEs and Huma tutorials, it read the
[Huma README from September 2022](https://github.com/danielgtaylor/huma/blob/2d1984f84fc0e535404e7dc79435bf066c9f64b6/README.md)
and the [Restish guide from May 2022](https://github.com/rest-sh/restish/blob/204e653bc7b81bb0b94d3018c9e9d4899c6a569c/docs/guide.md).
The GitHub history identifies Daniel as the author of those two revisions.
That does not establish authorship of every line in collaborative repositories.

The recurring habits were direct instructions, explanations of why a feature
works that way, concrete examples, useful parenthetical details and occasional
enthusiasm. The resulting voice is friendlier and more explanatory than the
first pass. It does not try to copy incidental typos, insert a catchphrase or
ban normal lists and punctuation.

A separate reviewer was started with `fork_turns="none"`, without the parent
conversation or the proposed persona. It read all seven main pages and the
desktop preview. Its findings led to these changes:

- Gameplay's repeated heading/summary/four-bullet grid became a reading column
  with a contents sidebar. Game modes and online play come first. Qualifiers
  such as “authored” and “eligible” were replaced with specific explanations,
  while content requirements and compatibility limits remain.
- Homepage and About copy now explain the author's choices in ordinary first
  person. About makes the time and effort point once, and contribution guidance
  explains what to include in a bug report.
- Feature captions describe what is visible. Timing, frame rates and capture
  dimensions remain in the expandable capture details. Comparison instructions
  no longer repeat the adjacent controls' instructions.
- Documentation counts appear once per section. The incomplete-reference note
  only appears when there are missing local guides. Brand download copy no
  longer repeats the heading and button.

For example, “Limited supplies affect the work the economy can admit” became
“Shortages limit how much work can proceed,” in a paragraph explaining when
resources are spent. The reviewer specifically recommended keeping the
Jeffy/Bulldog example, MacBook origin, factory scripts, AI disclosure and actual
numbered installation sequence.

The reviewer checked the revised pages again and caught one lost qualification:
alliances can change with players outside your lobby team, while lobby teams
last for the whole battle. That distinction has been restored. The follow-up
found no other consequential editorial issues or clear changes of meaning.

### Verification

- Hugo 0.160.0 builds with `--panicOnWarning`; the generated-site check passes
  for 31 HTML pages, internal destinations, anchors, local assets and CNAME.
- The existing checks pass for platform selection, demo startup and recovery,
  browser assets, all 15 format fixtures, installer checksums, map/mod catalogues,
  browser fetch fixtures and package assembly.
- `make check` initially failed five terminal-dependent installer assertions
  inside the sandbox. Rerunning the unchanged offline installer suite outside
  the sandbox passed all 19 tests. PowerShell is unavailable, so Windows offline
  tests were not run.
- In-app browser layout checks cover all seven rewritten pages at 1440, 390
  and 320 pixels wide. Each has one H1, no duplicate IDs, no horizontal overflow
  and no broken loaded images. No console errors appeared during those checks.
- Checked the camera's whole-map control, Classic/Split comparison presets,
  installation platform and ownership choices, and opening/dismissing the mobile
  menu with Escape. Tablet review exposed an existing gap between
  the navigation and menu breakpoints; both now switch at 820 pixels. Confirmed
  the menu opens and shows its links at 708 pixels.
- Visually reviewed the desktop homepage and Features, the project note,
  mobile installation, narrow About, and tablet navigation. These checks use
  the in-app browser, not physical phones or every supported game browser.
- After the GitHub-based follow-up, repackaged the brand guide, rebuilt Hugo
  with warnings treated as errors, and reran the generated-site and whitespace
  checks. Checked the six pages changed in that follow-up at 1440, 390 and 320
  pixels: one H1 each, no duplicate IDs, no horizontal overflow and no broken
  loaded images. The new Gameplay guide was also inspected visually. Its mobile
  contents links reach the selected heading, and the camera and comparison
  preset controls still update their selected state. No browser console errors
  appeared. Capture files, source references, viewer parameters and all camera
  frames are unchanged.

This review was completed locally before the owner approved publication.
The ignored `.cache/voice-review/` directory contains the responsive-layout
results and screenshots of the project note and revised Gameplay guide.

---

> Earlier follow-up: extractor alignment corrected, live water animation/controls
> added with native fallback, and a ninth aircraft soft-shadow chapter added.
> See the latest section of [BROWSER_REVIEW.md](BROWSER_REVIEW.md) for current
> checks, evidence and remaining gaps. The earlier sections below are history.

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
