"""Check add-on categories and packaging with small authored archives."""
import copy
import importlib.util
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import zipfile

import addoncatalog as ac
import modcatalog as mc

spec = importlib.util.spec_from_file_location("package_addon", Path(__file__).with_name("package-addon.py"))
package = importlib.util.module_from_spec(spec)
spec.loader.exec_module(package)


class AddonPackagingTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        for attr, value in (("BUILD", self.root / "build"), ("STATIC", self.root / "static")):
            patcher = patch.object(ac, attr, value)
            patcher.start()
            self.addCleanup(patcher.stop)
        self.meta = {"schema": 1, "id": "fixture", "name": "Fixture", "version": "1",
                     "summary": "An authored add-on fixture."}

    def recipe(self, kind="model"):
        recipe = {"metadata": self.meta, "archives": ["Fixture.ufo"]}
        if kind:
            recipe["kind"] = kind
            recipe["documents"] = ["README.txt", "SOURCES.txt"]
        if kind == "fix":
            recipe["archives"] = ["rev31.gp3"]
        return recipe

    def source(self, recipe, *, embedded=None, omit=()):
        path = self.root / "converter.zip"
        members = {name: f"Authored {name}".encode()
                   for name in [*recipe["archives"], *ac.documents(recipe)]}
        members[mc.METADATA_NAME] = mc.metadata_bytes(embedded or self.meta)
        with zipfile.ZipFile(path, "w") as archive:
            for name, data in members.items():
                if name not in omit:
                    archive.writestr(name, data)
        return path, members

    def build(self, recipe, **sources):
        path = self.root / "recipe.json"
        path.write_text(mc.dump_json(recipe))
        return package.build(path, **sources)

    def test_model_package_documents_identity_and_reproducibility(self):
        recipe = self.recipe()
        source, members = self.source(recipe)
        built, target, contents = self.build(recipe, package=source)
        first = target.read_bytes()
        with zipfile.ZipFile(target) as archive:
            self.assertEqual(archive.namelist(), sorted(members))
            for info in archive.infolist():
                self.assertEqual(archive.read(info), members[info.filename])
                self.assertEqual(info.date_time, mc.ZIP_TIME)
                self.assertEqual(info.external_attr >> 16, mc.ZIP_MODE)
                self.assertEqual(info.compress_type, zipfile.ZIP_STORED)
        self.assertEqual(self.build(recipe, package=source)[1].read_bytes(), first)
        entry = package.write_entry(built, target, contents)
        self.assertEqual(ac.entry_problems(entry, recipe), [])
        self.assertEqual(ac.packaged_archive_problems(target, recipe, entry), [])

    def test_model_catalogue_preserves_other_categories_and_replaces_edition(self):
        recipe = self.recipe()
        source, _ = self.source(recipe)
        built, target, contents = self.build(recipe, package=source)
        existing = {"schema": 1, "addons": [{"id": "bonus", "version": "1"}, {"id": "fixture", "version": "0"}],
                    "factions": [{"id": "faction"}], "fixes": [{"id": "fix"}]}
        ac.STATIC.mkdir()
        (ac.STATIC / ac.MANIFEST).write_text(mc.dump_json(existing))
        entry = package.write_entry(built, target, contents)
        package.write_entry(built, target, contents)
        manifest = mc.load_json(ac.STATIC / ac.MANIFEST)
        for key in ("schema", "factions", "fixes"):
            self.assertEqual(manifest[key], existing[key])
        self.assertEqual(set(manifest), set(existing))
        self.assertEqual(manifest["addons"], [*existing["addons"], entry])

    def test_existing_install_and_faction_sources_keep_their_categories(self):
        for kind, key in (("", "addons"), ("fix", "fixes"), ("faction", "factions")):
            with self.subTest(kind=kind):
                recipe = self.recipe(kind)
                source, members = self.source(recipe)
                if kind == "faction":
                    sources = {"package": source}
                else:
                    install = self.root / "install"
                    install.mkdir(exist_ok=True)
                    for name, data in members.items():
                        (install / name.lower()).write_bytes(data)
                    sources = {"install": install}
                built, target, contents = self.build(recipe, **sources)
                entry = package.write_entry(built, target, contents)
                self.assertEqual(ac.list_key(recipe), key)
                self.assertIn(entry, mc.load_json(ac.STATIC / ac.MANIFEST)[key])
                self.assertEqual(ac.packaged_archive_problems(target, recipe, entry), [])

    def test_source_kind_and_converter_metadata_are_checked(self):
        for kind in ("", "fix", "faction", "model"):
            recipe = self.recipe(kind)
            wrong = {"install": self.root} if kind in ("faction", "model") else {"package": self.root}
            with self.subTest(kind=kind), self.assertRaisesRegex(SystemExit, "recipes use"):
                self.build(recipe, **wrong)
        recipe = self.recipe()
        for sources in ({}, {"install": self.root, "package": self.root}):
            with self.assertRaisesRegex(SystemExit, "exactly one"):
                self.build(recipe, **sources)
        source, _ = self.source(recipe, embedded=dict(self.meta, summary="Different metadata."))
        with self.assertRaisesRegex(SystemExit, "differs from the recipe's metadata"):
            self.build(recipe, package=source)
        for omitted in (mc.METADATA_NAME, "Fixture.ufo", "SOURCES.txt"):
            source, _ = self.source(recipe, omit=(omitted,))
            with self.subTest(omitted=omitted), self.assertRaises(SystemExit):
                self.build(recipe, package=source)

    def test_model_recipe_accepts_documents_but_never_a_revision_archive(self):
        recipe = self.recipe()
        self.assertEqual(ac.list_key(recipe), "addons")
        self.assertEqual(ac.recipe_problems(recipe), [])
        changed = copy.deepcopy(recipe)
        changed["archives"] = ["rev31.gp3"]
        self.assertIn("only a fix recipe", "; ".join(ac.recipe_problems(changed)))
        changed = copy.deepcopy(recipe)
        changed.pop("kind")
        self.assertIn("only a faction, fix or model recipe", "; ".join(ac.recipe_problems(changed)))
        changed["kind"] = "unknown"
        self.assertIn("kind 'unknown'", "; ".join(ac.recipe_problems(changed)))


if __name__ == "__main__":
    unittest.main()
