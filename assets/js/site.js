const menuButton = document.querySelector('.menu-toggle');
const navigation = document.querySelector('#navigation');
function closeMenu() {
  menuButton?.setAttribute('aria-expanded', 'false');
  navigation?.classList.remove('open');
}
menuButton?.addEventListener('click', () => {
  const open = menuButton.getAttribute('aria-expanded') !== 'true';
  menuButton.setAttribute('aria-expanded', String(open));
  navigation.classList.toggle('open', open);
});
document.addEventListener('keydown', (event) => {
  if (event.key === 'Escape' && menuButton?.getAttribute('aria-expanded') === 'true') {
    closeMenu();
    menuButton.focus();
  }
});
navigation?.querySelectorAll('a').forEach(link => link.addEventListener('click', closeMenu));
document.addEventListener('click', (event) => {
  if (!event.target.closest('.site-header')) closeMenu();
});
document.querySelectorAll('[data-copy]').forEach(button => {
  if (!navigator.clipboard?.writeText) { button.hidden = true; return; }
  const initial = button.textContent;
  let reset;
  button.setAttribute('aria-live', 'polite');
  button.addEventListener('click', async () => {
    const text = document.getElementById(button.dataset.copy)?.textContent;
    if (!text) return;
    clearTimeout(reset);
    try {
      await navigator.clipboard.writeText(text);
      button.textContent = 'Copied';
    } catch {
      button.textContent = 'Select text to copy';
    }
    reset = setTimeout(() => { button.textContent = initial; }, 2200);
  });
});

// The reel loads nothing from YouTube until it is opened; without a dialog or
// with a modified click the ribbon stays an ordinary link to the video.
const reelDialog = document.querySelector('.reel-dialog');
if (reelDialog && typeof reelDialog.showModal === 'function') {
  const stage = reelDialog.querySelector('.reel-stage');
  let reelTrigger;
  document.querySelectorAll('[data-reel]').forEach(link => {
    link.addEventListener('click', event => {
      if (event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;
      event.preventDefault();
      reelTrigger = link;
      const frame = document.createElement('iframe');
      frame.src = `https://www.youtube-nocookie.com/embed/${encodeURIComponent(link.dataset.reel)}?autoplay=1&rel=0`;
      frame.title = 'Nanolathe announcement reel';
      frame.allow = 'autoplay; encrypted-media; picture-in-picture; fullscreen';
      frame.allowFullscreen = true;
      frame.referrerPolicy = 'strict-origin-when-cross-origin';
      stage.replaceChildren(frame);
      reelDialog.showModal();
    });
  });
  reelDialog.querySelector('.reel-close').addEventListener('click', () => reelDialog.close());
  reelDialog.addEventListener('click', event => { if (event.target === reelDialog) reelDialog.close(); });
  reelDialog.addEventListener('close', () => { stage.replaceChildren(); reelTrigger?.focus(); });
}

// Decorative adaptation of the spray described in rendering research [R-P0-19-P]:
// square marks, directed trajectories, a seven-color cycle, and a 30 Hz cadence.
// Coordinates and colors here are authored for the original website illustration;
// this is not a retail-behavior demo and it does not use game assets or engine RNG.
const canvas = document.querySelector('.nano-spray');
if (canvas) {
  const context = canvas.getContext('2d');
  const hero = canvas.parentElement;
  const motionButton = document.querySelector('.motion-toggle');
  const reducedMotion = matchMedia('(prefers-reduced-motion: reduce)');
  const greens = ['#67882e', '#769934', '#8aaa40', '#9bbb50', '#accb62', '#bad779', '#a2bd53'];
  // Tool-tip position measured in the original 1536 × 1024 illustration.
  // All trajectories share this anchor before responsive image placement.
  const source = { x: 964, y: 519 };
  let particles = [], running = false, paused = false, visible = true, frame = 0;
  let previous = 0, accumulator = 0, tick = 0;
  let scale = 1, offsetX = 0, offsetY = 0, width = 0, height = 0;
  function resize() {
    width = hero.clientWidth; height = hero.clientHeight;
    const dpr = Math.min(devicePixelRatio || 1, 2);
    canvas.width = Math.round(width * dpr); canvas.height = Math.round(height * dpr);
    context.setTransform(dpr, 0, 0, dpr, 0, 0);
    // Match the illustration's responsive background framing.
    scale = width <= 650 ? 760 / 1536 : width >= 1600 ? 1600 / 1536 : Math.max(width / 1536, height / 1024);
    const imageWidth = 1536 * scale, imageHeight = 1024 * scale;
    const positionX = width <= 650 ? .5 : width <= 820 ? .65 : width <= 1100 ? .6 : width >= 1600 ? 1 : .5;
    const positionY = width <= 650 ? 1 : width <= 1100 ? .5 : width >= 1600 ? .52 : .55;
    offsetX = (width - imageWidth) * positionX - (width <= 650 ? 155 : 0);
    offsetY = (height - imageHeight) * positionY;
  }
  function step() {
    tick++;
    // Continuous work has two overlapping emitter records, five particles each.
    for (let i = 0; i < 10; i++) {
      const targetX = 957 + (Math.random() - .5) * 95;
      const targetY = 680 + (Math.random() - .5) * 48;
      const life = Math.max(1, Math.trunc(Math.hypot(targetX - source.x, targetY - source.y) / 4));
      particles.push({ x: source.x, y: source.y, dx: (targetX - source.x) / life, dy: (targetY - source.y) / life, life, color: i % 7 });
    }
    particles = particles.filter(p => --p.life >= 0);
    for (const p of particles) { p.x += p.dx; p.y += p.dy; }
  }
  function draw(now) {
    if (!running) return;
    accumulator += Math.min(now - previous, 100); previous = now;
    while (accumulator >= 1000 / 30) { step(); accumulator -= 1000 / 30; }
    context.clearRect(0, 0, width, height);
    for (const p of particles) {
      context.fillStyle = greens[(p.color + tick) % 7];
      context.fillRect(Math.round(offsetX + p.x * scale), Math.round(offsetY + p.y * scale), 2, 2);
    }
    frame = requestAnimationFrame(draw);
  }
  function sync() {
    const shouldRun = !paused && !reducedMotion.matches && visible && !document.hidden;
    if (shouldRun === running) return;
    running = shouldRun;
    if (running) { previous = performance.now(); accumulator = 0; frame = requestAnimationFrame(draw); }
    else { cancelAnimationFrame(frame); }
    if (reducedMotion.matches) context.clearRect(0, 0, width, height);
  }
  if (context) {
    motionButton.hidden = reducedMotion.matches;
    motionButton.addEventListener('click', () => {
      paused = !paused;
      motionButton.setAttribute('aria-pressed', String(paused));
      motionButton.textContent = paused ? 'Play animation' : 'Pause animation';
      sync();
    });
    reducedMotion.addEventListener('change', () => { motionButton.hidden = reducedMotion.matches; sync(); });
    document.addEventListener('visibilitychange', sync);
    new IntersectionObserver(([entry]) => { visible = entry.isIntersecting; sync(); }).observe(hero);
    new ResizeObserver(resize).observe(hero);
    resize(); sync();
  }
}
