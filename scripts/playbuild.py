"""Shared rules for the published browser build under /play/.

The engine repository builds an asset-free browser distribution of every main
commit and publishes it as an immutable "browser-<run number>" release
(nanolathe/tools/browser-build and tools/browser-publish,
docs/DESIGN_BROWSER_HOST.md §6). Its root build.json names the content-hashed
Wasm, the matching Go runtime, the hashed host directory and that directory's
files. data/play.json pins where the build and the demo assets come from and
the demo files' digests.
"""
import gzip
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PINS = json.loads((ROOT / "data/play.json").read_text())
STATIC = ROOT / "static/play"
PUBLIC = ROOT / "public/play"
CACHE = ROOT / ".cache/play"
UNAVAILABLE = "UNAVAILABLE"
LOCAL = "LOCAL"
WASM = re.compile(r"nanolathe\.[a-f0-9]{16}\.wasm")
RUNTIME = re.compile(r"wasm_exec\.[a-f0-9]{16}\.js")
HOST = re.compile(r"host\.[a-f0-9]{16}")
HOST_FILE = re.compile(r"[a-z]+\.(?:js|html|css|json)")
SHA256 = re.compile(r"[0-9a-f]{64}")
DEMO_NAME = re.compile(r"[A-Za-z0-9._-]{1,64}")
LIMIT = 256 << 20


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def check_manifest(manifest):
    """Reject anything but a complete root manifest of the engine's bundle."""
    if not isinstance(manifest, dict) or manifest.get("schema") != 1:
        raise ValueError("browser build manifest is not schema 1")
    wasm, runtime, host = manifest.get("wasm", ""), manifest.get("runtime", ""), manifest.get("host", "")
    files, digest, size = manifest.get("files"), manifest.get("sha256", ""), manifest.get("size")
    if not (isinstance(wasm, str) and WASM.fullmatch(wasm) and isinstance(runtime, str) and RUNTIME.fullmatch(runtime)
            and isinstance(host, str) and HOST.fullmatch(host) and isinstance(digest, str) and SHA256.fullmatch(digest)
            and isinstance(size, int) and 0 < size <= LIMIT and isinstance(files, list) and files
            and all(isinstance(name, str) and HOST_FILE.fullmatch(name) for name in files)
            and "build.json" in files and "game.html" in files and "launcher.js" in files):
        raise ValueError("browser build manifest has unexpected fields")
    if manifest.get("wasm_gz") not in (None, wasm + ".gz"):
        raise ValueError("browser build manifest names a foreign gzip variant")
    if wasm[len("nanolathe."):len("nanolathe.") + 16] != digest[:16]:
        raise ValueError("browser build manifest's Wasm name disagrees with its digest")
    return manifest


def members(manifest):
    """Every published path of one build, relative to /play/."""
    names = {"index.html", "build.json", manifest["wasm"], manifest["runtime"]}
    if manifest.get("wasm_gz"):
        names.add(manifest["wasm_gz"])
    names |= {f"{manifest['host']}/{name}" for name in manifest["files"]}
    return names


def verify_build(directory, manifest):
    """Check a build's files on disk against its manifest; returns problems."""
    directory = Path(directory)
    problems = [f"missing {name}" for name in sorted(members(manifest)) if not (directory / name).is_file()]
    if problems:
        return problems
    data = (directory / manifest["wasm"]).read_bytes()
    if len(data) != manifest["size"] or sha256(data) != manifest["sha256"]:
        problems.append(f"{manifest['wasm']}: size or digest differs from build.json")
    if manifest.get("wasm_gz"):
        try:
            if gzip.decompress((directory / manifest["wasm_gz"]).read_bytes()) != data:
                problems.append(f"{manifest['wasm_gz']}: does not decompress to {manifest['wasm']}")
        except (OSError, EOFError) as error:
            problems.append(f"{manifest['wasm_gz']}: {error}")
    pinned = json.loads((directory / manifest["host"] / "build.json").read_text())
    expected = {key: value for key, value in manifest.items() if key not in ("host", "files")}
    if pinned != expected:
        problems.append(f"{manifest['host']}/build.json: differs from the root manifest")
    index = (directory / "index.html").read_text()
    for name in ("launcher.js", "style.css"):
        if f'{manifest["host"]}/{name}' not in index:
            problems.append(f"index.html: does not reference {manifest['host']}/{name}")
    return problems


def demo_rows():
    """The pinned demo files as the engine's manifest rows (browser_assets.py)."""
    rows = []
    for pin in PINS["demo"]["files"]:
        name, size, digest = pin["path"], pin["size"], pin["sha256"]
        if not (DEMO_NAME.fullmatch(name) and isinstance(size, int) and 0 < size <= 64 << 20 and SHA256.fullmatch(digest)):
            raise ValueError(f"data/play.json: invalid demo pin {pin}")
        rows.append({"path": name, "url": f"files/{digest}/{name}", "size": size, "sha256": digest})
    return rows


def demo_manifest():
    return {"schema": 1, "kind": "ta-demo", "files": demo_rows()}


def verify_demo(directory):
    """Check the published demo files against the pins; returns problems."""
    directory = Path(directory) / "demo"
    manifest_path = directory / "manifest.json"
    if not manifest_path.is_file():
        return ["demo/manifest.json: missing"]
    if json.loads(manifest_path.read_text()) != demo_manifest():
        return ["demo/manifest.json: differs from the pins in data/play.json"]
    problems = []
    for row in demo_rows():
        path = directory / row["url"]
        if not path.is_file():
            problems.append(f"demo/{row['url']}: missing")
            continue
        data = path.read_bytes()
        if len(data) != row["size"] or sha256(data) != row["sha256"]:
            problems.append(f"demo/{row['url']}: size or digest differs from data/play.json")
    return problems
