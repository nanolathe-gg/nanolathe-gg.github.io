// Compose the Reddit button from generated concept art and exact brand paths.
// Authoring dependency: Sharp, supplied separately from the website build.
const fs = require('node:fs/promises');
const path = require('node:path');
const sharp = require('sharp');

async function main() {
  const root = path.resolve(__dirname, '..');
  const output = path.join(root, 'static/brand');
  const art = await sharp(path.join(root, 'brand/sources/reddit-button-construction.png'))
    .extract({ left: 0, top: 310, width: 1881, height: 209 })
    .resize(1152, 128)
    .png().toBuffer();
  const original = await fs.readFile(path.join(output, 'wordmark.svg'), 'utf8');
  // Reframe only the transparent canvas; preserve the supplied geometry/colors.
  const wordmark = original.replace(
    'width="426" height="100" viewBox="0 0 426 100"',
    'x="8" y="4.4" width="180" height="23.2" viewBox="9 21 403.45 52"'
  );
  if (wordmark === original) throw new Error('Wordmark canvas changed; review placement.');
  const svg = `<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="288" height="32" viewBox="0 0 288 32" role="img" aria-labelledby="title desc">
<title id="title">Nanolathe</title>
<desc id="desc">Nanolathe's green segmented N and ivory wordmark beside a green construction spray. Original concept artwork.</desc>
<defs><linearGradient id="quiet"><stop offset="0" stop-color="#121516" stop-opacity=".7"/><stop offset=".59" stop-color="#121516" stop-opacity=".62"/><stop offset=".74" stop-color="#121516" stop-opacity="0"/></linearGradient></defs>
<image width="288" height="32" xlink:href="data:image/png;base64,${art.toString('base64')}"/>
<rect width="288" height="32" fill="url(#quiet)"/>
${wordmark}
<rect x=".5" y=".5" width="287" height="31" fill="none" stroke="#78836e" stroke-opacity=".42"/>
</svg>\n`;
  await fs.writeFile(path.join(output, 'reddit-button.svg'), svg);
  for (const scale of [1, 2]) {
    const filename = scale === 1 ? 'reddit-button-288x32.png' : 'reddit-button-576x64.png';
    // Supersampling preserves the tiny diagonal segments and outlined type.
    await sharp(Buffer.from(svg), { density: 288 })
      .resize(288 * scale, 32 * scale)
      .removeAlpha().png({ compressionLevel: 9 })
      .toFile(path.join(output, filename));
    const meta = await sharp(path.join(output, filename)).metadata();
    if (meta.width !== 288 * scale || meta.height !== 32 * scale || meta.hasAlpha) {
      throw new Error(`Unexpected button export: ${filename}`);
    }
    console.log(`${filename}: ${meta.width} × ${meta.height}, opaque PNG`);
  }
}

main().catch(error => { console.error(error); process.exitCode = 1; });
