# Native Features media v5 — capture report

Completed locally on2026-10-04. All six requested feature subjects have fresh real-engine media. Capture production pin: **279f7af159a7d33ffd16358d1133434d9d48c7b9**. Capture-only harness commit: **bd950b7a73165eb78e3fe7e5c380f7cccefe5295**, branch `capture/features-refresh-v5`, isolated checkout `nanolathe-features-capture`. The checkout is clean; its diff from the production pin contains only13files in `cmd/website-features-capture/`. Main advanced independently to `b1e3b5ef` during the task and was preserved. No runtime defaults, renderer coefficients, production packages, website files, retail archives, shared checkout state, or publishing changed.

Original final-frame file writes run from **2026-10-04T04:08:38.920875+00:00** through **2026-10-04T04:26:58.535452+00:00**. Dates are actual file-write times in UTC, recorded for every frame; they are not invented EXIF metadata. Metal probes and packaging ran afterward. Engine pin is local/unpublished; published-main source links must not be presented as this exact revision.

## Final media

The website-selected set is13native PNGs and9MP4s at the artifact root; six supplemental PNGs provide landscape whole paths,1×AA, and camera normal/end views. `manifest.json` maps every poster to its original raw file, its encoded SHA256 and RGBA pixel SHA256. **1473original raw PNGs** are inventoried in `raw-png-manifest.json`; no resampling, crop, compositing, image-generation, or pixel enhancement was used.

| Chapter | Selected root names | Native size / cadence | Scene and control |
|---|---|---|---|
| Light and impact | explosion-classic/modern PNG+MP4 |960×640;90frames,30fps,3s | Great Divide, seeds12345/67890, normal Session.Step after staged placement; Jeffy self-destruct frame30. Same publication and camera, Classic indexed CPU versus Modern GPU full default effects and synthesized art. Poster42/tick132. |
| Terrain | terrain-original/synthesized PNG |960×640 | Greenhaven at4250,4040, same Modern path; only Terrain Tiles nil versus real synthesized tile payload. Same synthesized feature banks and26submitted synthesized sprite commands in both. |
| Camera and tactical | camera-tactical PNG+MP4 |960×640;180frames,30fps,6s |38staged units with original COB poses. Actual camera starts2×at4100,4340 and pans400world pixels while smoothly zooming to0.25×; default strategic view/icons draw38markers at end. Poster0 shows full outpost; normal/end supplemental stills supplied. |
| Water | reflection-off/on PNG+MP4; water-off/on PNG+MP4 |960×640;180frames each,30fps,6s | Gods of War, seeds7/7, camera2×at2719,704. Real queued transport movement and Session.Step. Reflection pair toggles only WaterReflections; quiet shore pair toggles WaterSurface/Motion/Foam/Reflections, retains other default controls and original map art. |
| Armor and materials | materials-off/on PNG+MP4 |512×512;180frames,30fps,6s | Explicit staged original ARM model `armmanni`, original COB poses, one turn at2×camera. Same cloned drawlist off/on; only Finish/Glint toggle. Scorch=false on both. Original map art, no synthesis installed. Poster35. |
| Smooth model edges | aa-classic/modern PNG |960×640,2×camera | Five-model staged tableau, same publication/camera. Anti-Alias=true on both; Classic retail structure AA versus Modern Supersample=true. Whole paths also differ in synthesized terrain/foliage/materials. Supplemental native1×pair uses original art through production scale selection. |

## Exact presentation settings and evidence

Core and camera use `drawlist.AllEffects()`: WaterSurface, WaterMotion, WaterFoam, HovercraftLandWash, WaterReflections, ModelLight, GroundLight, Finish, Glint, BlastRings(distortion), FireShimmer(tree heat), WreckGlow, WreckShimmer, Scorch, SoftShadows, Supersample=true. Weapon/Explosion/NanoGlowStrength and ShadowSoftness=100. Glow=true, GlowStrength/GroundLightStrength/BlastRingStrength=100, master/vehicle/shading=true, Anti-Alias=true. Classic ignores Modern effect selection and uses its real software indexed composition. Water uses these defaults except the stated off control; materials disable only Scorch in both and Finish/Glint in off. Production tuning constants are untouched.

Core session clients bind private presentation CRT copies through `Session.PresentationCRT()` and `SetPresentationCRT`; water uses the same production binding. Camera/material fixtures bind a private seeded CRT through the public API. Both paths audit publication immutability; no global CRT hook or simulation RNG supplies presentation. Core's full-visibility and AA-heading overrides are matched capture inputs and restored after recording. The AA fixture removes a burnt successor with the feature lifecycle API to keep model edges visible.

Explosion poster42:14battle lights,3ground lights,55glow quads,52lit model faces,2blast waves,40material faces. Tree/wreck heat is enabled but HeatPlumes=WreckHeatPlumes=0 at that poster, so no active plume is claimed.16GPU geometry packets include11flying fragments;5model-subject packets contain supersample lanes. There are no Classic model planes in the Modern list. Separate same-list raw glow-off and light+glow-off controls exist at frames30–42; poster42's light+glow control changes93997pixels versus full Modern.

Reflection on records260–296reflection vertices, off0; ship position and heading change through real queued movement. Every30thwater/reflection frame passes exact off/on/off restoration, and all180publications remain unchanged. Materials pass exact first-frame off/on/off restoration and all180same-list/publication audits; poster35 has10material faces and changes3188/262144pixels. Reflection poster90 changes11424/614400pixels. These are subtle native effects at the shipped coefficients, especially at mobile width; no strengthened demonstration setting is hidden.

## Real2×texture synthesis

`internal/upscale.Cache.Tiles2x`, algorithm `nanolathe.upscale.terrain.2`, produces32×32→64×64indexed tiles. Default parameters: Iterations8, Samples100000, Tone12, Spread16, Deadzone8, Seam0, SeamZone-1, Coherence64, Settle2, Relax=true; Workers2 only caps work. The harness validates decoded on-disk `NLUPSCALE` magic, kind1, payload version1, count, exact pixel body, cold/cached byte equality and hashes. Cache files stay private under `/tmp` and are not bundled.

| Scene | Tiles | Output pixels different from nearest doubling | Tile-payload SHA256 |
|---|---:|---:|---|
| Great Divide |2820 |8214833/11550720(71.12%) |09671871a0eccb73a836456c05900379e1a5e0c2c2e6231cbf7c72a03ddc4b83 |
| Greenhaven |2347 |6451478/9613312(67.11%) |a751878221dd3dc48ec1bef689ed7a20562fdc9a7cebe84411c9c34d56bff210 |

Great Divide cache SHA256 is7bffc7b898af496f85ff23699628d09acba37bb720f663a7794c5b76c29c1f79(11550741bytes); Greenhaven is a5ef2379c156abf66ff22be38006249afe42a873676655d765428646a6299f37(9613333bytes). Per-scene `synthesis.json` records exact paths, parameters, calls and payloads.

Foliage has independent `Cache.Bank2x` evidence, algorithm `nanolathe.upscale.bank.2`, following the runtime loader's named-map-bank coverage. Default sprite parameters: Iterations8, Tone64, Deadzone0, Seam8, Coherence32, Coverage200000, Mismatch12288, Closeness1728, Tie2, Relax=true, ClampEdges=false. Example-only exclusions are burn/boom/fire/smoke/rec. Dimensions and anchor offsets2×, output indexed pixel hashes, non-nearest counts and identical cached output are checked per synthesized nonnil frame. Drawlist pointer identity proves actual use:87synthesized sprite commands at explosion poster42,26in both terrain controls, and synthesized sprites in camera detail view followed by0at tactical scale.

| Map | Bank | Synthesized frames | Changed indexed pixels versus nearest doubling |
|---|---|---:|---:|
| Great Divide |geotherm / rocks / trees |1 /4 /22 |0 /26002 /44672 |
| Greenhaven |geotherm / greenvents / rocks / rockshurt / trees |1 /6 /6 /5 /19 |0 /7174 /30215 /11045 /39957 |

Normal fallback remains for shadow twins, unqueried entries, missing variants, and unsupported empty/composite/unrepresentable-anchor frames. The tiny geotherm stub goes through synthesis but has0changed pixels, so the report does not claim every frame adds detail. Camera zoom and texture-synthesis scale are recorded separately; original tiles/sprites are selected at≤1×as production intends. Water/material scenes deliberately hold original map art in both controls.

## Verification, source chronology, and import

Focused builds, `go test -p2 ./cmd/website-features-capture/...`, `go vet -p2`, Python/shell syntax and `git diff --check` pass. Ten audit groups pass in `verification.json`, including same inputs/cameras, CPU decoded pixel hashes, Modern geometry, synthesis payloads, independent sprites, actual tactical markers, off/on/off controls, CRT binding, native sizes and unchanged production sources. All9MP4s pass ffprobe and independent full decoding with exact dimensions,30fps,90/180frames and3/6s durations. Frame-decoder hashes are in the nine `*-decoded.framemd5` files. Native keyframes for every subject/control plus camera detail/normal/end were visually inspected. These bounded single-Draw offline diagnostics make no performance claim; whole-engine landing/performance gates were not requested.

**Source chronology limitation:** production source was pinned throughout at279f7af1. The initial capture harness was uncommitted while being adapted; original capture executables were overwritten during builds and their historical binary SHA256values were not retained. The final source commit above is the reproducible capture-only harness, not an asserted historical hash of every movie-capture executable. After media capture, `ReadDebugInfo` Metal guards and camera's bounded `-limit` probe were added; these do not change scene generation or selected pixels. All four entrypoints positively reported actual=Metal in bounded probes, and eightfirst-frame off/on/terrain/cameraPNG replays match the original captured bytes exactly. `binary-probes.json` gives the exact hashes/build metadata of those **post-capture guarded probe binaries**, clearly scoped, and is not labeled as original-capture binary provenance. All production-file checksums are in `verification.json`.

Import these final evidence files with the selected media: `REPORT.md`, `manifest.json`, `raw-png-manifest.json`, `verification.json`, `binary-probes.json`, `metal-hardware.json`, `host-version.txt`, `checks.log`, `vet.log`, `export.log`, `backend-*.log`, per-scene raw `events.jsonl`/`census.json`/`metadata.json`/`movies-metadata.json`/`synthesis.json`, the nine decode checksum files, and `source/`(exact13-file source copy with manifest checksums). Raw full frames remain available locally under `raw/`; no retail archives, source GAF/model art, synthesis cache payloads or executable binaries are in the source/evidence bundle. Hardware evidence identifies Apple M3 Pro18cores, Metal supported; actual API probes identify Metal. No blocking capture gaps remain beyond the historical executable-hash limitation stated above.
