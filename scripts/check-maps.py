"""Check the community map catalogue and, optionally, its release payloads.

Use --archives DIR for local packages or --remote to verify published ZIPs.
The engine performs the deeper OTA/TNT and feature validation at installation.
"""
import argparse
import json
from pathlib import Path, PurePosixPath
import stat
import tempfile
import urllib.request
import zipfile

import modcatalog as mc

RELEASE = "https://github.com/nanolathe-gg/nanolathe-gg.github.io/releases/download/maps/"
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--archives", type=Path)
parser.add_argument("--remote", action="store_true")
parser.add_argument("--source-only", action="store_true")
args = parser.parse_args()
source = mc.ROOT / "static/maps/manifest.json"
manifest = mc.load_json(source)
errors = []
if (manifest.get("schema") != 1 or set(manifest) != {"schema", "maps", "dependencies"}
        or not isinstance(manifest["maps"], list) or not isinstance(manifest["dependencies"], list)):
    parser.error("expected schema 1 with maps and dependencies arrays")
dependencies = {e.get("id") for e in manifest["dependencies"]}
seen = set()
for kind in ("dependencies", "maps"):
    for entry in manifest[kind]:
        key = entry.get("id", "<missing>")
        errors.extend(f"{key}: {p}" for p in mc.identity_problems(entry))
        if key in seen:
            errors.append(f"{key}: duplicate package ID")
        seen.add(key)
        archive = entry.get("archive", {})
        expected_url = RELEASE + mc.archive_name(entry)
        if archive.get("url") != expected_url:
            errors.append(f"{key}: expected release URL {expected_url}")
        if type(archive.get("size")) is not int or archive["size"] <= 0:
            errors.append(f"{key}: invalid size")
        if not mc.SHA256.fullmatch(archive.get("sha256", "")):
            errors.append(f"{key}: invalid SHA-256")
        if kind == "maps":
            path = entry.get("map", "")
            if (mc.name_problem(path) or len(PurePosixPath(path).parts) != 2
                    or not path.startswith("maps/") or not path.endswith(".ota")):
                errors.append(f"{key}: invalid map path")
            requires = entry.get("requires", [])
            if (not isinstance(requires, list) or any(not isinstance(r, str) for r in requires)
                    or len(set(requires)) != len(requires) or not set(requires) <= dependencies):
                errors.append(f"{key}: invalid dependencies")
        elif entry.get("map") or entry.get("requires"):
            errors.append(f"{key}: shared features cannot depend on other packages or select a map")

if not args.source_only:
    published = mc.ROOT / "public/maps/manifest.json"
    if not published.is_file() or published.read_bytes() != source.read_bytes():
        errors.append("published map manifest differs from source; run make build")


def check_archive(path, entry):
    key, spec = entry["id"], entry["archive"]
    if path.stat().st_size != spec["size"] or mc.sha256(path) != spec["sha256"]:
        errors.append(f"{key}: archive size or SHA-256 differs")
        return
    with zipfile.ZipFile(path) as z:
        names = set()
        for info in z.infolist():
            if mc.name_problem(info.filename) or stat.S_ISLNK(info.external_attr >> 16):
                errors.append(f"{key}: unsafe member {info.filename}")
            if info.filename.casefold() in names:
                errors.append(f"{key}: duplicate member {info.filename}")
            names.add(info.filename.casefold())
        meta = json.loads(z.read(mc.METADATA_NAME))
        if (meta.get("schema") != 1 or mc.catalogue_metadata(meta) != mc.catalogue_metadata(entry)
                or set(meta) - {"schema", *mc.CATALOGUE_FIELDS}):
            errors.append(f"{key}: package metadata differs or carries configuration")
        if z.testzip() is not None:
            errors.append(f"{key}: ZIP CRC failure")


if not errors:
    for entry in manifest["dependencies"] + manifest["maps"]:
        if args.archives:
            check_archive(args.archives / mc.archive_name(entry), entry)
        if args.remote:
            with tempfile.TemporaryDirectory() as tmp:
                path = Path(tmp) / mc.archive_name(entry)
                req = urllib.request.Request(entry["archive"]["url"], headers={"User-Agent": "nanolathe-map-check"})
                with urllib.request.urlopen(req, timeout=90) as response, path.open("wb") as out:
                    while block := response.read(1 << 20):
                        out.write(block)
                check_archive(path, entry)
if errors:
    raise SystemExit("\n".join(errors))
size = sum(e["archive"]["size"] for e in manifest["maps"] + manifest["dependencies"])
print(f"Map catalogue: {len(manifest['maps'])} maps, {len(dependencies)} shared packages, {size:,} bytes catalogued.")
