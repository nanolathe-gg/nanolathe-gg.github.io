// Preview byte-derived assets from authored fixtures, not a browser SMK decoder.
document.querySelectorAll('[data-zrb-player]').forEach(root => {
  fetch(root.dataset.zrbSource).then(response => {
    if (!response.ok) throw new Error('Fixture unavailable');
    return response.json();
  }).then(data => {
    const get = name => root.querySelector(`[data-zrb-${name}]`);
    const play = get('play'), slider = get('frame'), speed = get('speed');
    const motion = matchMedia('(prefers-reduced-motion: reduce)');
    const jumps = root.querySelectorAll('[data-zrb-jump]');
    let selected = Number(root.dataset.zrbStart), timer = null;
    // Warm only the frames each example exposes.
    const previewFrames = play ? data.frames : [...jumps].map(button => data.frames[Number(button.dataset.zrbJump)]);
    for (const frame of previewFrames) {
      for (const kind of ['frame', 'blocks']) {
        const image = new Image();
        image.src = `${data.prefix}${kind}-${frame.index}.svg`;
      }
    }
    function draw() {
      const frame = data.frames[selected];
      if (slider) {
        slider.value = selected;
        slider.setAttribute('aria-valuetext', `Frame ${selected} of ${data.frames.length - 1}`);
        get('frame-label').textContent = `${String(selected).padStart(2, '0')} / ${data.frames.length - 1}`;
      }
      get('image').src = `${data.prefix}frame-${selected}.svg`;
      get('image').alt = `Frame ${selected}: ${frame.description}`;
      get('blocks').src = `${data.prefix}blocks-${selected}.svg`;
      get('blocks').alt = `Frame ${selected}: ${frame.solid} solid writes and ${frame.retained} retained blocks`;
      get('solid').textContent = `${frame.solid} / 128`;
      get('retained').textContent = `${frame.retained} / 128`;
      get('palette').textContent = `${frame.paletteBytes} bytes`;
      get('packet').textContent = `Packet ${selected} · offset ${frame.offset} · ${frame.size} bytes · mask 0x${frame.mask.toString(16).padStart(2, '0').toUpperCase()}`;
      get('note').textContent = frame.note;
      const doubled = get('double')?.checked ?? false;
      root.dataset.double = String(doubled);
      get('extent').textContent = doubled
        ? 'Display extent · 64 × 64; each stored row is repeated.'
        : 'Stored extent · each block is 4 × 4 pixels.';
      if (get('show-blocks')) {
        root.dataset.showBlocks = String(get('show-blocks').checked);
        get('block-panel').hidden = !get('show-blocks').checked;
      }
      jumps.forEach(button => button.setAttribute('aria-pressed', String(Number(button.dataset.zrbJump) === selected)));
    }
    function stop() {
      clearTimeout(timer);
      timer = null;
      if (play) {
        play.textContent = 'Play';
        play.setAttribute('aria-pressed', 'false');
      }
    }
    function schedule() {
      timer = setTimeout(() => {
        if (selected === data.frames.length - 1 && !get('loop').checked) { stop(); return; }
        selected = (selected + 1) % data.frames.length;
        draw();
        schedule();
      }, Number(speed.value));
    }
    play?.addEventListener('click', () => {
      if (timer !== null) { stop(); return; }
      if (selected === data.frames.length - 1) { selected = 0; draw(); }
      play.textContent = 'Pause';
      play.setAttribute('aria-pressed', 'true');
      schedule();
    });
    slider?.addEventListener('input', () => { stop(); selected = Number(slider.value); draw(); });
    get('step')?.addEventListener('click', () => { stop(); selected = (selected + 1) % data.frames.length; draw(); });
    jumps.forEach(button => button.addEventListener('click', () => {
      stop(); selected = Number(button.dataset.zrbJump); draw();
    }));
    get('double')?.addEventListener('change', draw);
    get('show-blocks')?.addEventListener('change', draw);
    speed?.addEventListener('change', () => { if (timer !== null) { clearTimeout(timer); schedule(); } });
    document.addEventListener('visibilitychange', () => { if (document.hidden) stop(); });
    motion.addEventListener('change', stop);
    new IntersectionObserver(([entry]) => { if (!entry.isIntersecting) stop(); }).observe(root);
    // Motion starts paused, including with reduced motion. Play is always opt-in.
    draw();
    get('controls').hidden = false;
    get('help').firstChild.textContent = 'Views are generated from the decoded SMK2 download. ';
  }).catch(() => {
    root.querySelector('[data-zrb-help]').firstChild.textContent = 'Interactive preview unavailable; the static frame and downloads remain available. ';
  });
});
