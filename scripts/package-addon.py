"""Package an official add-on from an install and write its catalogue entry.

Usage: python3 scripts/package-addon.py addons/<id>-<version>.json --install /path/to/TotalAnnihilation

Copies the recipe's archives byte for byte into .cache/addons/<id>-<version>.zip
with the recipe's identity-only nanolathe-mod.json, then replaces the entry in
static/addons/manifest.json. Upload the ZIP to the "addons" release before
publishing the manifest (README, "Official add-on catalogue").
"""
import argparse
import hashlib
from pathlib import Path
import sys
import zipfile

import addoncatalog as ac
import modcatalog as mc

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("recipe", type=Path)
parser.add_argument("--install", required=True, type=Path)
args = parser.parse_args()
recipe = mc.load_json(args.recipe)
if problems := ac.recipe_problems(recipe):
    sys.exit("\n".join(f"{args.recipe}: {p}" for p in problems))
meta = recipe["metadata"]
on_disk = {p.name.lower(): p for p in args.install.iterdir() if p.is_file()}
members, contents = {mc.METADATA_NAME: mc.metadata_bytes(meta)}, []
for name in recipe["archives"]:
    source = on_disk.get(name.lower())
    if source is None:
        sys.exit(f"{args.install}: has no {name}")
    data = source.read_bytes()
    members[name] = data
    contents.append({"name": name, "size": len(data), "sha256": hashlib.sha256(data).hexdigest()})
out = ac.build_path(meta)
out.parent.mkdir(parents=True, exist_ok=True)
# One timestamp and mode, sorted members, stored: a rebuild is byte-identical.
with zipfile.ZipFile(out, "w", compression=zipfile.ZIP_STORED) as archive:
    for name in sorted(members):
        info = zipfile.ZipInfo(name, mc.ZIP_TIME)
        info.external_attr = mc.ZIP_MODE << 16
        archive.writestr(info, members[name])
entry = {**mc.catalogue_metadata(meta), "archive": {"url": ac.archive_url(meta), "size": out.stat().st_size, "sha256": mc.sha256(out)},
         "contents": sorted(contents, key=lambda c: c["name"].lower())}
manifest_path = ac.STATIC / ac.MANIFEST
manifest = mc.load_json(manifest_path) if manifest_path.is_file() else {"schema": 1, "addons": []}
manifest["addons"] = [e for e in manifest["addons"] if (e["id"], e["version"]) != (meta["id"], meta["version"])] + [entry]
manifest_path.parent.mkdir(parents=True, exist_ok=True)
manifest_path.write_text(mc.dump_json(manifest))
print(f"{out}: {entry['archive']['size']} bytes, sha256 {entry['archive']['sha256']}")
