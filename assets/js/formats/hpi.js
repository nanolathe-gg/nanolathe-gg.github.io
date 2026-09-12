(() => {
  const el = document.querySelector('[data-hpi-cipher]');
  if (!el) return;
  const plain = [2, 0, 0, 0, 28, 0, 0, 0];
  const hex = x => x.toString(16).toUpperCase().padStart(2, '0');
  const slider = el.querySelector('input');
  const update = () => {
    const pos = Number(slider.value), p = plain[pos - 20], c = (~(p ^ pos ^ 1)) & 255;
    el.querySelector('[data-hpi-cipher-byte]').textContent = hex(c);
    el.querySelector('[data-hpi-plain-byte]').textContent = hex(p);
    el.querySelector('[data-hpi-position]').textContent = `Absolute archive offset 0x${hex(pos)} · root-node byte +${pos - 20}`;
    el.querySelector('[data-hpi-meaning]').textContent = pos < 24 ? 'Bytes 0–3 of the root: entry count 2 (little-endian).' : 'Bytes 4–7 of the root: entry-list pointer 28 / 0x1C (little-endian).';
    el.querySelector('[data-hpi-formula]').textContent = `${hex(pos)} XOR 01 XOR NOT ${hex(c)} = ${hex(p)} · all results masked to 8 bits`;
  };
  slider.addEventListener('input', update); update(); el.querySelector('[data-hpi-controls]').hidden = false;
})();
