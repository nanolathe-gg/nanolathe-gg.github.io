"""Build a hosted mod archive and its manifest entry from a recipe.

    python3 scripts/package-mod.py mods/prota-4.8.json ~/Downloads/ProTA4.8.zip [--upload]

Each upstream archive must match its recipe size and SHA-256. Multipart
recipes list sources in order; pass one archive path per source. Each source
may strip a wrapping directory with stripPrefix before selecting its members.
Duplicate destination names are refused, including across sources. The recipe's
include patterns select members; executables, libraries and anything else the
engine refuses are never copied. The recipe's metadata is embedded as
nanolathe-mod.json. The archive is written to .cache/mods/, and
static/mods/manifest.json gains or replaces the entry for that id and version,
pointing at the asset of the same name on this repository's "mods" release.

--upload publishes the archive with the GitHub CLI, creating the release if
it does not exist. An asset is never replaced: a published name that already
holds different bytes is refused, because clients verify and resume against
the published hash. A mistake is corrected with a new version.
"""
import json
from pathlib import Path
import stat
import subprocess
import sys
import zipfile

import modcatalog as mc


def fail(message):
    raise SystemExit(f"package-mod: {message}")


def gh(*args):
    return subprocess.run(["gh", *args, "--repo", mc.REPOSITORY], check=True, capture_output=True, text=True).stdout


def build(recipe_path, *upstream_paths):
    recipe = mc.load_json(recipe_path)
    meta = recipe["metadata"]
    if problems := mc.metadata_problems(meta):
        fail("; ".join(problems))
    # Multipart recipes name each source independently. Refuse collisions:
    # filesystem overwrite order cannot establish archive mount precedence.
    sources = recipe.get("sources", [recipe])
    if not sources or len(sources) != len(upstream_paths):
        fail(f"expected {len(sources)} upstream archives in recipe order")
    members, folded = {}, {mc.METADATA_NAME.casefold()}
    for source_recipe, upstream_path in zip(sources, upstream_paths):
        upstream, include = source_recipe["upstream"], source_recipe["include"]
        upstream_path = Path(upstream_path).expanduser()
        if upstream_path.stat().st_size != upstream["size"] or mc.sha256(upstream_path) != upstream["sha256"]:
            fail(f"{upstream_path} is not the recipe's {upstream['file']} ({upstream['size']} bytes, SHA-256 {upstream['sha256']})")
        prefix = source_recipe.get("stripPrefix", "").rstrip("/")
        if prefix and (problem := mc.name_problem(prefix)) is not None:
            fail(f"stripPrefix {prefix!r} {problem}")
        selected = []
        with zipfile.ZipFile(upstream_path) as source:
            for info in source.infolist():
                name = info.filename
                if prefix:
                    if not name.startswith(prefix + "/"):
                        continue
                    name = name[len(prefix) + 1:]
                if info.is_dir() or not mc.selected(name, include):
                    continue
                if (problem := mc.name_problem(name)) is not None:
                    fail(f"{name} {problem}")
                if stat.S_IFMT(info.external_attr >> 16) not in (0, stat.S_IFREG):
                    fail(f"{info.filename} is not a regular file")
                if name.casefold() in folded:
                    fail(f"{name} is selected twice")
                folded.add(name.casefold())
                selected.append(name)
                members[name] = source.read(info)
        for pattern in include:
            if not any(mc.selected(name, [pattern]) for name in selected):
                fail(f"include pattern {pattern!r} matches nothing in {upstream['file']}")
    members[mc.METADATA_NAME] = mc.metadata_bytes(meta)

    target = mc.build_path(meta)
    target.parent.mkdir(parents=True, exist_ok=True)
    partial = target.with_suffix(".zip.tmp")
    with zipfile.ZipFile(partial, "w", compression=zipfile.ZIP_STORED) as archive:
        for name in sorted(members):
            info = zipfile.ZipInfo(name, mc.ZIP_TIME)
            info.create_system = 3
            info.external_attr = mc.ZIP_MODE << 16
            info.compress_type = zipfile.ZIP_STORED
            archive.writestr(info, members[name])
    partial.replace(target)
    if problems := mc.archive_problems(target, meta):
        fail("; ".join(problems))
    print(f"{target.relative_to(mc.ROOT)}: {len(members)} members, {target.stat().st_size} bytes, SHA-256 {mc.sha256(target)}")
    return meta, target


def upload(target):
    try:
        release = json.loads(gh("release", "view", mc.RELEASE_TAG, "--json", "assets"))
    except subprocess.CalledProcessError:
        gh("release", "create", mc.RELEASE_TAG, "--title", "Mods",
           "--notes", "Mod archives for Nanolathe's Get more mods dialog, listed by https://nanolathe.gg/mods/manifest.json. Each asset is one mod version and is never replaced.",
           "--latest=false")
        release = {"assets": []}
    for asset in release["assets"]:
        if asset["name"] == target.name:
            if asset["size"] != target.stat().st_size or asset.get("digest", "sha256:" + mc.sha256(target)) != "sha256:" + mc.sha256(target):
                fail(f"release {mc.RELEASE_TAG} already holds a different {target.name}; publish a new version instead")
            print(f"{target.name} is already published")
            return
    gh("release", "upload", mc.RELEASE_TAG, str(target))
    print(f"uploaded {target.name} to release {mc.RELEASE_TAG}")


def write_entry(meta, target):
    manifest_path = mc.STATIC / mc.MANIFEST
    manifest = mc.load_json(manifest_path) if manifest_path.exists() else {"schema": mc.SCHEMA, "mods": []}
    entry = dict(meta)
    entry["archive"] = {"url": mc.archive_url(meta), "size": target.stat().st_size, "sha256": mc.sha256(target)}
    mods = manifest["mods"]
    for index, existing in enumerate(mods):
        if existing["id"] == meta["id"] and existing["version"] == meta["version"]:
            mods[index] = entry
            break
    else:
        mods.append(entry)
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(mc.dump_json(manifest))


if __name__ == "__main__":
    args = [arg for arg in sys.argv[1:] if arg != "--upload"]
    if len(args) < 2:
        raise SystemExit(__doc__)
    meta, target = build(*args)
    if "--upload" in sys.argv[1:]:
        upload(target)
    write_entry(meta, target)
