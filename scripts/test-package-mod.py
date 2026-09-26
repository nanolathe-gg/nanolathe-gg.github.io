"""Focused packaging checks with authored ZIP and transcoded-RAR fixtures.

Run: python3 scripts/test-package-mod.py
Real upstream archives are checked separately by package-mod.py's pinned recipe.
"""
from contextlib import nullcontext, redirect_stdout
import importlib.util
import io
from pathlib import Path
import stat
import tarfile
import tempfile
import unittest
from unittest.mock import patch
import zipfile

import modcatalog as mc

spec = importlib.util.spec_from_file_location("package_mod", Path(__file__).with_name("package-mod.py"))
package = importlib.util.module_from_spec(spec)
spec.loader.exec_module(package)


class PackagingTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        build = patch.object(mc, "BUILD", self.root / "build")
        build.start()
        self.addCleanup(build.stop)
        root = patch.object(mc, "ROOT", self.root)
        root.start()
        self.addCleanup(root.stop)
        self.meta = {"schema": 1, "id": "fixture", "name": "Fixture", "version": "1"}

    def recipe(self, members, format="zip", prefix="", include=None):
        source = self.root / ("upstream.zip" if format == "zip" else "transcoded.tar")
        if format == "zip":
            with zipfile.ZipFile(source, "w") as archive:
                for name, data, mode in members:
                    info = zipfile.ZipInfo(name)
                    info.create_system = 3
                    info.external_attr = mode << 16
                    archive.writestr(info, data)
        else:
            with tarfile.open(source, "w") as archive:
                for name, data, mode in members:
                    info = tarfile.TarInfo(name)
                    if stat.S_ISLNK(mode):
                        info.type, info.linkname = tarfile.SYMTYPE, "elsewhere"
                        data = b""
                    info.size = len(data)
                    archive.addfile(info, io.BytesIO(data))
        recipe = {
            "upstream": {"file": source.name, "size": source.stat().st_size, "sha256": mc.sha256(source)},
            "include": include or ["*"], "metadata": self.meta,
        }
        if format != "zip":
            recipe["upstream"]["format"] = format
        if prefix:
            recipe["stripPrefix"] = prefix
        path = self.root / "recipe.json"
        path.write_text(mc.dump_json(recipe))
        return path, source

    def build(self, members, format="zip", prefix="", include=None):
        args = self.recipe(members, format, prefix, include)

        def transcoded(path, patterns, strip_prefix):
            with path.open("rb") as stream:
                yield from package.tar_members(stream, patterns, strip_prefix)

        reader = patch.object(package, "rar_members", transcoded) if format == "rar" else nullcontext()
        with reader, redirect_stdout(io.StringIO()):
            return package.build(*args)[1]

    def test_content_root_selection_and_reproducibility(self):
        members = [(name, data, stat.S_IFREG | 0o644) for name, data in [
            ("Step 2/Icon/unit.pcx", b"icon"), ("Step 2/Mod.gp3", b"archive"),
            ("Step 2/launcher.exe", b"omitted"), ("Step 20/Mod.gp3", b"outside"),
        ]]
        for format in ("zip", "rar"):
            with self.subTest(format=format):
                args = dict(format=format, prefix="Step 2/", include=["*.gp3", "Icon/*"])
                target = self.build(members, **args)
                first = target.read_bytes()
                with zipfile.ZipFile(target) as archive:
                    self.assertEqual(archive.namelist(), ["Icon/unit.pcx", "Mod.gp3", mc.METADATA_NAME])
                    self.assertEqual(archive.read("Mod.gp3"), b"archive")
                    self.assertEqual(archive.read(mc.METADATA_NAME), mc.metadata_bytes(self.meta))
                    for info in archive.infolist():
                        self.assertEqual(info.date_time, mc.ZIP_TIME)
                        self.assertEqual(info.external_attr >> 16, mc.ZIP_MODE)
                        self.assertEqual(info.compress_type, zipfile.ZIP_STORED)
                self.assertEqual(mc.archive_problems(target, self.meta), [])
                self.assertEqual(self.build(members, **args).read_bytes(), first)

    def test_selected_unsafe_names_and_duplicates_are_rejected(self):
        regular = stat.S_IFREG | 0o644
        cases = [
            [("../escape.gp3", b"a", regular)],
            [("nested/../../escape.gp3", b"a", regular)],
            [("C:/escape.gp3", b"a", regular)],
            [("Icon\\escape.pcx", b"a", regular)],
            [("launcher.EXE", b"a", regular)],
            [("Mod.gp3", b"a", regular), ("mod.gp3", b"b", regular)],
            [(mc.METADATA_NAME, b"replacement", regular)],
            [("Mod.gp3", b"elsewhere", stat.S_IFLNK | 0o777)],
        ]
        for format in ("zip", "rar"):
            for members in cases:
                with self.subTest(format=format, names=[m[0] for m in members]):
                    prefixed = [("Step 2/" + name, data, mode) for name, data, mode in members]
                    with self.assertRaises(SystemExit):
                        self.build(prefixed, format=format, prefix="Step 2/")

    def test_empty_patterns_and_unsafe_prefix_are_rejected(self):
        members = [("Mod.gp3", b"archive", stat.S_IFREG | 0o644)]
        with self.assertRaisesRegex(SystemExit, "matches nothing"):
            self.build(members, include=["missing/*"])
        with self.assertRaisesRegex(SystemExit, "stripPrefix"):
            self.build(members, prefix="../")

    def test_upstream_checksum_is_required(self):
        args = self.recipe([("Mod.gp3", b"archive", stat.S_IFREG | 0o644)])
        recipe = mc.load_json(args[0])
        recipe["upstream"]["sha256"] = "0" * 64
        args[0].write_text(mc.dump_json(recipe))
        with self.assertRaisesRegex(SystemExit, "not the recipe's"):
            package.build(*args)
        self.assertFalse(mc.build_path(self.meta).exists())


if __name__ == "__main__":
    unittest.main()
