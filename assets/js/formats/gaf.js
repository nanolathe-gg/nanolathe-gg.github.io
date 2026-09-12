// Progressive enhancements for the original authored fixture. No retail assets.
const player = document.querySelector('[data-gaf-player]');
if (player) {
  const stage = player.querySelector('.sprite-stage');
  const sprite = player.querySelector('[data-sprite]');
  const frames = [...player.querySelectorAll('[data-select-frame]')];
  const slider = player.querySelector('[data-frame]');
  const hold = player.querySelector('[data-hold]');
  const offsets = player.querySelector('[data-offsets]');
  const loop = player.querySelector('[data-loop]');
  const play = player.querySelector('[data-play]');
  const motion = matchMedia('(prefers-reduced-motion: reduce)');
  let selected = 0, timer = null;
  function draw(announce = true) {
    const f = frames[selected].dataset;
    const scale = Math.max(1, Math.min(6, Math.floor((stage.clientWidth - 30) / 64)));
    player.querySelector('[data-scale]').textContent = `${scale}× nearest neighbor · crosshair = anchor`;
    sprite.src = `pulse-${selected}.svg`;
    sprite.width = Number(f.width) * scale; sprite.height = Number(f.height) * scale;
    sprite.style.left = `${offsets.checked ? -Number(f.x)*scale : 0}px`;
    sprite.style.top = `${offsets.checked ? -Number(f.y)*scale : 0}px`;
    sprite.alt = `Original green pulse, frame ${selected}, ${f.width} by ${f.height} pixels`;
    slider.value = selected;
    player.querySelector('[data-frame-label]').textContent = `0${selected} / 05`;
    const readout = player.querySelector('[data-geometry]');
    readout.setAttribute('aria-live', announce ? 'polite' : 'off');
    readout.textContent = `${f.width} × ${f.height} px · offset (${f.x}, ${f.y}) · ${offsets.checked ? 'origin = anchor − offset' : 'offset ignored: top-left lands on anchor'}`;
    frames.forEach((button,i) => button.setAttribute('aria-pressed', String(i === selected)));
  }
  function stop() {
    clearTimeout(timer); timer = null;
    play.textContent = 'Play'; play.setAttribute('aria-pressed', 'false');
  }
  function schedule() {
    timer = setTimeout(() => {
      if (selected === frames.length-1 && !loop.checked) { stop(); return; }
      selected = (selected+1)%frames.length; draw(false); schedule();
    }, Number(hold.value)*100);
  }
  play.addEventListener('click', () => {
    if (timer !== null) { stop(); return; }
    if (selected === frames.length-1) { selected = 0; draw(); }
    play.textContent = 'Pause'; play.setAttribute('aria-pressed','true'); schedule();
  });
  frames.forEach((button, i) => button.addEventListener('click', () => { stop(); selected=i; draw(); }));
  slider.addEventListener('input', () => { stop(); selected=Number(slider.value); draw(); });
  offsets.addEventListener('change', () => draw());
  hold.addEventListener('input', () => {
    player.querySelector('[data-hold-label]').textContent = `${hold.value} tick${hold.value === '1' ? '' : 's'}`;
    if (timer !== null) { clearTimeout(timer); schedule(); }
  });
  document.addEventListener('visibilitychange', () => { if (document.hidden) stop(); });
  motion.addEventListener('change', stop);
  new IntersectionObserver(([entry]) => { if (!entry.isIntersecting) stop(); }).observe(player);
  // Start paused for everyone, including reduced-motion users. Playback is opt-in.
  new ResizeObserver(() => draw(false)).observe(stage);
  draw();
}
const keyToggle = document.querySelector('[data-color-key]');
keyToggle?.addEventListener('change', () => {
  const on = keyToggle.checked;
  const image = document.querySelector('[data-key-image]');
  image.src = on ? 'mask-keyed.svg' : 'mask-storage.svg';
  image.alt = on ? 'Opaque black diamond with transparent corners' : 'Black diamond with opaque blue index 9 corners';
  document.querySelector('[data-key-label]').textContent = on ? 'After · key applied' : 'After · key ignored';
  document.querySelector('[data-key-description]').textContent = on ? 'Index 9 skips the destination. Index 0 stays black.' : 'Ignoring the key paints the entire bounding square.';
});
const clipToggle = document.querySelector('[data-clip]');
clipToggle?.addEventListener('change', () => {
  const clipped = clipToggle.checked;
  const image = document.querySelector('[data-clip-image]');
  image.src = clipped ? 'composition-clipped.svg' : 'composition-destination.svg';
  image.alt = clipped ? 'Children clipped to parent dimensions, losing outer pixels' : 'Children extend beyond the parent boundary, matching destination clipping';
  document.querySelector('[data-clip-label]').textContent = clipped ? 'Parent-sized host canvas' : 'Full destination';
  document.querySelector('[data-clip-description]').textContent = clipped ? 'A parent-sized intermediate raster loses the outer pixels.' : 'The children keep their extensions outside the parent.';
});
const next = document.querySelector('[data-rle-next]');
if (next) {
  let step = 3;
  const statuses = ['Ready · 0 pixels, 0 payload bytes', '05 → skip 2 · 2 pixels, 1 payload byte', '06 04 → repeat index 4 twice · 4 pixels, 3 payload bytes', '04 00 05 → copy indexes 0, 5 · 6 pixels, 6 payload bytes'];
  function render() {
    document.querySelectorAll('[data-command], [data-pixel]').forEach(el => {
      const index = Number(el.dataset.command ?? el.dataset.pixel);
      el.classList.toggle('pending', index >= step);
      el.classList.toggle('current-command', el.hasAttribute('data-command') && index === step-1);
    });
    document.querySelector('[data-rle-status]').textContent = statuses[step];
    next.textContent = step === 3 ? 'Start again' : 'Next command';
  }
  next.addEventListener('click', () => { step = step === 3 ? 0 : step+1; render(); });
  document.querySelector('[data-rle-reset]').addEventListener('click', () => { step=0; render(); });
}
document.querySelectorAll('[data-enhancement]').forEach(el => { el.hidden = false; });
