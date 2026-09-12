# Real CPU / GPU website comparison capture

Engine base: `774f79c69288d1fe706d3a4bb2769e5814045331`. Capture-only executable; no renderer or simulation production files changed. Based on the existing website v2 effects harness. Assets are read from `/Users/daniel/TotalAnnihilation`; none are copied into source.

## Outputs and viewing

`aa-cpu.png`, `aa-gpu.png`: 960×640 PNG pair. Four mobile units (Bulldog, Maverick, Zeus, Merl) and one building (Annihilator), with matching committed COB pieces and presentation-only diagonal headings. Native 480×320 capture at **1× camera zoom**, cropped at x=120,y=70,width=240,height=160 and enlarged **4× nearest neighbor**. Both files use the exact same rectangle and filtering. This enlargement makes original framebuffer pixels inspectable; it does not add detail. Native frames are retained in `raw-aa/`.

`lighting-{cpu,gpu,glow}.mp4` and matching `.png` posters: 960×640, H.264/yuv420p, 30 FPS, 150 frames, exactly 5 seconds, no audio. Same native size, crop and enlargement as AA. Poster frame 34 (1.133 seconds). CPU and GPU are the primary comparison; `glow` is an optional third view with ordinary modern bloom enabled. There are no captions baked into images.

## CPU path proof and honest AA distinction

CPU uses a separate `client.Client`, `SetEnhanced(false)`, `SetAntiAlias(true)` and `ComposeFrameSnapshot()`. At this revision `internal/client/client.go`'s `composeCurrentFrame()` executes `list.Replay(c.classicSink())`, then the classic sink expands the **software indexed framebuffer** through the palette. The PNG copies that returned CPU RGBA. GPU execution is not used to produce CPU pixels.

Every captured CPU frame records 153,600 indexed bytes and nonzero completed `Classic` model planes. Every modern list records **zero Classic planes**, and AA's five visible model packets all carry supersample geometry. `internal/client/model_compose.go: supersampleModel` gates CPU AA to structures; `supersampleGeometry` covers modern model subjects. This follows DESIGN_GPU_RENDERER §17: CPU retains structure-only AA; GPU performs full-unit supersampling. Both switches are true, recorded per frame.

CPU and modern rendering have existing raster/compositing differences in addition to modern AA and lighting. This pair is not a claim of pixel equality outside the named feature.

## Lighting event and controls

One ordinary seeded Great Divide session (simulation seed 12345, CRT seed 67890) places a Bulldog at scene-center x−34 and a Jeffy at x+35. Two original commanders remain at distant starts to keep the session alive. Scene center is 1636,2084. The same nearby clearing removal as v2 uses the feature lifecycle API. After 90 warmup steps, capture covers ticks 90–239. At frame 30, `Combat.ApplySelfDestructDamage` initiates Jeffy death, followed by ordinary `Session.Step`; explosion art, fragment motion, corpse and their lifetimes are entirely engine-produced. The Bulldog survives. No synthetic explosion, shader gain, effect lifetime or light-radius change is made.

One committed publication is recorded by both clients before the next step. A SHA-256 digest is made before rendering and checked unchanged after both recorders finish. Frame logs include that shared state digest, rendered unit poses, effects, counters and CPU pixel hash. AA headings and full visibility are presentation-only overrides, restored afterward. Unit piece slices come directly from the current committed publication; no staged slices are retained across buffer reset. Modern draw lists are deep-cloned before GPU execution.

Modern lighting is ON; **blast distortion, tree/wreck shimmer, metallic glints, water effects and reflections are OFF**. Glow is OFF for the primary GPU output and ON only in `glow`. Wreck heat/emission birth metadata is suppressed in the borrowed presentation snapshot for both recorders, then restored; this prevents the separate wreck-cooling feature from contaminating the lighting comparison. All effect source art remains. Classic has no modern distortion path.

A third internal control replays the **same modern draw list** with battle lighting OFF for frames 28–50. At frame 34 the lighting change affects 1,557 native pixels in the surviving Bulldog's receiver crop [187,128,228,180]; its changed bounding box is [183,128,275,180]. Peak light count is five and peak lit model faces is 33. Primary GPU counters verify zero BlastWaves, HeatPlumes, WreckHeatPlumes, GlowPasses and ReflectionVertices throughout all 150 frames. This isolates surface lighting from bloom and distortion, despite unavoidable CPU-vs-GPU baseline raster differences.

## Reproduce

From this worktree (Go build and encoding restricted to two CPU threads):

```sh
GOMAXPROCS=2 go build -p 2 -o /private/tmp/nanolathe-feature-v3-cpu-media/capture ./cmd/website-cpu-capture
GOMAXPROCS=2 /private/tmp/nanolathe-feature-v3-cpu-media/capture -scene aa -out /private/tmp/nanolathe-feature-v3-cpu-media/raw-aa
GOMAXPROCS=2 /private/tmp/nanolathe-feature-v3-cpu-media/capture -scene lighting -out /private/tmp/nanolathe-feature-v3-cpu-media/raw-lighting
python3 cmd/website-cpu-capture/export.py
```

The Ebitengine module's `skills/run-ebitengine-app-headless/SKILL.md` was read first. This capture uses its hidden real-GPU context principle and verifies actual PNG outputs. The established macOS workaround renders and reads every bounded frame in one `Draw` call, then terminates before host presentation can hit the known hidden Metal drawable crash. The capture is diagnostic; it is not a frame-time benchmark.

`media.json` contains complete ffprobe streams/container data. `verification.json` contains CPU-path and same-list lighting-control checks. `manifest.json` hashes all deliverable media, raw frames, logs and source files (except itself). Final AA images, CPU/GPU/glow posters and temporal contact sheets were visually inspected. Tests/benchmarks beyond the capture build and output checks were not run because this is a capture-only presentation harness, not an engine change.
