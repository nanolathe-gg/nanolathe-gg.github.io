"""Check generated internal destinations, anchors, and required pages without dependencies."""
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit
import sys

root = Path(__file__).resolve().parents[1] / "public"
required = ["index.html", "get-started/index.html", "docs/index.html", "features/index.html", "resources/index.html", "404.html"]
errors = []

class Page(HTMLParser):
    def __init__(self, path):
        super().__init__()
        self.ids = set()
        self.links = []
        self.feed(path.read_text())
    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if "id" in attrs:
            self.ids.add(attrs["id"])
        for attr in ("href", "src"):
            if attr in attrs:
                self.links.append(attrs[attr])

for name in required:
    if not (root / name).is_file():
        errors.append(f"Missing page: {name}")
pages = {path: Page(path) for path in root.rglob("*.html")}
for path, page in pages.items():
    for link in page.links:
        url = urlsplit(link)
        if url.scheme or url.netloc:
            continue
        dest = ((root / unquote(url.path).lstrip('/')) if url.path.startswith('/') else path.parent / unquote(url.path)) if url.path else path
        if dest.is_dir():
            dest /= "index.html"
        dest = dest.resolve()
        if not dest.is_file():
            errors.append(f"{path.relative_to(root)}: missing {link}")
        elif url.fragment and dest in pages and unquote(url.fragment) not in pages[dest].ids:
            errors.append(f"{path.relative_to(root)}: missing anchor {link}")
if (root / "CNAME").read_text().strip() != "nanolathe.gg":
    errors.append("Unexpected custom domain")
if errors:
    print('\n'.join(errors), file=sys.stderr)
    sys.exit(1)
print(f"Checked {len(pages)} HTML pages: internal links, anchors, assets, and CNAME pass.")
