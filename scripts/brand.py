"""Rebuild the outlined SVG brand assets. Authoring-only dependency: fonttools."""
from pathlib import Path
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen

root = Path(__file__).resolve().parents[1]
dest = root / "static/brand"
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
for name, text, green in [("wordmark", "#edf0e7", "#b6ef63"), ("wordmark-light", "#17210f", "#4c771d")]:
    (dest / f"{name}.svg").write_text(f'<svg xmlns="http://www.w3.org/2000/svg" width="{x+12:.0f}" height="100" viewBox="0 0 {x+12:.0f} 100"><title>Nanolathe</title><g transform="translate(0 18)" fill="{green}">{mark}</g><path fill="{text}" d="{letters}"/></svg>\n')
(dest / 'mark.svg').write_text(f'<svg xmlns="http://www.w3.org/2000/svg" width="64" height="64" viewBox="0 0 64 64"><title>Nanolathe mark</title><g fill="#b6ef63">{mark}</g></svg>\n')
(dest / 'favicon.svg').write_text(f'<svg xmlns="http://www.w3.org/2000/svg" width="64" height="64" viewBox="0 0 64 64"><rect width="64" height="64" rx="10" fill="#10130f"/><g fill="#b6ef63">{mark}</g></svg>\n')
(dest / 'avatar.svg').write_text(f'<svg xmlns="http://www.w3.org/2000/svg" width="512" height="512" viewBox="0 0 512 512"><title>Nanolathe avatar</title><rect width="512" height="512" fill="#10130f"/><path stroke="#35452a" fill="none" d="M36 82V36h46M430 36h46v46M476 430v46h-46M82 476H36v-46"/><g transform="translate(81 81) scale(5.45)" fill="#b6ef63">{mark}</g></svg>\n')
(root/'layouts/partials/mark.html').write_text(f'<svg class="brand-mark" width="34" height="34" viewBox="0 0 64 64" aria-hidden="true"><g fill="currentColor">{mark}</g></svg>\n')
print('Created outlined wordmarks, mark, favicon, avatar, and header partial.')
