"""Verify the official add-on catalogue against its recipes.

Every entry must match a recipe in addons/ and every recipe have an entry;
static/addons holds only the manifest, and the published copy equals the
source. A locally built archive in .cache/addons is checked when present;
--remote downloads every release asset and checks it as the engine would.
"""
import sys
import tempfile
import urllib.request

import addoncatalog as ac
import modcatalog as mc

errors = []
manifest_path = ac.STATIC / ac.MANIFEST
manifest = mc.load_json(manifest_path)
lists = [key for key in ("addons", "factions") if key in manifest]
if manifest.get("schema") != 1 or not isinstance(manifest.get("addons"), list) or set(manifest) != {"schema", *lists} \
        or not all(isinstance(manifest[key], list) for key in lists):
    sys.exit(f"{manifest_path}: not a schema 1 catalogue with an addons list and an optional factions list")
recipes = {}
for path in sorted(ac.RECIPES.glob("*.json")):
    recipe = mc.load_json(path)
    errors += [f"{path.name}: {p}" for p in ac.recipe_problems(recipe)]
    meta = recipe.get("metadata", {})
    if path.stem != f"{meta.get('id')}-{meta.get('version')}":
        errors.append(f"{path.name}: name it {meta.get('id')}-{meta.get('version')}.json")
    recipes[f"{meta.get('id')}@{meta.get('version')}"] = recipe
entries, seen = [], set()
for listed, entry in [(name, e) for name in lists for e in manifest[name]]:
    key = f"{entry.get('id')}@{entry.get('version')}"
    if key in seen:
        errors.append(f"{key}: listed twice")
    seen.add(key)
    recipe = recipes.get(key)
    if recipe is None:
        errors.append(f"{key}: has no recipe in addons/")
        continue
    if ac.list_key(recipe) != listed:
        errors.append(f"{key}: belongs under {ac.list_key(recipe)!r}, not {listed!r}")
    errors += [f"{key}: {p}" for p in ac.entry_problems(entry, recipe)]
    entries.append((key, recipe, entry))
errors += [f"{key}: has a recipe but no manifest entry" for key in sorted(set(recipes) - seen)]
for path in sorted(ac.STATIC.rglob("*")):
    if path.is_file() and path != manifest_path:
        errors.append(f"{path.relative_to(ac.ROOT)}: archives belong on the {ac.RELEASE_TAG} release, not in static/")
published = ac.PUBLIC / ac.MANIFEST
if not published.is_file() or published.read_bytes() != manifest_path.read_bytes():
    errors.append(f"{published.relative_to(ac.ROOT)}: published copy differs from the source")
if not errors:
    for key, recipe, entry in entries:
        local = ac.build_path(recipe["metadata"])
        if local.is_file():
            errors += [f"{key}: {p}" for p in ac.packaged_archive_problems(local, recipe, entry)]
if "--remote" in sys.argv[1:] and not errors:
    for key, recipe, entry in entries:
        with tempfile.NamedTemporaryFile(suffix=".zip") as download:
            request = urllib.request.Request(entry["archive"]["url"], headers={"User-Agent": "nanolathe-website-check"})
            with urllib.request.urlopen(request, timeout=60) as response:
                for block in iter(lambda: response.read(1 << 20), b""):
                    download.write(block)
            download.flush()
            errors += [f"{key}: {p}" for p in ac.packaged_archive_problems(download.name, recipe, entry)]
if errors:
    print("\n".join(errors), file=sys.stderr)
    sys.exit(1)
print(f"{len(entries)} add-ons: manifest, recipes and available archives verified" + (" with release assets" if "--remote" in sys.argv[1:] else ""))
