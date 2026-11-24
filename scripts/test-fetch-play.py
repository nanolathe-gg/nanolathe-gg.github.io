"""Offline checks for browser release discovery and manifest validation."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
fetch_play = __import__("fetch-play")

ENGINE = {"repository": "nanolathe-gg/nanolathe", "prefix": "browser-", "archive": "nanolathe-browser.tar.gz",
          "manifest": "build.json", "sums": "SHA256SUMS"}
NAMES = (ENGINE["archive"], ENGINE["manifest"], ENGINE["sums"])
DOWNLOAD = "https://github.com/nanolathe-gg/nanolathe/releases/download/"


def release(tag, names=NAMES, draft=False, base=DOWNLOAD):
    return {"tag_name": tag, "draft": draft,
            "assets": [{"name": name, "browser_download_url": f"{base}{tag}/{name}"} for name in names]}


class NewestRelease(unittest.TestCase):
    def test_highest_run_number_with_every_asset_wins(self):
        listing = [release("browser-8"), release("browser-12", names=NAMES[:2]), release("browser-11"),
                   release("browser-13", draft=True), release("browser-latest", names=()), release("v1.0"),
                   release("browser-14", base="https://example.com/"), release("browser-9")]
        tag, urls = fetch_play.newest_release(listing, ENGINE)
        self.assertEqual(tag, "browser-11")
        self.assertEqual(urls, {name: f"{DOWNLOAD}browser-11/{name}" for name in NAMES})

    def test_no_complete_release_is_an_error(self):
        with self.assertRaises(LookupError):
            fetch_play.newest_release([release("browser-latest", names=()), release("browser-3", draft=True)], ENGINE)


class Sums(unittest.TestCase):
    def test_sha256sum_lines_are_read_and_names_required(self):
        a, b = "a" * 64, "b" * 64
        text = f"{a}  nanolathe-browser.tar.gz\n{b} *build.json\nnoise\n"
        self.assertEqual(fetch_play.parse_sums(text, NAMES[:2]), {"nanolathe-browser.tar.gz": a, "build.json": b})
        with self.assertRaises(ValueError):
            fetch_play.parse_sums(text, NAMES)


class FilmFontManifest(unittest.TestCase):
    def test_nested_fonts_must_match_the_pinned_asset_paths(self):
        digest = "a" * 64
        files = ["build.json", "game.html", "launcher.js"]
        manifest = {
            "schema": 1, "wasm": f"nanolathe.{digest[:16]}.wasm", "sha256": digest,
            "size": 10, "runtime": f"wasm_exec.{digest[:16]}.js", "host": f"host.{digest[:16]}",
            "files": files,
        }
        self.assertEqual(fetch_play.pb.check_manifest(manifest), manifest)

        font = {"name": "display-cjk.png", "url": "film/display-cjk.png", "size": 10, "sha256": digest}
        with_font = dict(manifest, files=[*files, font["url"]], film_cjk=[font])
        self.assertEqual(fetch_play.pb.check_manifest(with_font), with_font)
        for invalid in (
            dict(with_font, film_cjk=[]),
            dict(with_font, film_cjk=[dict(font, url="../display-cjk.png")]),
            dict(with_font, files=[*files, "film/../display-cjk.png"]),
        ):
            with self.subTest(manifest=invalid), self.assertRaises(ValueError):
                fetch_play.pb.check_manifest(invalid)


if __name__ == "__main__":
    unittest.main()
