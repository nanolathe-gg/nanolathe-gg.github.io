"""Verify the hosted mod catalogue against its recipes.

Every manifest entry must have a recipe in mods/ with the same identity and
display fields, and every recipe an entry; each entry names its asset on the "mods" release with
a well-formed size and SHA-256; static/mods holds only the manifest; and the
published copy equals the source. Locally built archives are also checked when
present; --local requires every current archive to be available in .cache/mods/.

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
if (manifest.get("schema") != mc.SCHEMA or not isinstance(manifest.get("mods"), list)
        or set(manifest) != {"schema", "mods"}):
    sys.exit(f"{manifest_path}: not a schema {mc.SCHEMA} catalogue with a mods list")

recipes = {}
for path in sorted(mc.RECIPES.glob("*.json")):
    meta = mc.load_json(path)["metadata"]
    errors += [f"{path.name}: {problem}" for problem in mc.metadata_problems(meta)]
    key = f"{meta['id']}@{meta['version']}"
    if path.stem != f"{meta['id']}-{meta['version']}":
        errors.append(f"{path.name}: name it {meta['id']}-{meta['version']}.json")
    recipes[key] = meta

entries = []
seen, seen_ids = set(), set()
for entry in manifest["mods"]:
    key = f"{entry.get('id')}@{entry.get('version')}"
    errors += [f"{key}: {problem}" for problem in mc.entry_problems(entry)]
    if entry.get("id") in seen_ids:
        errors.append(f"{key}: mod id listed twice; list only the current package")
    seen.add(key)
    seen_ids.add(entry.get("id"))
    meta = recipes.get(key)
    if meta is None or mc.catalogue_metadata(meta) != mc.catalogue_metadata(entry):
        errors.append(f"{key}: differs from its recipe in mods/, or has none")
    entries.append((key, meta, entry))
for key in sorted(set(recipes) - seen):
    errors.append(f"{key}: has a recipe but no manifest entry")

for path in sorted(mc.STATIC.rglob("*")):
    if path.is_file() and path != manifest_path:
        errors.append(f"{path.relative_to(mc.ROOT)}: archives belong on the {mc.RELEASE_TAG} release, not in static/")
published = mc.PUBLIC / mc.MANIFEST
if not published.is_file() or published.read_bytes() != manifest_path.read_bytes():
    errors.append(f"{published.relative_to(mc.ROOT)}: published copy differs from the source")

if not errors:
    for key, meta, entry in entries:
        local = mc.build_path(meta)
        if local.is_file():
            errors += [f"{key}: {problem}" for problem in mc.packaged_archive_problems(local, meta, entry)]
        elif "--local" in sys.argv[1:]:
            errors.append(f"{key}: local archive {local} is missing")

if "--remote" in sys.argv[1:] and not errors:
    for key, meta, entry in entries:
        archive = entry["archive"]
        with tempfile.NamedTemporaryFile(suffix=".zip") as download:
            request = urllib.request.Request(archive["url"], headers={"User-Agent": "nanolathe-website-check"})
            with urllib.request.urlopen(request, timeout=60) as response:
                for block in iter(lambda: response.read(1 << 20), b""):
                    download.write(block)
            download.flush()
            errors += [f"{key}: {problem}" for problem in mc.packaged_archive_problems(download.name, meta, entry)]

if errors:
    print("\n".join(errors), file=sys.stderr)
    sys.exit(1)
checked = "manifest, recipes and available local archives"
if "--remote" in sys.argv[1:]:
    checked += ", plus release assets"
print(f"Mod catalogue: {len(seen)} entries; {checked} and the published copy agree.")
