"""Build a portable brand kit and public guide/token downloads. Standard library only."""
from pathlib import Path
import html
import json
import shutil
import zipfile

root = Path(__file__).resolve().parents[1]
output = root / 'static/brand'
brand = json.loads((root / 'data/brand.json').read_text())
colors = {color['token']: color['hex'] for color in brand['colors']}
guides = ['GUIDE.md', 'ARTWORK_PROMPTS.md', 'PAGE_PATTERNS.md', 'README_HEADER.md']
for name in guides:
    shutil.copyfile(root / 'brand' / name, output / name)
(output / 'tokens.json').write_text(json.dumps(brand, indent=2) + '\n')
variables = [f"  --{color['token']}: {color['hex']};" for color in brand['colors']]
variables += [f"  --{role}: {font['stack']};" for role, font in brand['fonts'].items()]
(output / 'tokens.css').write_text('/* Nanolathe brand tokens. Font file is in ../fonts/. */\n:root {\n' + '\n'.join(variables) + '\n}\n')

files = [root/'ASSETS.md', root/'LICENSE', root/'data/brand.json']
files += list((root/'assets/css').glob('*.css'))
files += list((root/'assets/js').glob('*.js'))
files += list((root/'layouts').rglob('*.html'))
files += [root/'scripts/brand.py', root/'scripts/export-brand.cjs', root/'scripts/readme-banner.py']
files += [root/'brand'/name for name in guides]
files += list((root/'static/fonts').glob('*'))
files += [root/'static/images/construction.webp', root/'static/images/readme-construction.webp']
files += list((root/'brand/sources').glob('*.png'))
files += [p for p in output.rglob('*') if p.is_file() and p.suffix in ('.svg','.png','.webp','.ico','.css','.json')]

cards = []
for asset in brand['assets']:
    name, stem = html.escape(asset['name']), asset['file']
    light = stem in ['wordmark-light','wordmark-dark','mark-dark','avatar-light']
    cards.append(f'<article><div class="preview {"light" if light else ""}"><img src="static/brand/{stem}.svg" alt="{name}"></div><h2>{name}</h2><p>{html.escape(asset["description"])}</p><a href="static/brand/{stem}.svg">SVG</a> · <a href="static/brand/{stem}.png">PNG</a></article>')
swatches = ''.join(f'<li><span style="background:{color["hex"]}"></span><strong>{html.escape(color["name"])}</strong> <code>{color["hex"]}</code><p>{html.escape(color["role"])}</p></li>' for color in brand['colors'])
icon_links = ''.join(f'<a href="static/brand/icons/{name}.svg">{(output / f"icons/{name}.svg").read_text()} {name}</a> ' for name in brand['icons'])
catalog = f'''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Nanolathe brand kit</title>
<style>@font-face{{font-family:Chakra;src:url(static/fonts/chakra-petch-semibold.ttf);font-weight:600}}*{{box-sizing:border-box}}body{{margin:0 auto;padding:40px 24px;max-width:1100px;background:{colors['bg']};color:{colors['text']};font:16px/1.6 Arial,sans-serif}}h1,h2{{font-family:Chakra,Arial,sans-serif;font-weight:600;line-height:1.2}}h1{{font-size:44px}}a{{color:{colors['amber']}}}p{{color:{colors['muted']}}}.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:24px}}article{{border:1px solid {colors['line']};padding:20px}}article h2{{font-size:22px}}.preview{{height:140px;display:flex;align-items:center;justify-content:center;padding:18px}}.preview img{{max-width:100%;max-height:120px}}.light{{background:#f1f0e8}}ul{{list-style:none;padding:0;display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:20px}}li span{{display:block;height:50px;margin-bottom:12px;border:1px solid {colors['line']}}}code{{color:{colors['green']}}}.links svg{{vertical-align:middle;margin-right:6px}}.links a{{display:inline-block;margin:8px 15px 8px 0}}</style>
<h1>Nanolathe brand kit</h1><p>Version {brand['version']}. Everything here works offline. Open an SVG for scalable artwork, or use a PNG where vectors are not supported. The wordmarks have outlined lettering.</p>
<div class="links"><a href="brand/GUIDE.md">Design guide</a><a href="brand/ARTWORK_PROMPTS.md">Artwork prompts</a><a href="brand/PAGE_PATTERNS.md">Page patterns</a><a href="static/brand/tokens.css">CSS tokens</a><a href="static/brand/tokens.json">JSON tokens</a></div>
<h2>README header</h2><img src="static/brand/readme-header.png" alt="Nanolathe wordmark and original reactor construction illustration" style="width:100%;height:auto"><p><a href="static/brand/readme-header.png">PNG</a> · <a href="static/brand/readme-header.webp">WebP</a> · <a href="static/brand/readme-header.svg">Editable SVG</a> · <a href="brand/README_HEADER.md">README snippet and source details</a></p>
<h2>Logo assets</h2><div class="grid">{''.join(cards)}</div><h2>Colors</h2><ul>{swatches}</ul>
<h2>Typography</h2><p><a href="static/fonts/chakra-petch-semibold.ttf">Chakra Petch SemiBold</a> for headings and wordmarks. Arial / Helvetica for body copy; system monospace for code. <a href="static/fonts/OFL.txt">Bundled font license</a>.</p>
<h2>Icons</h2><div class="links">{icon_links}</div><h2>Reference artwork</h2><p><a href="static/images/construction.webp">Construction illustration</a> · <a href="ASSETS.md">Provenance and original prompt</a></p><h2>Favicons and profiles</h2><div class="links"><a href="static/brand/favicon.ico">ICO</a><a href="static/brand/favicon.svg">SVG favicon</a><a href="static/brand/apple-touch-icon.png">Apple touch icon</a><a href="static/brand/avatar-1024.png">1024 px avatar</a></div>
</html>'''
readme = '''# Nanolathe brand kit

Open START-HERE.html in your browser for the offline asset catalog.

- brand/GUIDE.md: colors, fonts, logo usage, layout, motion, and voice.
- brand/ARTWORK_PROMPTS.md: reusable style and scene prompts.
- brand/PAGE_PATTERNS.md: Hugo layouts and component examples.
- brand/README_HEADER.md: README banner, embedding snippet, source, and prompt.
- static/brand/: SVG and PNG logos, icons, profile images, favicons, CSS/JSON tokens.
- static/fonts/: Chakra Petch SemiBold and the SIL Open Font License.
- static/images/construction.webp: original concept-art reference.
- brand/sources/readme-construction.png: original README illustration master.
- ASSETS.md: artwork provenance and the original generation prompt.
- assets/, layouts/, scripts/: editable source examples referenced by the guides.

Use the existing wordmarks instead of asking an image generator to redraw the logo.
For a new page or illustration, share the appropriate guide and the assets with your designer or agent.

The assets and catalog are ready to use. To build the full Hugo website, clone
https://github.com/nanolathe-gg/nanolathe-gg.github.io and follow its README.
The source examples here are references, not a standalone website checkout.
'''

# Fixed metadata makes the archive reproducible when its source files are unchanged.
archive = output/'nanolathe-brand-kit.zip'
with zipfile.ZipFile(archive, 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as zip_file:
    def write(name, data):
        info = zipfile.ZipInfo('nanolathe-brand-kit/'+name, date_time=(2026,9,7,0,0,0))
        info.compress_type = zipfile.ZIP_DEFLATED
        info.external_attr = 0o644 << 16
        zip_file.writestr(info, data)
    write('START-HERE.html', catalog.encode())
    write('README.md', readme.encode())
    for path in sorted(set(files)):
        write(path.relative_to(root).as_posix(), path.read_bytes())
print(f'Packaged {len(set(files))+2} files into {archive.name} ({archive.stat().st_size:,} bytes).')
