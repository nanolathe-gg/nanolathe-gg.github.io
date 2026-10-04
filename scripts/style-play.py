"""Apply the website shell to the engine launcher; preserve its pinned runtime."""
from html.parser import HTMLParser
from pathlib import Path
import re


class Launcher(HTMLParser):
    def __init__(self, text):
        super().__init__()
        self.ids = []
        self.feed(text)

    def handle_starttag(self, tag, attributes):
        value = dict(attributes).get("id")
        if value:
            self.ids.append(value)


def decorate(text):
    original = Launcher(text).ids
    required = {"welcome", "demo", "demo-info", "drop", "folder", "game", "stop",
                "game-view", "controls", "status", "storage-error", "advanced", "saved"}
    if not required.issubset(original):
        raise ValueError("The engine launcher contract changed; review the website shell before publishing")
    header = '''<header class="browser-header">
<a class="browser-brand" href="/" aria-label="Nanolathe home"><img src="/brand/favicon.svg" width="34" height="34" alt=""><span>nanolathe</span></a>
<nav aria-label="Main navigation"><a href="/features/">Features</a><a href="/docs/">Documentation</a><a href="/about/">About</a></nav>
<a class="browser-install" href="/get-started/">Install the beta <span aria-hidden="true">↗</span></a></header>'''
    welcome = '''<section id="welcome" aria-labelledby="demo-title">
<p class="eyebrow">Nanolathe / Browser demo</p><h1 id="demo-title">Play the demo.</h1>
<p id="browser-support">Desktop Chrome or Edge recommended, with a keyboard and mouse.</p>
<div class="demo-recovery-actions">
<button id="demo" disabled>Checking demo availability…</button><span id="demo-info"></span>
<button id="fallback-folder" type="button">Choose game folder</button><a href="/get-started/">Install the native beta <span aria-hidden="true">↗</span></a></div>
<noscript><style>#controls,#advanced,#saved,#status,.demo-recovery-actions{display:none!important}</style><p>Enable JavaScript to play in your browser, or <a href="/get-started/">install the native beta</a>.</p></noscript>
<div id="drop" hidden><input id="folder" type="file" webkitdirectory multiple></div>
<p class="demo-limit">Three original demo missions. The browser uses original texture detail. <a href="/docs/browser-demo/">Browser controls &amp; saves</a>.</p>
</section>'''
    head = '''<meta name="description" content="Play the original three-mission Total Annihilation demo in Nanolathe, an open-source RTS engine. Desktop browser, keyboard and mouse; no installation needed.">
<meta name="theme-color" content="#121516"><link rel="canonical" href="https://nanolathe.gg/play/">
<link rel="icon" href="/brand/favicon.svg" type="image/svg+xml"><link rel="stylesheet" href="/css/browser-play.css">
<script src="/js/browser-play.js" defer></script>'''
    footer = '''<footer class="browser-footer"><span>Nanolathe · Independent, MIT-licensed engine</span><a href="/docs/keyboard-shortcuts/">Controls guide</a><a href="/play/demo/README.txt">Original demo readme</a><a href="https://github.com/nanolathe-gg/nanolathe">Engine source <span aria-hidden="true">↗</span></a></footer>'''
    text, headers = re.subn(r"<header>.*?</header>", header, text, count=1, flags=re.S)
    text, sections = re.subn(r'<section id="welcome">.*?</section>', welcome, text, count=1, flags=re.S)
    if headers != 1 or sections != 1 or "</head>" not in text or "</body>" not in text:
        raise ValueError("The engine launcher structure changed; review it before publishing")
    text = text.replace("</head>", head + "</head>", 1).replace("<body>", '<body class="browser-play">', 1)
    text = text.replace("<summary>Graphics and diagnostics</summary>", "<summary>Options and diagnostics</summary>")
    # The pinned engine binds #stop during bootstrap. Keep an invisible hook
    # until that binding completes; browser-play.js then removes it from the DOM.
    text = re.sub(r'<button id="stop"[^>]*>.*?</button>', '<button id="choose-folder" type="button">Choose game folder</button><button id="stop" hidden aria-hidden="true" tabindex="-1"></button>', text, count=1, flags=re.S)
    text = text.replace('<div id="game-view" hidden>', '''<div id="game-view" hidden>
<div id="demo-loading-panel"><p class="eyebrow">Nanolathe / Browser demo</p><h2>Preparing your first battle.</h2><p>The engine and original demo files are loading. Progress appears below.</p></div>
<div id="game-folder-drop"><strong>Bring your own battlefield.</strong><span>Drop your installed TotalA folder here. Your files stay on your computer.</span></div>''', 1)
    text = text.replace("</body>", footer + "</body>", 1)
    final = Launcher(text).ids
    if not set(original).issubset(final) or len(final) != len(set(final)):
        raise ValueError("The website shell removed an engine control or created duplicate IDs")
    return text


def main():
    import playbuild as pb
    if (pb.STATIC / pb.UNAVAILABLE).exists():
        return
    target = pb.STATIC / "index.html"
    import json
    manifest = json.loads((pb.STATIC / "build.json").read_text())
    original = pb.CACHE / f"launcher-source.{manifest['host']}.html"
    text = target.read_text()
    if '<body class="browser-play">' in text:
        text = original.read_text()
    else:
        original.parent.mkdir(parents=True, exist_ok=True)
        original.write_text(text)
    target.write_text(decorate(text))
    readme = next(row for row in pb.demo_rows() if row["path"].lower() == "tademoreadme.txt")
    source = pb.STATIC / "demo" / readme["url"]
    if source.is_file():
        (pb.STATIC / "demo/README.txt").write_bytes(source.read_bytes())
    print("play: website shell applied; pinned host modules and engine runtime unchanged")


if __name__ == "__main__":
    main()
