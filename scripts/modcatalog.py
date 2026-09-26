"""Shared rules for the hosted mod catalogue.

A recipe in mods/ names an upstream archive, the members to keep and the
metadata to embed. scripts/package-mod.py builds the archive, uploads it to
this repository's "mods" GitHub release and writes its manifest entry;
scripts/check-mods.py verifies the manifest on every build, and the release
assets themselves with --remote. The engine reads the manifest at
https://nanolathe.gg/mods/manifest.json and refuses an archive whose size or
SHA-256 differs from its entry (docs/DESIGN_MODS_MUTATORS.md §5 in the engine
repository).
"""
import fnmatch
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import stat
import zipfile

ROOT = Path(__file__).resolve().parents[1]
RECIPES = ROOT / "mods"
STATIC = ROOT / "static" / "mods"
PUBLIC = ROOT / "public" / "mods"
BUILD = ROOT / ".cache" / "mods"
MANIFEST = "manifest.json"
# The archives are assets of one release on this repository, so the site's
# history does not carry them. The engine accepts release assets of
# nanolathe-gg repositories and follows GitHub's redirect to its asset host.
REPOSITORY = "nanolathe-gg/nanolathe-gg.github.io"
RELEASE_TAG = "mods"
RELEASE_BASE = f"https://github.com/{REPOSITORY}/releases/download/{RELEASE_TAG}/"
SCHEMA = 1
METADATA_NAME = "nanolathe-mod.json"
# Every member carries one timestamp and one mode, and members are stored in
# sorted order without compression, so a rebuild from the same upstream
# archive is byte-identical whatever zlib the machine has.
ZIP_TIME = (2000, 1, 1, 0, 0, 0)
ZIP_MODE = 0o100644
# The engine skips these on extraction and never runs them; hosted archives
# carry none.
EXECUTABLES = {".exe", ".dll", ".com", ".bat", ".cmd", ".scr", ".msi", ".ps1", ".sh", ".dylib", ".so"}
ID = re.compile(r"[a-z0-9-]{1,64}")
VERSION = re.compile(r"[A-Za-z0-9][A-Za-z0-9._+-]{0,63}")
SHA256 = re.compile(r"[0-9a-f]{64}")


def sha256(path):
    digest = hashlib.sha256()
    with open(path, "rb") as source:
        for block in iter(lambda: source.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def load_json(path):
    return json.loads(Path(path).read_text())


def dump_json(value):
    return json.dumps(value, indent=2, ensure_ascii=False) + "\n"


def archive_name(meta):
    return f"{meta['id']}-{meta['version']}.zip"


def archive_url(meta):
    """The archive's release asset URL."""
    return RELEASE_BASE + archive_name(meta)


def build_path(meta):
    """Where package-mod.py writes the archive before uploading it."""
    return BUILD / archive_name(meta)


def metadata_bytes(meta):
    return dump_json(meta).encode()


def selected(name, patterns):
    return any(fnmatch.fnmatchcase(name, pattern) for pattern in patterns)


def content_name(name, include, strip_prefix=""):
    """Select within the content root, preserving its relative member names."""
    if strip_prefix:
        prefix = strip_prefix.rstrip("/") + "/"
        if not name.startswith(prefix):
            return None
        name = name[len(prefix):]
    return name if selected(name, include) else None


def name_problem(name):
    """Why a member name is unsafe to extract, or None."""
    path = PurePosixPath(name)
    if not name or "\\" in name or name.startswith("/") or re.match(r"[A-Za-z]:", name):
        return "not a relative slash path"
    if any(part in ("", ".", "..") for part in name.rstrip("/").split("/")):
        return "has an empty, '.' or '..' segment"
    if path.suffix.lower() in EXECUTABLES:
        return "is an executable or library"
    return None


def metadata_problems(meta):
    problems = []
    if meta.get("schema") != SCHEMA:
        problems.append(f"metadata schema is not {SCHEMA}")
    if not ID.fullmatch(str(meta.get("id", ""))):
        problems.append("id is not lower-case letters, digits and dashes")
    if not VERSION.fullmatch(str(meta.get("version", ""))):
        problems.append("version is not a plain version string")
    if not str(meta.get("name", "")).strip():
        problems.append("name is empty")
    return problems


def archive_problems(path, meta):
    """Everything wrong with a hosted archive for this metadata."""
    problems = []
    seen = set()
    with zipfile.ZipFile(path) as archive:
        for info in archive.infolist():
            name = info.filename
            if (problem := name_problem(name)) is not None:
                problems.append(f"{name}: {problem}")
            if stat.S_ISLNK(info.external_attr >> 16):
                problems.append(f"{name}: is a symbolic link")
            folded = name.casefold()
            if folded in seen:
                problems.append(f"{name}: duplicates another member by case")
            seen.add(folded)
        try:
            embedded = json.loads(archive.read(METADATA_NAME))
        except KeyError:
            problems.append(f"{METADATA_NAME} is missing")
        else:
            if embedded != meta:
                problems.append(f"{METADATA_NAME} differs from the manifest entry")
    return problems
