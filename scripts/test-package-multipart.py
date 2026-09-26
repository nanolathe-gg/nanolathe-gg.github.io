"""Check multipart packaging with small authored archives, without game data."""
from contextlib import redirect_stdout
import importlib.util
import io
from pathlib import Path
import stat
import tempfile
import unittest
from unittest.mock import patch
import zipfile

import modcatalog as mc

spec = importlib.util.spec_from_file_location("package_mod", Path(__file__).with_name("package-mod.py"))
package = importlib.util.module_from_spec(spec)
spec.loader.exec_module(package)


class MultipartTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        for attr, value in (("ROOT", self.root), ("BUILD", self.root / "build")):
            patcher = patch.object(mc, attr, value)
            patcher.start()
            self.addCleanup(patcher.stop)
        self.meta = {"schema": 1, "id": "fixture", "name": "Fixture", "version": "1"}

    def source(self, filename, entries, include, prefix=""):
        path = self.root / filename
        with zipfile.ZipFile(path, "w") as archive:
            for name, data in entries:
                archive.writestr(name, data)
        source = {"upstream": {"file": filename, "size": path.stat().st_size,
                               "sha256": mc.sha256(path)}, "include": include}
        if prefix:
            source["stripPrefix"] = prefix
        return source, path

    def build(self, sources, paths):
        recipe = self.root / "recipe.json"
        recipe.write_text(mc.dump_json({"sources": sources, "metadata": self.meta}))
        with redirect_stdout(io.StringIO()):
            return package.build(recipe, *paths)[1]

    def test_combines_only_selected_content_reproducibly(self):
        base, base_path = self.source("base.zip", [
            ("Root/Shared.ccx", b"base"), ("Root/Icon/unit.pcx", b"icon"),
            ("Root/launcher.exe", b"omitted"), ("Root2/Shared.ccx", b"outside"),
        ], ["Shared.ccx", "Icon/*"], "Root/")
        mod, mod_path = self.source("mod.zip", [("Mod.gp3", b"mod")], ["Mod.gp3"])
        target = self.build([base, mod], [base_path, mod_path])
        first = target.read_bytes()
        with zipfile.ZipFile(target) as archive:
            self.assertEqual(archive.namelist(), ["Icon/unit.pcx", "Mod.gp3", "Shared.ccx", mc.METADATA_NAME])
            self.assertEqual(archive.read("Shared.ccx"), b"base")
            self.assertEqual(archive.read("Mod.gp3"), b"mod")
        self.assertEqual(mc.archive_problems(target, self.meta), [])
        self.assertEqual(self.build([base, mod], [base_path, mod_path]).read_bytes(), first)

    def test_missing_inputs_and_corrupt_later_source_are_rejected(self):
        base, base_path = self.source("base.zip", [("Base.ccx", b"base")], ["Base.ccx"])
        mod, mod_path = self.source("mod.zip", [("Mod.gp3", b"mod")], ["Mod.gp3"])
        with self.assertRaisesRegex(SystemExit, "expected 2"):
            self.build([base, mod], [base_path])
        mod["upstream"]["sha256"] = "0" * 64
        with self.assertRaisesRegex(SystemExit, "not the recipe's"):
            self.build([base, mod], [base_path, mod_path])
        self.assertFalse(mc.build_path(self.meta).exists())

    def test_collisions_and_each_sources_patterns_are_checked(self):
        base, base_path = self.source("base.zip", [("Mod.gp3", b"base")], ["*.gp3"])
        mod, mod_path = self.source("mod.zip", [("mod.gp3", b"mod")], ["*.gp3"])
        with self.assertRaisesRegex(SystemExit, "selected twice"):
            self.build([base, mod], [base_path, mod_path])
        mod["include"] = ["Mod.gp3"]
        with self.assertRaisesRegex(SystemExit, "matches nothing"):
            self.build([base, mod], [base_path, mod_path])

    def test_selected_unsafe_members_and_prefixes_are_rejected(self):
        for name in ("../escape.gp3", "launcher.exe", mc.METADATA_NAME):
            source, path = self.source("bad.zip", [("Root/" + name, b"bad")], ["*"], "Root")
            with self.subTest(name=name), self.assertRaises(SystemExit):
                self.build([source], [path])
        source, path = self.source("bad.zip", [("Mod.gp3", b"bad")], ["*"], "../")
        with self.assertRaisesRegex(SystemExit, "stripPrefix"):
            self.build([source], [path])
        with zipfile.ZipFile(path, "w") as archive:
            info = zipfile.ZipInfo("link.gp3")
            info.create_system = 3
            info.external_attr = (stat.S_IFLNK | 0o777) << 16
            archive.writestr(info, "elsewhere")
        source.pop("stripPrefix")
        source["upstream"].update(size=path.stat().st_size, sha256=mc.sha256(path))
        with self.assertRaisesRegex(SystemExit, "not a regular file"):
            self.build([source], [path])


if __name__ == "__main__":
    unittest.main()
