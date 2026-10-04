"""Verify the published browser build and demo under public/play."""
import json
import os
import sys

import playbuild as pb

required = os.environ.get("PLAY_REQUIRED") == "1"
if (pb.STATIC / pb.UNAVAILABLE).is_file():
    if required:
        sys.exit("play: the browser build was required but only the placeholder was fetched")
    if not (pb.PUBLIC / "index.html").is_file():
        sys.exit("play: the placeholder page was not published")
    print("play: placeholder published; the engine's browser build was unavailable")
    sys.exit(0)
if not (pb.STATIC / "build.json").is_file():
    sys.exit("play: static/play has neither a build nor the placeholder; run scripts/fetch-play.py")
if (pb.PUBLIC / pb.UNAVAILABLE).is_file():
    sys.exit("play: public/play still holds a stale placeholder; rebuild with make build")
manifest = pb.check_manifest(json.loads((pb.PUBLIC / "build.json").read_text()))
if manifest != json.loads((pb.STATIC / "build.json").read_text()):
    sys.exit("play: public/play/build.json differs from static/play; rebuild with make build")
problems = pb.verify_build(pb.PUBLIC, manifest)
demo_problems = pb.verify_demo(pb.PUBLIC)
if demo_problems == ["demo/manifest.json: missing"] and not required:
    print("play: no demo assets published; the launcher offers local import only")
else:
    problems += demo_problems
if problems:
    print("\n".join(problems), file=sys.stderr)
    sys.exit(1)
print(f"play: build {manifest['version']} ({manifest['wasm']}) and demo assets verified under public/play.")
