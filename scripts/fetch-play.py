"""Place the engine's browser build and the demo assets under static/play.

The engine's rolling "browser-latest" release carries nanolathe-browser.tar.gz
and its build.json; this repository's "demo" release carries the original
demo archive and readme, pinned by digest in data/play.json. style-play.py then
decorates the root launcher; Hugo serves static/play at https://nanolathe.gg/play/,
keeping the pinned engine modules and demo files at the required same origin.

Normal runs also keep the one build that is live at nanolathe.gg/play/, so a
launcher opened before a deployment can still restart its pinned host
directory, Wasm and runtime (engine docs/DESIGN_BROWSER_HOST.md §4).

When the engine release cannot be obtained, the live build is mirrored; when
neither exists, a placeholder page is written. PLAY_REQUIRED=1 (or
--required) turns those fallbacks into failures, which the website workflow
sets for every CI build.

  --local DIR      use a local tools/browser-build output instead of the release
  --demo-root DIR  take the demo files from an extracted demo folder (digests still apply)
  --compare-live   only report whether the release differs from the live site
"""
import argparse
import io
import json
import os
import shutil
import sys
import tarfile
import urllib.request

import playbuild as pb

USER_AGENT = "nanolathe-website-play"


def fetch(url, limit=pb.LIMIT):
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=120) as response:
        data = response.read(limit + 1)
    if len(data) > limit:
        raise ValueError(f"{url}: larger than {limit} bytes")
    return data


def write(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)


def release_manifest():
    engine = pb.PINS["engine"]
    return pb.check_manifest(json.loads(fetch(engine["release"] + engine["manifest"], 1 << 20)))


def release_build(out):
    """Download, verify and unpack the rolling release into out."""
    engine = pb.PINS["engine"]
    manifest = release_manifest()
    cached = pb.CACHE / f"nanolathe-browser.{manifest['sha256'][:16]}.{manifest['host']}.tar.gz"
    if cached.is_file():
        archive = cached.read_bytes()
    else:
        archive = fetch(engine["release"] + engine["archive"])
        write(cached, archive)
    expected = pb.members(manifest)
    seen = set()
    with tarfile.open(fileobj=io.BytesIO(archive), mode="r:gz") as tar:
        for member in tar:
            name = member.name
            while name.startswith("./"):
                name = name[2:]
            if member.isdir() or name in ("", "."):
                continue
            if not member.isreg() or name not in expected or member.size > pb.LIMIT:
                raise ValueError(f"{engine['archive']}: unexpected member {member.name}")
            write(out / name, tar.extractfile(member).read())
            seen.add(name)
    if json.loads((out / "build.json").read_text()) != manifest:
        raise ValueError("the archive's build.json differs from the released manifest")
    problems = pb.verify_build(out, manifest)
    if problems:
        raise ValueError("released build: " + "; ".join(problems))
    print(f"play: engine build {manifest['version']} ({manifest['wasm']})")
    return manifest


def local_build(out, source):
    manifest = pb.check_manifest(json.loads((source / "build.json").read_text()))
    for name in sorted(pb.members(manifest)):
        write(out / name, (source / name).read_bytes())
    problems = pb.verify_build(out, manifest)
    if problems:
        raise ValueError(f"{source}: " + "; ".join(problems))
    # A later plain run keeps this preview unless asked to refresh (main).
    write(out / pb.LOCAL, f"{source}\n".encode())
    print(f"play: local engine build {manifest['version']} ({manifest['wasm']})")
    return manifest


def live_manifest():
    return pb.check_manifest(json.loads(fetch(pb.PINS["live"] + "build.json", 1 << 20)))


def copy_live(out, manifest, names):
    for name in names:
        write(out / name, fetch(pb.PINS["live"] + name))
    problems = pb.verify_build(out, manifest)
    if problems:
        raise ValueError("live build: " + "; ".join(problems))


def mirror_live(out):
    manifest = live_manifest()
    copy_live(out, manifest, sorted(pb.members(manifest)))
    print(f"play: mirrored the live build {manifest['version']} ({manifest['wasm']})")
    return manifest


def retain_previous(out, manifest):
    """Keep the live build's hashed files beside the new build, if it differs."""
    try:
        live = live_manifest()
    except Exception as error:  # noqa: BLE001 - any failure means nothing to retain
        print(f"play: no live build to retain ({error})")
        return
    if live["wasm"] == manifest["wasm"] and live["host"] == manifest["host"]:
        return
    added = []
    try:
        for name in sorted(pb.members(live) - {"index.html", "build.json"}):
            if (out / name).exists():
                continue
            write(out / name, fetch(pb.PINS["live"] + name))
            added.append(out / name)
        data = (out / live["wasm"]).read_bytes()
        if len(data) != live["size"] or pb.sha256(data) != live["sha256"]:
            raise ValueError(f"{live['wasm']}: live bytes differ from the live manifest")
    except Exception as error:  # noqa: BLE001 - retention is best effort
        for path in added:
            path.unlink(missing_ok=True)
        print(f"play: previous build not retained ({error})")
        return
    print(f"play: retained the previous build {live['version']} ({live['wasm']})")


def demo_assets(out, demo_root):
    for row in pb.demo_rows():
        name, size, digest = row["path"], row["size"], row["sha256"]
        cached = pb.CACHE / f"{digest}-{name}"
        if demo_root:
            matches = [p for p in demo_root.iterdir() if p.is_file() and p.name.lower() == name.lower()]
            if not matches:
                raise FileNotFoundError(f"{demo_root / name}")
            data = matches[0].read_bytes()
        elif cached.is_file():
            data = cached.read_bytes()
        else:
            data = fetch(pb.PINS["demo"]["release"] + name, 64 << 20)
        if len(data) != size or pb.sha256(data) != digest:
            raise ValueError(f"{name}: size or digest differs from data/play.json")
        if not cached.is_file():
            write(cached, data)
        write(out / "demo" / row["url"], data)
    write(out / "demo/manifest.json", (json.dumps(pb.demo_manifest(), indent=2) + "\n").encode())
    print("play: demo assets verified")


def placeholder(out):
    write(out / pb.UNAVAILABLE, b"The browser build was unavailable when this site was built.\n")
    write(out / "index.html", b"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Play Nanolathe in your browser</title>
<style>body{margin:0;min-height:100vh;display:grid;place-items:center;background:#101419;color:#dce4e8;font:16px system-ui;text-align:center}a{color:#9edbbe}</style></head>
<body><main><h1>The browser build is not published yet</h1>
<p>Check back soon, or <a href="/get-started/">install Nanolathe</a> to play now.</p></main></body></html>
""")
    print("play: wrote the placeholder page", file=sys.stderr)


def compare_live():
    try:
        release = release_manifest()
    except Exception as error:  # noqa: BLE001
        print(f"play: release unavailable ({error}); nothing to compare")
        return "false"
    try:
        live = live_manifest()
        changed = live["sha256"] != release["sha256"] or live["host"] != release["host"]
    except Exception as error:  # noqa: BLE001
        print(f"play: live build unavailable ({error})")
        changed = True
    return "true" if changed else "false"


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--local", type=lambda p: pb.Path(p).expanduser().resolve())
    parser.add_argument("--demo-root", type=lambda p: pb.Path(p).expanduser().resolve())
    parser.add_argument("--compare-live", action="store_true")
    parser.add_argument("--required", action="store_true", help="fail instead of mirroring or writing a placeholder")
    args = parser.parse_args()
    if args.compare_live:
        changed = compare_live()
        print(f"changed={changed}")
        if os.environ.get("GITHUB_OUTPUT"):
            with open(os.environ["GITHUB_OUTPUT"], "a") as output:
                output.write(f"changed={changed}\n")
        return
    required = args.required or os.environ.get("PLAY_REQUIRED") == "1"
    if not args.local and (pb.STATIC / pb.LOCAL).is_file() and not os.environ.get("CI") and os.environ.get("PLAY_REFRESH") != "1":
        print(f"play: keeping the local preview from {(pb.STATIC / pb.LOCAL).read_text().strip()}; set PLAY_REFRESH=1 to fetch the release")
        return
    out = pb.STATIC.with_name("play.tmp")
    if out.exists():
        shutil.rmtree(out)
    try:
        manifest = local_build(out, args.local) if args.local else release_build(out)
    except Exception as error:  # noqa: BLE001 - the fallbacks below decide
        if required:
            raise
        print(f"play: engine build unavailable ({error})", file=sys.stderr)
        shutil.rmtree(out, ignore_errors=True)
        try:
            manifest = mirror_live(out)
        except Exception as mirror_error:  # noqa: BLE001
            print(f"play: live build unavailable ({mirror_error})", file=sys.stderr)
            shutil.rmtree(out, ignore_errors=True)
            placeholder(out)
            manifest = None
    if manifest and not args.local:
        retain_previous(out, manifest)
    if manifest:
        try:
            demo_assets(out, args.demo_root)
        except Exception as error:  # noqa: BLE001
            if required:
                raise
            print(f"play: demo assets unavailable ({error}); the launcher offers local import only", file=sys.stderr)
    if pb.STATIC.exists():
        shutil.rmtree(pb.STATIC)
    out.rename(pb.STATIC)
    print(f"play: {pb.STATIC.relative_to(pb.ROOT)} ready")


if __name__ == "__main__":
    main()
