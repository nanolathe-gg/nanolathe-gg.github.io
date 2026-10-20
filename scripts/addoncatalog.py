"""Shared rules for the official add-on catalogue.

An add-on is a set of Total Annihilation archives — *.UFO content archives,
or one patch-tier revision archive for a fix — that the engine mounts with
the base game, apart from the mod slot
(docs/DESIGN_MODS_MUTATORS.md §5.7 in the engine repository). A recipe in
addons/ names its identity and archives; scripts/package-addon.py copies
those archives byte for byte from an install into one ZIP and writes its
catalogue entry, including every archive's size and SHA-256;
scripts/check-addons.py verifies the catalogue on every build. The ZIPs are
assets of this repository's "addons" release, and the engine reads the
catalogue at https://nanolathe.gg/addons/manifest.json.

A recipe of kind "faction" is a faction add-on or unit pack converted by the
engine's cmd/factionpack (DESIGN_MODS_MUTATORS §5.8): package-addon.py takes
its archive and named root documents from that converter's ZIP, and the
entry goes under the catalogue's "factions" list, which builds without
faction support ignore.

A recipe of kind "fix" is a community repair whose patch-tier revision
archive replaces the base install's patch archive (DESIGN_MODS_MUTATORS
§5.7): the entry goes under the "fixes" list, which builds without fix
support ignore.

A recipe of kind "model" is a model replacement converted by the engine's
cmd/modelpack. Like a faction recipe, it takes its archive and root documents
from the converter's ZIP. Its entry goes in the ordinary "addons" list.
"""
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import stat
import zipfile

import modcatalog as mc

ROOT = mc.ROOT
RECIPES = ROOT / "addons"
STATIC = ROOT / "static" / "addons"
PUBLIC = ROOT / "public" / "addons"
BUILD = ROOT / ".cache" / "addons"
MANIFEST = "manifest.json"
RELEASE_TAG = "addons"
RELEASE_BASE = f"https://github.com/{mc.REPOSITORY}/releases/download/{RELEASE_TAG}/"
# The engine's limits: at most 32 archives, each a flat content *.UFO or
# patch-tier revision name.
MAX_ARCHIVES = 32
METADATA_FIELDS = {"schema", *mc.CATALOGUE_FIELDS}
RECIPE_FIELDS = {"metadata", "archives", "kind", "documents"}
# The catalogue list each recipe kind's entry belongs to.
LISTS = {"": "addons", "faction": "factions", "fix": "fixes", "model": "addons"}
# Root documents the engine's add-on library accepts beside the archives.
DOCUMENT_EXTENSIONS = (".txt", ".md", ".rtf", ".html")


def list_key(recipe):
    return LISTS.get(recipe.get("kind", ""), "")


def documents(recipe):
    return list(recipe.get("documents", []))


def archive_url(meta):
    return RELEASE_BASE + mc.archive_name(meta)


def build_path(meta):
    return BUILD / mc.archive_name(meta)


def revision_name(name):
    """A patch-tier revision archive name: rev* with a patch extension."""
    if not isinstance(name, str):
        return False
    suffix = PurePosixPath(name).suffix
    if suffix.lower() not in (".gp3", ".gp4", ".gpf", ".swx"):
        return False
    stem = name[: len(name) - len(suffix)]
    return len(stem) > 3 and stem[:3].lower() == "rev"


def archive_name_problem(name):
    if not isinstance(name, str) or not name or len(name.encode()) > 255 or PurePosixPath(name).name != name \
            or re.search(r"[/\\:\x00\r\n]", name):
        return f"{name!r} is not a flat archive file name"
    if name.lower().endswith(".ufo") and len(name) > 4:
        return None
    if revision_name(name):
        return None
    return f"{name!r} is not a flat *.UFO or rev*.GP3 file name"


def recipe_problems(recipe):
    meta = recipe.get("metadata")
    if not isinstance(meta, dict):
        return ["metadata is not an object"]
    problems = mc.identity_problems(meta)
    if meta.get("schema") != 1:
        problems.append("metadata schema is not 1: an add-on carries identity only")
    problems += [f"unknown metadata field {key!r}" for key in sorted(set(meta) - METADATA_FIELDS)]
    problems += [f"unknown recipe field {key!r}" for key in sorted(set(recipe) - RECIPE_FIELDS)]
    if not list_key(recipe):
        problems.append(f"kind {recipe.get('kind')!r} is not one of {sorted(k for k in LISTS if k)}")
    names = recipe.get("archives")
    if not isinstance(names, list) or not 1 <= len(names) <= MAX_ARCHIVES:
        return problems + [f"archives is not a list of 1 to {MAX_ARCHIVES} names"]
    problems += [p for p in map(archive_name_problem, names) if p]
    if len({str(n).lower() for n in names}) != len(names):
        problems.append("archives repeats a name without regard to case")
    if recipe.get("kind") == "fix" and not any(revision_name(n) for n in names):
        problems.append("a fix recipe's archives must include a patch-tier revision archive")
    if recipe.get("kind") != "fix" and any(revision_name(n) for n in names):
        problems.append("only a fix recipe names a patch-tier revision archive")
    docs = recipe.get("documents", [])
    if docs and recipe.get("kind") not in ("faction", "fix", "model"):
        problems.append("only a faction, fix or model recipe names documents")
    if not isinstance(docs, list):
        return problems + ["documents is not a list"]
    for name in docs:
        if not isinstance(name, str) or PurePosixPath(name).name != name or re.search(r"[/\\:\x00\r\n]", name) \
                or not name.lower().endswith(DOCUMENT_EXTENSIONS):
            problems.append(f"document {name!r} is not a flat {'/'.join(DOCUMENT_EXTENSIONS)} name")
    taken = [str(n).lower() for n in [*names, *docs, mc.METADATA_NAME]]
    if len(set(taken)) != len(taken):
        problems.append("documents repeat an archive, each other or the metadata")
    return problems


def entry_problems(entry, recipe):
    """A catalogue entry: the recipe's identity, its release asset and its contents."""
    if not isinstance(entry, dict):
        return ["entry is not an object"]
    meta = recipe["metadata"]
    problems = []
    for key in sorted(set(entry) - {*mc.CATALOGUE_FIELDS, "archive", "contents"}):
        problems.append(f"unknown catalogue field {key!r}")
    if mc.catalogue_metadata(entry) != mc.catalogue_metadata(meta):
        problems.append("identity or display text differs from its recipe")
    archive = entry.get("archive")
    if not isinstance(archive, dict) or archive.get("url") != archive_url(meta):
        problems.append(f"archive url is not {archive_url(meta)!r}")
    elif type(archive.get("size")) is not int or archive["size"] <= 0 or not mc.SHA256.fullmatch(str(archive.get("sha256"))):
        problems.append("archive size or sha256 is malformed")
    contents = entry.get("contents")
    if not isinstance(contents, list) or sorted(str(c.get("name")).lower() for c in contents if isinstance(c, dict)) \
            != sorted(n.lower() for n in recipe["archives"]):
        return problems + ["contents do not list exactly the recipe's archives"]
    for c in contents:
        if set(c) != {"name", "size", "sha256"} or type(c["size"]) is not int or c["size"] <= 0 \
                or not mc.SHA256.fullmatch(str(c["sha256"])):
            problems.append(f"contents entry {c.get('name')!r} is malformed")
    return problems


def packaged_archive_problems(path, recipe, entry):
    """The ZIP: the entry's size and hash, identity-only metadata, and exactly the listed archives."""
    problems = []
    size = Path(path).stat().st_size
    if size != entry["archive"]["size"]:
        return [f"archive is {size} bytes, the entry says {entry['archive']['size']}"]
    if mc.sha256(path) != entry["archive"]["sha256"]:
        return ["archive SHA-256 differs from the entry"]
    expected = {c["name"].lower(): c for c in entry["contents"]}
    with zipfile.ZipFile(path) as archive:
        names = set()
        for info in archive.infolist():
            if stat.S_ISLNK(info.external_attr >> 16):
                problems.append(f"{info.filename}: is a symbolic link")
            names.add(info.filename)
            if info.filename == mc.METADATA_NAME or info.filename in documents(recipe):
                continue
            want = expected.get(info.filename.lower())
            if want is None or want["name"] != info.filename:
                problems.append(f"{info.filename}: not in the entry's contents")
                continue
            data = archive.read(info)
            if len(data) != want["size"] or hashlib.sha256(data).hexdigest() != want["sha256"]:
                problems.append(f"{info.filename}: differs from the entry's contents")
        if {n.lower() for n in names} != {*expected, mc.METADATA_NAME, *(d.lower() for d in documents(recipe))}:
            problems.append("archive members are not exactly the metadata, the listed archives and the recipe's documents")
        if json.loads(archive.read(mc.METADATA_NAME)) != recipe["metadata"]:
            problems.append(f"{mc.METADATA_NAME} differs from the recipe")
    return problems
