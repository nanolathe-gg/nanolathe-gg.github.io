"""Authored release listings for the browser build's discovery; no network."""
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


if __name__ == "__main__":
    unittest.main()
