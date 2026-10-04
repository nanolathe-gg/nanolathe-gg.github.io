# Homepage hero: current modern GPU battle

Captured October 4, 2026 from production engine
`e2ac78cda2a19ff77fb8ee04a6ed32fc8f2e8819`, the local main revision at capture
start. The isolated worktree is `../nanolathe-hero-capture`, branch
`capture/homepage-modern-hero`. Capture-only diagnostics are saved locally at
`25e956d1202fc097251f75958fa5fe8183a432b8`; they observe the actual backend,
recorded art and executor statistics after production GPU readback. The
attached patch changes no renderer, shader, simulation, data or default.

The existing production `--film` route builds this staged Greenhaven battle
using the ordinary Session, unit definitions, movement orders, weapons, COB
scripts and construction. Seed 7, heavy roster, 24 requested mobiles per side,
6 columns, spacing 36, half-gap 160, two rear buildings, factory production,
three additional aircraft and one builder per side are in `hero.json`.
The stager places 40 units and skips 20 unplaceable units. After 300 lead-in
ticks, the film publishes tick 301 and records frame 0 at interpolation fraction
0. This is the production presentation of the 300–301 interval, rather than a
claim that every interpolated subject uses the current tick's pose. The census
and state hash describe the current publication, tick 301.

The camera is fixed at 2×, centered at scene anchor `(4280,4230)` plus offset
`(-55,-70)`. The script reveals the scene, disables shake, silences the message
ring and requests the clean viewport. Its existing film crop copies the native
1280×880 world viewport from surface 1408×944 at `(128,32)`, removing only
interface chrome. There is no additional image crop, rescaling, retouching or
compositing. Original healthy tree sprites surround the battle; no tree art
has been substituted. The capture is an illustrative battle, not a toggle pair.

The actual backend is Metal. Enhanced rendering, AA, interpolation, feature
and unit shadows, glow, all modern effect families and normal 100% strengths
are enabled through the production film route. Its actual detail loader uses
an input-keyed local synthesis cache: the drawlist audit confirms 2347 real
64×64 terrain tiles and 45 synthesized feature-sprite commands. Shadow and
missing sprite variants retain the ordinary fallback. The GPU execution reports
57 model subjects, 34 battle lights, 21 ground-light discs, 24 flash commands
and 5 glow passes. Exact full statistics, source/binary hashes and controls
are in `manifest.json` and `capture.log`.

`static/images/renderer/hero-modern-e2ac78cd.webp` is a lossless export of
the local `capture-home-hero/hero-300/frame000000.png` under the task directory. Both decode to identical RGBA
SHA-256 `4380514ad6748c7f7d37497e6fe09189122e396bd893bd78c1da4bbd2f76a7e8`.
The filename changes so existing browser caches fetch the fresh hero. The prior
unused `hero-battle.webp` is retired; its original hash and crop remain in
`../initial-review/media-manifest.json`.

## Reproduce locally

Use an isolated engine checkout at the production revision, apply
`capture-diagnostics.patch`, and read the engine's `AGENTS.md`,
`docs/FILM_CAPTURE.md` and installed Ebitengine headless-running skill. On macOS,
a display context is required even though the production film hides its window.
Do not include retail archives, synthesis caches, raw sequences or executables
in the website repository or a deliverable bundle.

```sh
GOCACHE=/tmp/nanolathe-capture-gocache GOMAXPROCS=2 \
  go build -p 2 -o /tmp/nanolathe-home-hero ./cmd/nanolathe

# This assertion wakes the display briefly without changing persistent settings.
caffeinate -u -t 60 &
XDG_CACHE_HOME=/tmp/nanolathe-home-hero-cache \
XDG_CONFIG_HOME=/tmp/nanolathe-home-hero-config \
EBITENGINE_GRAPHICS_LIBRARY=metal \
  /tmp/nanolathe-home-hero \
  --root "$HOME/TotalAnnihilation" --renderer modern --auto-remaster=true \
  --film /path/to/website/scripts/renderer-capture/home-hero/hero.json \
  --film-out /tmp/nanolathe-home-hero-frames --film-frames 1

cwebp -lossless -exact -q 100 -m 6 \
  /tmp/nanolathe-home-hero-frames/frame000000.png \
  -o hero-modern-e2ac78cd.webp
```

The result cache is optional; a fresh loader synthesizes the art from the same
installed data. The original producer was built before its source-only local
commit, so it stamps the production revision and `modified=true`. The recorded
binary hash and source hashes identify that exact producer.

## Local review

The hero was visually inspected in native output and at desktop/mobile sizes.
Headless Chrome checks all five widths (320, 390, 768, 1024 and 1440), native image
dimensions and served bytes, the eager hero request, page overflow, all loaded
images, direct `/play/` CTA and home comparison mouse/touch/keyboard controls.
`browser-verification.json` holds the full local report;
screenshots live in the sibling local `../qa/` directory. `make check` passes
with terminal access for the offline installer PTY fixtures; PowerShell is unavailable, so Windows-specific
offline tests are skipped. Engine diagnostic build and `go vet ./cmd/nanolathe`
pass. Physical Safari/mobile checks of this image refresh were not repeated.
Nothing is pushed or published; the Hugo preview remains at
`http://127.0.0.1:1313/`.
