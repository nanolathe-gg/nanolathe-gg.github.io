// Optional authoring tool. Install Sharp separately; website builds do not need Node.
const fs = require('node:fs/promises');
const path = require('node:path');
const sharp = require('sharp');

async function main() {
  const root = path.resolve(__dirname, '..');
  const output = path.join(root, 'static/brand');
  const brand = JSON.parse(await fs.readFile(path.join(root, 'data/brand.json'), 'utf8'));
  for (const asset of brand.assets) {
    const width = asset.file.startsWith('wordmark') ? 1000 : 512;
    await sharp(path.join(output, `${asset.file}.svg`), { density: 192 })
      .resize({ width }).png().toFile(path.join(output, `${asset.file}.png`));
  }
  const favicons = [];
  for (const size of [16, 32, 48]) {
    const png = await sharp(path.join(output, 'favicon.svg'), { density: 192 })
      .resize(size, size).png().toBuffer();
    await fs.writeFile(path.join(output, `favicon-${size}.png`), png);
    favicons.push({ size, png });
  }
  // An ICO directory can contain PNG images; preserve each purpose-sized export.
  const directory = Buffer.alloc(6 + favicons.length * 16);
  directory.writeUInt16LE(1, 2);
  directory.writeUInt16LE(favicons.length, 4);
  let offset = directory.length;
  favicons.forEach(({ size, png }, index) => {
    const entry = 6 + index * 16;
    directory[entry] = size;
    directory[entry + 1] = size;
    directory.writeUInt16LE(1, entry + 4);
    directory.writeUInt16LE(32, entry + 6);
    directory.writeUInt32LE(png.length, entry + 8);
    directory.writeUInt32LE(offset, entry + 12);
    offset += png.length;
  });
  await fs.writeFile(path.join(output, 'favicon.ico'), Buffer.concat([directory, ...favicons.map(({ png }) => png)]));
  for (const [name, size] of [['apple-touch-icon', 180], ['avatar-1024', 1024]]) {
    await sharp(path.join(output, 'avatar.svg'), { density: 192 })
      .resize(size, size).png().toFile(path.join(output, `${name}.png`));
  }
  console.log(`Exported ${brand.assets.length} logo PNGs, favicon sizes, ICO, and profile images.`);
}

main().catch(error => {
  console.error(error);
  process.exitCode = 1;
});
