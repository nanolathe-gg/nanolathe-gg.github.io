"""Package an official add-on and write its catalogue entry.

Usage: python3 scripts/package-addon.py addons/<id>-<version>.json --install /path/to/TotalAnnihilation
       python3 scripts/package-addon.py addons/<id>-<version>.json --package <converter output>.zip

Copies the recipe's archives byte for byte, from an install or, for a
faction or model recipe, from the engine converter's ZIP together with the
recipe's documents, into .cache/addons/<id>-<version>.zip with the recipe's
identity-only nanolathe-mod.json, then replaces the entry in
static/addons/manifest.json, under "factions" or "fixes" for those recipe
kinds and "addons" otherwise. Upload the ZIP to the "addons" release before
publishing the manifest (README, "Official add-on catalogue").
"""
import json
import argparse
import hashlib
from pathlib import Path
import sys
import zipfile

import addoncatalog as ac
import modcatalog as mc

def build(recipe_path, *, install=None, package=None):
    recipe = mc.load_json(recipe_path)
    if problems := ac.recipe_problems(recipe):
        sys.exit("\n".join(f"{recipe_path}: {p}" for p in problems))
    meta = recipe["metadata"]
    if (install is None) == (package is None):
        sys.exit(f"{recipe_path}: choose exactly one of --install and --package")
    if (recipe.get("kind") in ("faction", "model")) != (package is not None):
        sys.exit(f"{recipe_path}: faction and model recipes use --package; other recipes use --install")
    if package is not None:
        with zipfile.ZipFile(package) as source:
            found = {info.filename.lower(): info for info in source.infolist()}
            read = lambda name: source.read(found[name.lower()]) if name.lower() in found else None
            if json.loads(read(mc.METADATA_NAME) or b"null") != meta:
                sys.exit(f"{package}: {mc.METADATA_NAME} differs from the recipe's metadata")
            sources = {name: read(name) for name in [*recipe["archives"], *ac.documents(recipe)]}
    else:
        on_disk = {p.name.lower(): p for p in install.iterdir() if p.is_file()}
        sources = {name: on_disk[name.lower()].read_bytes() if name.lower() in on_disk else None
                   for name in [*recipe["archives"], *ac.documents(recipe)]}
    members, contents = {mc.METADATA_NAME: mc.metadata_bytes(meta)}, []
    for name, data in sources.items():
        if data is None:
            sys.exit(f"{package or install}: has no {name}")
        members[name] = data
        if name in recipe["archives"]:
            contents.append({"name": name, "size": len(data), "sha256": hashlib.sha256(data).hexdigest()})
    out = ac.build_path(meta)
    out.parent.mkdir(parents=True, exist_ok=True)
    # One timestamp and mode, sorted members, stored: a rebuild is byte-identical.
    with zipfile.ZipFile(out, "w", compression=zipfile.ZIP_STORED) as archive:
        for name in sorted(members):
            info = zipfile.ZipInfo(name, mc.ZIP_TIME)
            info.external_attr = mc.ZIP_MODE << 16
            archive.writestr(info, members[name])
    return recipe, out, sorted(contents, key=lambda c: c["name"].lower())


def write_entry(recipe, out, contents):
    meta = recipe["metadata"]
    entry = {**mc.catalogue_metadata(meta),
             "archive": {"url": ac.archive_url(meta), "size": out.stat().st_size, "sha256": mc.sha256(out)},
             "contents": contents}
    manifest_path = ac.STATIC / ac.MANIFEST
    manifest = mc.load_json(manifest_path) if manifest_path.is_file() else {"schema": 1, "addons": []}
    key = ac.list_key(recipe)
    manifest[key] = [e for e in manifest.get(key, []) if (e["id"], e["version"]) != (meta["id"], meta["version"])] + [entry]
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(mc.dump_json(manifest))
    return entry


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("recipe", type=Path)
    source_group = parser.add_mutually_exclusive_group(required=True)
    source_group.add_argument("--install", type=Path)
    source_group.add_argument("--package", type=Path, help="a faction or model recipe's converter ZIP")
    args = parser.parse_args()
    recipe, out, contents = build(args.recipe, install=args.install, package=args.package)
    entry = write_entry(recipe, out, contents)
    print(f"{out}: {entry['archive']['size']} bytes, sha256 {entry['archive']['sha256']}")


if __name__ == "__main__":
    main()
