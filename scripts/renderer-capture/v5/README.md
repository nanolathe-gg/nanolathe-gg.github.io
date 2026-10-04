# Fresh native Features captures

Engine source: `279f7af159a7d33ffd16358d1133434d9d48c7b9`, local main pinned
at capture start on October 3, 2026. Diagnostic branch:
`capture/features-refresh-v5`. The isolated capture worktree is
`/Users/daniel/Documents/Codex/2026-10-03/task/nanolathe-features-capture`.
The final diagnostic harness commit is `bd950b7a73165eb78e3fe7e5c380f7cccefe5295`.
The capture harness adds no production renderer or simulation changes.

The page uses these actual engine scenes:

- Greenhaven camera demonstration: 38 original units with settled COB poses,
  held at staged placements. The real camera moves from 2× detail to 0.25×
  tactical view, panning from the base to the opposing forces. Every frame is
  freshly rendered; this is a camera demonstration, not combat footage.
- Greenhaven terrain: the same Modern draw path and 2× camera compare original
  terrain tiles with real synthesized tiles. Synthesized feature banks remain
  constant, so the control changes only terrain detail.
- Great Divide explosion: a Jeffy self-destructs beside a Bulldog in an ordinary
  staged session. Classic CPU and Modern GPU read the same committed
  publication, tick and camera. This compares whole rendering paths, including
  Modern terrain, feature artwork, anti-aliasing and presentation effects.
- Gods of War coast and transport: normal committed wind animates a unit-free
  shore, while a separate ARM transport follows session movement and COB wakes.
  Paired views toggle water effects or reflections respectively. Native model
  height and reflection opacity remain unchanged.
- Comet Catcher material turntable: an original ARM mobile Annihilator retains
  its frozen activated pose while a copied view heading rotates. Paired frames
  switch materials and glints together. Native 512×512, 2× camera, without a crop.
- Matched model lineup: original mobile units and an Annihilator building share
  poses and camera in Classic CPU and Modern GPU, both with anti-aliasing enabled.
  This is a whole-path comparison, not an isolated anti-aliasing toggle.

All other stills and movies are native 960×640. The website preserves the
capture aspect ratios and scales them to the viewport. No still has been
resized, cropped, retouched, sharpened, composited or recolored. Videos encode
native frames without frame interpolation or effect amplification. Motion is
opt-in, with native controls and direct media links; switching a paired clip
preserves its playback position.

## Synthesis and renderer provenance

The harness calls the real terrain cache API with production default parameters
and the runtime named-feature-bank loader. Cache payloads, cold/warm equality,
2× dimensions and differences from nearest doubling are audited. Shadow and
missing sprite variants retain the client’s documented fallback. The terrain
comparison holds feature artwork constant; the explosion’s full-path comparison
includes real synthesized feature artwork.

Modern frames execute on Metal; Classic pixels come from the indexed software
composer and palette expansion. The session comparisons record committed input
hashes, matching camera state and the production presentation CRT handoff.
Draw-list counts and effect settings are recorded in the diagnostic evidence.
Staged camera and material scenes use their own identified seeded presentation
state, separately from ordinary session movement.

The original capture executables were rebuilt during diagnostics, and their
historical binary hashes were not retained. After capture, backend guards were
added to the harness. Four bounded probes reported actual Metal, and eight
first-frame replays matched the original PNG bytes. `binary-probes.json` records
those later probe binaries only; `REPORT.md` explains the source chronology.
Production source stayed pinned throughout, and the final source, raw frames,
scene metadata and website exports have recorded hashes.

The source harness and its reproduction commands are in `source/`. Its producer
report and verification files retain exact scene placement, controls, raw-frame
hashes and media metadata. Raw frames and synthesis caches stay outside the
website at `/Users/daniel/Documents/Codex/2026-10-03/task/capture-features-v5/`;
retail archives and generated texture banks are not bundled.

## Website exports

Run from the website checkout after producing the verified artifact directory:

```sh
python3 scripts/renderer-capture/v5/prepare-web-media.py /path/to/capture-features-v5
```

The packager exports 13 PNGs with `cwebp -lossless -exact -z 9`, then decodes PNG
and WebP to RGBA and requires matching pixel hashes. It copies all 9 MP4s
unchanged and verifies the copy hashes, decoded frame counts, durations, codecs
and dimensions. `webp-export-verification.json` records the pixel proof;
`website-media.json` inventories only the 22 files served in
`static/images/renderer/v5/`. The producer’s raw manifest is separate.

`verification.json` records ten passing capture audit groups. Focused diagnostic
build/package checks and Go vet passed; all nine movies also passed full decoding
and frame-count checks. Native capture used Apple M3 Pro graphics, Ebitengine
2.10.4 and macOS 26.6.2. The source bundle includes no retail archives, raw image
sequences, synthesis payloads or executable binaries.

The website build needs neither retail data nor a GPU. Reproduction needs the
pinned isolated engine checkout, the installed game data and normal macOS
graphics access; read the installed Ebitengine headless-running skill first.
These captures are presentation diagnostics, not performance measurements.
No engine main changes, publication or deployment are part of this refresh.

The capture revision is local and has not been pushed. Page source links therefore
point to the published engine `main`, explicitly labeled as published source,
while the capture pin and exact reproduction evidence remain recorded here.
