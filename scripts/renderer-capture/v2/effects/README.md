# Real simulation effects capture

Engine base: 9e61946a64ee96619551579ecddf4786f7865c9d. Sources are in this output directory and in the isolated engine worktree's cmd/website-effects/main.go. No engine behavior or renderer shaders modified. No image-generated or composited visual effects.

Retail VFS root: /Users/daniel/TotalAnnihilation. Map: Great Divide. Both simulation RNG seeds explicit: 12345 and 67890. Fixture center: (1636, 2084). Original commanders remain at their distant start locations to preserve a normal skirmish lifecycle; they are outside the capture camera. The computer commander can run ordinary simulation outside the view. Selected clearing features removed via the feature lifecycle service; surrounding terrain and tree detail is retail-authored. Camera hides HUD and supplies all-visible presentation coverage during drawlist recording, then restores the committed visibility snapshot. No effect or unit snapshot fields are staged.

All output: 960x640, 150 frames, 30fps, 5 seconds, H.264 yuv420p, faststart. One Session.Step per frame: ticks 90–239. Initialization advances 90 host steps so COB Create/Activate is settled. The captured trigger is at frame30 (1 second), before tick120. Event evolution is real time; no retiming, skipped simulation ticks, or drawn overlays. Looping repeats the scene and resets to its starting state at the loop boundary.

* `shockwave-off/on`: one visible ARM Bulldog (armbull, objects3d/ARMBULL.3do) killed by combat.ApplySelfDestructDamage, using its authored BIG_UNIT self-destruct weapon. Real destruction publishes named fx.gaf explosions, whole-piece debris and fragment events; 3 shockwaves run for the original 14 nonzero-strength ticks. On/off differ only by Renderer.SetBlastDistortion.
* `lighting-off/on`: two visible units, ARM Bulldog and ARM Jeffy (armfav, objects3d/ARMFAV.3do). Jeffy dies through the same real self-damage entry using SMALL_UNIT. Bulldog survives and its surfaces receive warm light. Native enhanced 2x camera. On/off toggle Renderer.SetBattleLighting and Renderer.SetGlow together. Both preserve ordinary authored flash discs. No overwhelming battle crowd.
* `fire-off/on`: zero visible units; three architree01 features placed through Features.PlaceAt. Actual art: architrees.gaf palm01 / palm01flame. At frame30, Features.Ignite(cell,1,0) starts each normal burning lifecycle. Their real fire cursor, smoke puffs and spread events advance via Session.Step. Three actual renderer heat plumes accompany the fire. On/off differ only by Renderer.SetTreeHeat.

The harness installs the same presentation effect timing resolver and fragment material resolver as cmd/nanolathe/battle.go. Authoritative feature GAF sequence timing and smoke frame count remain the ordinary session composition bindings. Geometry and ordinary effects are recorded once per tick; both comparison renders execute that identical cloned drawlist. Per-frame events.jsonl includes exact effect identifiers, source slots, source coordinates, start ticks, live burn counts and off/on renderer counters.

Build:
```
GOCACHE=/private/tmp/nanolathe-feature-v2-effects/go-cache go build -o /private/tmp/nanolathe-feature-v2-effects/capture ./cmd/website-effects
```
Run from the worktree, outside the sandbox so macOS Metal is available:
```
/private/tmp/nanolathe-feature-v2-effects/capture -scene lighting -frames 150 -out /private/tmp/nanolathe-feature-v2-effects/lighting
/private/tmp/nanolathe-feature-v2-effects/capture -scene shockwave -frames 150 -out /private/tmp/nanolathe-feature-v2-effects/shockwave
/private/tmp/nanolathe-feature-v2-effects/capture -scene fire -tree architree01 -frames 150 -out /private/tmp/nanolathe-feature-v2-effects/fire
python3 /private/tmp/nanolathe-feature-v2-effects/export.py
```

GPU method: read Ebitengine v2.10.1 run-ebitengine-app-headless skill before execution. The capture is a hidden native Ebitengine window, performs all GPU readbacks in one Draw call to avoid a macOS Metal host-present crash, and uses the production gpurender renderer. Sparse diagnostic runs preceded each final capture; no performance benchmarks ran.

Final completion QA (2026-09-12): rebuilt the latest existing harness and reran
lighting to apply its corrected centered camera. Bulldog and dying Jeffy now
occupy the central area of the frame. Shockwave/fire source frame sequences were
already complete and retained. Exported every off/on pair with bounded two-thread
ffmpeg, CRF18; all six outputs verified by ffprobe: H.264, 960×640, 30/1fps,
150frames, exactly5seconds. `media.json` stores sizes, hashes and ffprobe results.
`verification.json` records counter ranges, comparison image bounds and frame
counts. `qa/` contains decoded video keyframes used for visual inspection.

The paired sources are pixel-identical before the trigger. On/off peak counters:
lighting LitModelFaces 0→33 (57 active frames); shockwave BlastWaves 0→3
(14 active frames); fire HeatPlumes 0→3 (120 active frames). Fire renders zero GPU
model subjects throughout its sequence; original commanders outside the view
remain in the full-session unit census. The rising model-subject counts during
explosions include authentic destruction fragments, not extra staged units.
Lighting also records up to12 lit smoke sprites. Lighting comparison toggles both
battle lighting and glow, as described above. Ordinary flash effects are present
in both states and account for the bright base explosion even with the
presentation enhancement off.

Visually inspected off/on poster source frames, decoded H.264 keyframes and later
fire frames. No shader or tracked engine source changed. The driver build passes;
no engine integration or performance suites were rerun for this media-only work.
