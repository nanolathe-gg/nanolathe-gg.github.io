"""Compose the README header from original artwork and exact outlined brand geometry.

Authoring-only dependency: fonttools. The illustration is preserved as an image
layer, and the wordmark is copied from its vector source without redrawing it.
"""
from pathlib import Path
import base64
import json
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen

root = Path(__file__).resolve().parents[1]
brand = json.loads((root / 'data/brand.json').read_text())
colors = {color['token']: color['hex'] for color in brand['colors']}
font = TTFont(root / 'static/fonts/chakra-petch-semibold.ttf')
glyphs, cmap = font.getGlyphSet(), font.getBestCmap()

def lettering(text, x, y, size):
    pen = SVGPathPen(glyphs)
    scale = size / font['head'].unitsPerEm
    for character in text:
        glyph = cmap[ord(character)]
        glyphs[glyph].draw(TransformPen(pen, (scale, 0, 0, -scale, x, y)))
        x += font['hmtx'][glyph][0] * scale
    return pen.getCommands()

art = base64.b64encode((root / 'brand/sources/readme-construction.png').read_bytes()).decode()
wordmark = (root / 'static/brand/wordmark.svg').read_text()
wordmark = wordmark.replace('width="426" height="100"', 'x="88" y="235" width="864" height="203"')
tagline = lettering(brand['positioning']['tagline'], 109, 449, 32)
caption = lettering('ORIGINAL CONCEPT ARTWORK', 1710, 739, 16)
banner = f'''<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="2048" height="768" viewBox="0 0 2048 768" role="img" aria-labelledby="title description">
<title id="title">Nanolathe — Open-source 2.5D RTS engine</title>
<desc id="description">The Nanolathe wordmark beside original concept artwork of a reactor core being assembled from a green nanoframe.</desc>
<image width="2048" height="768" xlink:href="data:image/png;base64,{art}"/>
{wordmark}
<path fill="{colors['muted']}" d="{tagline}"/>
<path fill="{colors['muted']}" opacity=".8" d="{caption}"/>
</svg>
'''
(root / 'static/brand/readme-header.svg').write_text(banner)
print('Created self-contained README header SVG with outlined lettering.')
