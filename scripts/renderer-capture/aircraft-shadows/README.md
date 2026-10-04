# Native aircraft shadow comparison

Production engine `617540c587e1b75d6d8ba7bf5243d24bea3f3bc2`, actual Metal,
Greenhaven, native960×640,2× camera, committed publication tick100. Two original
CORE Hurricane models (`corhurc`) use their activated original COB poses, heading9000,
and clearances60/180 world units above the ground. The presentation fixture omits
vegetation so both shadows remain visible. Heights are authored for this frozen
renderer study; it does not claim to simulate takeoff or flight.

The client records one drawlist with aircraft placement metadata at the default
`ShadowSoftness=100`. The native renderer executes that same clone with only
`SoftShadows` on and off. Warmup occurs before pixel capture. On/off/on restores
byte-identical pixels; the committed publication remains unchanged. All other
treatments, model positions, poses, terrain synthesis and camera remain identical.
The images are uncropped, unretouched, native-size captures. Lossless/exact WebP
matches decoded PNG RGBA exactly. No amplified blur or composited comparison.

Copy `source/` to an isolated pinned-engine checkout's
`cmd/website-features-capture/shadows/`, alongside v6's `common/`, and build/run:

```sh
go build -o /tmp/nanolathe-shadows ./cmd/website-features-capture/shadows
EBITENGINE_GRAPHICS_LIBRARY=metal caffeinate -u -t 60 /tmp/nanolathe-shadows
```

The diagnostic command currently names Daniel's installed retail directory and
local artifact/cache paths, matching the other v6 capture fixtures. Adjust those
paths for a different local install. Raw outputs are `../capture-aircraft-shadows/`;
private retail archives and caches stay outside the website. `verification.json`
records settings, metadata, actual aircraft clearances and exact-restoration proof.
`producer.json` records source/binary/log hashes. `website-media.json` records
served-file hashes and native pixel equality. This command is local diagnostic
work, not an engine-main/runtime change or a performance benchmark.

The final isolated diagnostic sources are saved locally at
`6c0cfd983f2d082b69fbdda0027811432a07a10f`; binary/source hashes identify the exact pre-commit builds.
