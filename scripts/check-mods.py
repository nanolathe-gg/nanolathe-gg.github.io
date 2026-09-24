"""Verify the hosted mod catalogue against its recipes.

Every manifest entry must have a recipe in mods/ with the same metadata, and
every recipe an entry; each entry names its asset on the "mods" release with
a well-formed size and SHA-256; static/mods holds only the manifest; and the
published copy equals the source.

--remote also downloads every entry's release asset and checks its size,
SHA-256, embedded nanolathe-mod.json and contents, as the engine would.
"""
import sys
import tempfile
import urllib.request

import modcatalog as mc

errors = []
manifest_path = mc.STATIC / mc.MANIFEST
manifest = mc.load_json(manifest_path)
if manifest.get("schema") != mc.SCHEMA or not isinstance(manifest.get("mods"), list):
    sys.exit(f"{manifest_path}: not a schema {mc.SCHEMA} catalogue with a mods list")

recipes = {}
for path in sorted(mc.RECIPES.glob("*.json")):
    meta = mc.load_json(path)["metadata"]
    key = f"{meta['id']}@{meta['version']}"
    if path.stem != f"{meta['id']}-{meta['version']}":
        errors.append(f"{path.name}: name it {meta['id']}-{meta['version']}.json")
    recipes[key] = meta

entries = []
seen = set()
for entry in manifest["mods"]:
    meta = {key: value for key, value in entry.items() if key != "archive"}
    key = f"{meta.get('id')}@{meta.get('version')}"
    errors += [f"{key}: {problem}" for problem in mc.metadata_problems(meta)]
    if key in seen:
        errors.append(f"{key}: listed twice")
    seen.add(key)
    if recipes.get(key) != meta:
        errors.append(f"{key}: differs from its recipe in mods/, or has none")
    archive = entry.get("archive", {})
    if archive.get("url") != mc.archive_url(meta):
        errors.append(f"{key}: archive url is not {mc.archive_url(meta)!r}")
    if not isinstance(archive.get("size"), int) or archive["size"] <= 0:
        errors.append(f"{key}: archive size is not a positive integer")
    if not mc.SHA256.fullmatch(str(archive.get("sha256", ""))):
        errors.append(f"{key}: archive sha256 is not 64 lower-case hex digits")
    entries.append((key, meta, archive))
for key in sorted(set(recipes) - seen):
    errors.append(f"{key}: has a recipe but no manifest entry")

for path in sorted(mc.STATIC.rglob("*")):
    if path.is_file() and path != manifest_path:
        errors.append(f"{path.relative_to(mc.ROOT)}: archives belong on the {mc.RELEASE_TAG} release, not in static/")
published = mc.PUBLIC / mc.MANIFEST
if not published.is_file() or published.read_bytes() != manifest_path.read_bytes():
    errors.append(f"{published.relative_to(mc.ROOT)}: published copy differs from the source")

if "--remote" in sys.argv[1:] and not errors:
    for key, meta, archive in entries:
        with tempfile.NamedTemporaryFile(suffix=".zip") as download:
            request = urllib.request.Request(archive["url"], headers={"User-Agent": "nanolathe-website-check"})
            with urllib.request.urlopen(request, timeout=60) as response:
                for block in iter(lambda: response.read(1 << 20), b""):
                    download.write(block)
            download.flush()
            size = download.tell()
            if size != archive["size"]:
                errors.append(f"{key}: release asset is {size} bytes, the entry says {archive['size']}")
            elif mc.sha256(download.name) != archive["sha256"]:
                errors.append(f"{key}: release asset SHA-256 differs from the entry")
            else:
                errors += [f"{key}: {problem}" for problem in mc.archive_problems(download.name, meta)]

if errors:
    print("\n".join(errors), file=sys.stderr)
    sys.exit(1)
checked = "manifest, recipes, release assets" if "--remote" in sys.argv[1:] else "manifest and recipes"
print(f"Mod catalogue: {len(seen)} entries; {checked} and the published copy agree.")
