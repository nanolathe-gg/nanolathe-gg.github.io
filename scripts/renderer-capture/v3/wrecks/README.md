# Real unit-death wreck cooling capture

Base engine commit: `801c8b28c38ff6505b4939d96cce7fcf22200da5` (landed main). Only `cmd/website-wreck-capture/` is added; no simulation, renderer, assets or shader production files changed. The previously approved CPU/lighting captures are unchanged.

## Deliverables

- `wrecks-off.mp4` / `wrecks-on.mp4`: matched 960×640 H.264/yuv420p videos, 390 frames at 30 FPS, **13 seconds at normal simulation speed**. No audio.
- `wrecks-off.png` / `wrecks-on.png`: matched frame-80 posters, 2.667 seconds into the clip / 1.667 seconds after corpse birth.
- `raw/`: both original 480×320 native captures at **2× camera zoom**, plus per-frame event/metadata/counter records.
- `decoded-off/`, `decoded-on/`, `qa-{raw,decoded}-{off,on}.png`: nine keyframes spanning live tank, death, warm wreck, cooled material and shimmer expiry, including frames 329/330 at the exact expiry boundary.
- `media.json`: full ffprobe stream/container data and framing. `verification.json`: birth/expiry and equality assertions. `manifest.json`: SHA-256 and file sizes, including source, media, original/decoded frames and logs (excluding itself).

All public images use the identical crop `(120,70,240,160)` of each 480×320 render and a **4× nearest-neighbor enlargement** to 960×640. The engine genuinely renders model geometry at 2×; the final enlargement only exposes those existing pixels. No blur, recoloring, relighting or detail invention is applied in export.

## Actual scene and birth evidence

Great Divide, scene center `(1636,2084)`, one ARM Stumpy (`armstump`), simulation seed 12345 and CRT seed 67890. The ordinary session retains its two commanders at distant starts. A local fixture clearing uses the existing feature-removal lifecycle; other terrain stays authored. The camera is fixed.

At warmup step 30, an ordinary `Combat.AcceptDamage` packet removes 892 health, leaving 100. The session continues normally so the engine's prior-health severity sample settles. At capture frame 30 an ordinary 101-damage packet lethally hits that tank. This deliberately avoids self-destruct's 30,000-damage packet, whose normal COB severity may pulverize the corpse. Neither health words, COB return values nor corpse selection are overwritten. Ordinary `Session.Step`, COB Killed and successful `PlaceCorpse` generate the actual `armstump_dead` feature.

The first committed corpse appears at **tick 120 / frame 30**, with `WreckBornTick=120`, `WreckHeatKnown=true`, actual physical position/orientation, `RuntimeLive=true` and visible anchor. No corpse, birth age, model geometry or effect animation is synthesized. The real existing explosion and smoke art can obscure the first pale-hot frames; that occlusion is retained. The wreck treatment itself does not create smoke, and this capture adds none.

The 13-second clip covers committed ticks 90–479. Death occurs one second into the video. The hot material cools to its original texture at age 180 (6 seconds after death / frame 210). Wreck shimmer falls to zero at age 300 (10 seconds after death / frame 330). The final two seconds show the expired treatment and unchanged original material.

## Matched comparison and isolation

Both sides use the modern GPU renderer with AA enabled. Before the next simulation step, the harness records the same committed publication twice. OFF suppresses only `FeatureView.WreckHeatKnown` in the borrowed presentation view; ON restores the actual published value. Both draw lists are deep-cloned. After recording, original metadata is restored and the committed frame's SHA-256 must equal its pre-recording digest. This does not write the simulation or invent a timestamp.

Battle lighting, bloom, explosion distortion, metal glints, new §29 material finishes, new §29 scorch, coastal water effects and reflections are disabled through the existing executor controls. The shared `SetTreeHeat(true)` switch must remain enabled to execute wreck shimmer, but **no tree plume is admitted**: every frame verifies `HeatPlumes == WreckHeatPlumes`. Both output modes verify zero `BlastWaves`, `GlowPasses`, `BattleLights`, `MaterialFaces`, `ScorchQuads` and `ReflectionVertices`.

One ON wreck plume is submitted on frames 30–329; OFF submits none. The first real model operands are emission `[0.9,0.75,0.43499997]`, heat strength `0.55`, scale `2`. Strength decreases every tick using the unchanged engine formula. Emission is exactly zero from frame 210; no heat operands or plume remain from frame 330. Native OFF/ON PNG pixels are **exactly identical before death and at every frame from 330 through 389**. The original feature's known birth metadata remains published after the renderer's effect expiry; known birth does not imply an active effect.

The GPU glow is subtle by design after the initial blast: the visible hull is orange/red at the poster and cools naturally. No shader gains, age remapping, slow motion or contrast boosts were applied to make it stronger. Grass behind the hull exposes the air shimmer. This documents the real landed behavior and its actual occlusion, not an unobscured synthetic material preview.

## Reproduction and validation

Read the repository AGENTS.md, INVARIANTS and DESIGN_GPU_RENDERER §28–29, and the module's `skills/run-ebitengine-app-headless/SKILL.md`. As in the approved prior captures, use a hidden real GPU context and finish bounded rendering/readbacks within one Draw callback to avoid the known macOS hidden Metal host-present issue.

```sh
GOMAXPROCS=2 go build -p 2 -o /private/tmp/nanolathe-feature-v3-wrecks-media/capture ./cmd/website-wreck-capture
GOMAXPROCS=2 /private/tmp/nanolathe-feature-v3-wrecks-media/capture -out /private/tmp/nanolathe-feature-v3-wrecks-media/raw
python3 cmd/website-wreck-capture/export.py
```

Retail content defaults to `/Users/daniel/TotalAnnihilation`; no retail data is included in harness source. Encoding uses two threads, CRF 17, slow preset, and faststart. A short 70-frame probe confirmed genuine birth before the full run. Go build, normal capture termination, all 390-frame state/control/birth/expiry assertions, ffprobe frame count/duration, raw equality at expiry, and raw/decoded visual keyframe review passed. Raw and decoded sequences show the explosion, cooling hull and settled endpoint. No benchmark or engine-wide suite was run because no production engine behavior changed. No commit, merge or publishing was performed.
