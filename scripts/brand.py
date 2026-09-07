"""Rebuild the outlined SVG brand assets. Authoring-only dependency: fonttools."""
from pathlib import Path
import json
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen

root = Path(__file__).resolve().parents[1]
dest = root / "static/brand"
brand = json.loads((root / "data/brand.json").read_text())
colors = {color['token']: color['hex'] for color in brand['colors']}
font = TTFont(root / "static/fonts/chakra-petch-semibold.ttf")
glyphs, cmap = font.getGlyphSet(), font.getBestCmap()
scale = 72 / font["head"].unitsPerEm
pen = SVGPathPen(glyphs)
x = 84
for char in "nanolathe":
    glyph = cmap[ord(char)]
    glyphs[glyph].draw(TransformPen(pen, (scale, 0, 0, -scale, x, 73)))
    x += font["hmtx"][glyph][0] * scale - 1
letters = pen.getCommands()
mark = '<path d="M9 53V11h12v42ZM23 13l18 21v17L23 30ZM43 11h12v42H43ZM45 3h6v5h-6ZM54 3h5v5h-5ZM58 12h4v5h-4Z"/>'
for name, text, green in [("wordmark", colors['text'], colors['green']), ("wordmark-light", "#17210f", "#4c771d"), ("wordmark-white", "#ffffff", "#ffffff"), ("wordmark-dark", "#17210f", "#17210f")]:
    (dest / f"{name}.svg").write_text(f'<svg xmlns="http://www.w3.org/2000/svg" width="{x+12:.0f}" height="100" viewBox="0 0 {x+12:.0f} 100"><title>Nanolathe</title><g transform="translate(0 18)" fill="{green}">{mark}</g><path fill="{text}" d="{letters}"/></svg>\n')
for name, color in [('mark',colors['green']),('mark-white','#ffffff'),('mark-dark','#17210f')]:
    (dest / f'{name}.svg').write_text(f'<svg xmlns="http://www.w3.org/2000/svg" width="64" height="64" viewBox="0 0 64 64"><title>Nanolathe mark</title><g fill="{color}">{mark}</g></svg>\n')
(dest / 'mark-outline.svg').write_text(f'<svg xmlns="http://www.w3.org/2000/svg" width="64" height="64" viewBox="0 0 64 64"><title>Nanolathe construction outline</title><g fill="none" stroke="{colors["green"]}" stroke-width="1.2">{mark}</g></svg>\n')
(dest / 'favicon.svg').write_text(f'<svg xmlns="http://www.w3.org/2000/svg" width="64" height="64" viewBox="0 0 64 64"><rect width="64" height="64" rx="10" fill="{colors["bg"]}"/><g fill="{colors["green"]}">{mark}</g></svg>\n')
for name, background, ink in [('avatar',colors['bg'],colors['green']),('avatar-light','#f1f0e8','#4c771d')]:
    (dest / f'{name}.svg').write_text(f'<svg xmlns="http://www.w3.org/2000/svg" width="512" height="512" viewBox="0 0 512 512"><title>Nanolathe avatar</title><rect width="512" height="512" fill="{background}"/><path stroke="{colors["amber-line"]}" fill="none" d="M36 82V36h46M430 36h46v46M476 430v46h-46M82 476H36v-46"/><g transform="translate(81 81) scale(5.45)" fill="{ink}">{mark}</g></svg>\n')
(root/'layouts/partials/mark.html').write_text(f'<svg class="brand-mark" width="34" height="34" viewBox="0 0 64 64" aria-hidden="true"><g fill="currentColor">{mark}</g></svg>\n')
icons = {
    'arrow-right': '<path d="M5 12h14M13 6l6 6-6 6"/>',
    'external-link': '<path d="M13 4h7v7M20 4 10 14M9 4H4v16h16v-5"/>',
    'download': '<path d="M12 3v12M7 10l5 5 5-5M4 16v5h16v-5"/>',
    'code': '<path d="m7 6-5 6 5 6M17 6l5 6-5 6M14 3l-4 18"/>',
    'layers': '<path d="m12 3 10 5-10 5L2 8Zm-10 9 10 5 10-5M2 16l10 5 10-5"/>',
    'book': '<path d="M12 5v16M12 5C9 3 6 3 2 3v16c4 0 7 0 10 2 3-2 6-2 10-2V3c-4 0-7 0-10 2Z"/>',
    'archive': '<path d="M3 3h18v5H3ZM5 8v13h14V8M9 12h6"/>',
    'pause': '<path d="M6 4h4v16H6ZM14 4h4v16h-4Z"/>',
    'play': '<path d="m7 3 14 9-14 9Z"/>',
    'copy': '<path d="M8 8h13v13H8ZM16 8V3H3v13h5"/>',
}
(dest / 'icons').mkdir(exist_ok=True)
for name in brand['icons']:
    (dest / f'icons/{name}.svg').write_text(f'<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="butt" stroke-linejoin="miter"><title>{name.replace("-"," ").title()}</title>{icons[name]}</svg>\n')
print('Created brand SVG variants, icons, and header partial.')
