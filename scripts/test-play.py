"""Check published-build integrity and the website/engine launcher boundary."""
import gzip
import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

import playbuild as pb

spec = importlib.util.spec_from_file_location("play_shell", Path(__file__).with_name("style-play.py"))
shell = importlib.util.module_from_spec(spec)
spec.loader.exec_module(shell)


class BrowserBuild(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        wasm, runtime = b"\0asmfixture", b"matching Go runtime fixture"
        digest = pb.sha256(wasm)
        self.manifest = dict(schema=1, version="fixture", wasm=f"nanolathe.{digest[:16]}.wasm",
                             wasm_gz=f"nanolathe.{digest[:16]}.wasm.gz", size=len(wasm), sha256=digest,
                             runtime=f"wasm_exec.{pb.sha256(runtime)[:16]}.js")
        encoded = (json.dumps(self.manifest, sort_keys=True, indent=2) + "\n").encode()
        files = {"game.html": b"<html>fixture</html>", "launcher.js": b"// fixture", "style.css": b"body{}"}
        digest = hashlib.sha256(encoded)
        for name, data in sorted(files.items()):
            digest.update(name.encode() + b"\0" + data)
        self.host = "host." + digest.hexdigest()[:16]
        (self.root / self.host).mkdir()
        for name, data in files.items():
            (self.root / self.host / name).write_bytes(data)
        (self.root / self.host / "build.json").write_bytes(encoded)
        (self.root / self.manifest["wasm"]).write_bytes(wasm)
        (self.root / self.manifest["wasm_gz"]).write_bytes(gzip.compress(wasm))
        (self.root / self.manifest["runtime"]).write_bytes(runtime)
        (self.root / "index.html").write_text(f'<link href="{self.host}/style.css"><script src="{self.host}/launcher.js"></script>')
        self.manifest.update(host=self.host, files=sorted(files) + ["build.json"])
        (self.root / "build.json").write_text(json.dumps(self.manifest))

    def test_complete_build(self):
        self.assertEqual(pb.verify_build(self.root, pb.check_manifest(self.manifest)), [])

    def test_corrupt_engine_module(self):
        (self.root / self.manifest["wasm"]).write_bytes(b"corrupt")
        self.assertTrue(any("digest differs" in p for p in pb.verify_build(self.root, self.manifest)))

    def test_corrupt_host_module(self):
        (self.root / self.host / "launcher.js").write_bytes(b"corrupt")
        self.assertTrue(any("host file bytes" in p for p in pb.verify_build(self.root, self.manifest)))

    def test_mismatched_runtime(self):
        (self.root / self.manifest["runtime"]).write_bytes(b"another Go runtime")
        self.assertTrue(any("runtime bytes" in p for p in pb.verify_build(self.root, self.manifest)))

    def test_reject_foreign_paths_and_duplicate_members(self):
        for files in [["../game.html", "build.json", "launcher.js"], self.manifest["files"] + ["launcher.js"]]:
            with self.assertRaises(ValueError):
                pb.check_manifest(dict(self.manifest, files=files))


class WebsiteShell(unittest.TestCase):
    def fixture(self):
        controls = ["demo", "demo-info", "drop", "folder"]
        other = ["game", "game-view", "controls", "status", "storage-error", "advanced", "saved", "future-engine-control"]
        return ('<html><head></head><body><header>Engine</header><section id="welcome">' +
                ''.join(f'<div id="{name}"></div>' for name in controls) + '</section>' +
                ''.join(f'<div id="{name}"></div>' for name in other) + '</body></html>')

    def test_keeps_every_engine_control(self):
        original = self.fixture()
        result = shell.decorate(original)
        self.assertTrue(set(shell.Launcher(original).ids).issubset(shell.Launcher(result).ids))
        self.assertIn('class="browser-play"', result)
        self.assertIn('href="/get-started/"', result)

    def test_changed_engine_contract_fails(self):
        with self.assertRaises(ValueError):
            shell.decorate(self.fixture().replace('id="game"', 'id="new-game"'))


if __name__ == "__main__":
    unittest.main()
