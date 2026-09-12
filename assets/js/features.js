document.querySelectorAll('[data-comparison]').forEach(figure => {
  const stage = figure.querySelector('.comparison-stage');
  const range = figure.querySelector('input[type="range"]');
  const buttons = [...figure.querySelectorAll('[data-position]')];
  function update() {
    const value = Number(range.value);
    stage.style.setProperty('--split', `${value}%`);
    stage.dataset.position = String(value);
    range.setAttribute('aria-valuetext', `${value}% ${buttons[0].textContent}, ${100 - value}% ${buttons[1].textContent}`);
    buttons.forEach(button => button.setAttribute('aria-pressed', String(Number(button.dataset.position) === value)));
  }
  range.addEventListener('input', update);
  function drag(event) {
    const bounds = stage.getBoundingClientRect();
    range.value = String(Math.max(0, Math.min(100, Math.round((event.clientX - bounds.left) / bounds.width * 100))));
    update();
  }
  stage.addEventListener('pointerdown', event => {
    if (event.button !== 0) return;
    stage.setPointerCapture(event.pointerId);
    drag(event);
  });
  stage.addEventListener('pointermove', event => {
    if (stage.hasPointerCapture(event.pointerId)) drag(event);
  });
  stage.addEventListener('dragstart', event => event.preventDefault());
  buttons.forEach(button => button.addEventListener('click', () => { range.value = button.dataset.position; update(); }));
  figure.querySelector('.comparison-controls').hidden = false;
  figure.querySelector('.comparison-hint').hidden = false;
  const inspection = figure.querySelector('.comparison-inspection');
  if (inspection) {
    inspection.hidden = false;
    const magnifications = [...inspection.querySelectorAll('[data-magnification]')];
    magnifications.forEach(button => button.addEventListener('click', () => {
      stage.style.setProperty('--inspection-scale', button.dataset.magnification);
      magnifications.forEach(choice => choice.setAttribute('aria-pressed', String(choice === button)));
    }));
  }
  update();
});
// Motion is opt-in, including for reduced-motion users. Pause clips off screen.
if ('IntersectionObserver' in window) {
  const observer = new IntersectionObserver(entries => entries.forEach(entry => {
    if (!entry.isIntersecting) entry.target.pause();
  }));
  document.querySelectorAll('.renderer-motion video').forEach(video => observer.observe(video));
}
document.addEventListener('visibilitychange', () => {
  if (document.hidden) document.querySelectorAll('.renderer-motion video').forEach(video => video.pause());
});

const gameplayDialog = document.querySelector('.gameplay-dialog');
if (gameplayDialog && typeof gameplayDialog.showModal === 'function') {
  let gameplayTrigger;
  document.querySelectorAll('[data-open-gameplay]').forEach(link => {
    link.addEventListener('click', event => {
      if (event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;
      event.preventDefault();
      gameplayTrigger = link;
      gameplayDialog.showModal();
      document.documentElement.classList.add('gameplay-modal-open');
    });
  });
  gameplayDialog.querySelector('.gameplay-close').addEventListener('click', () => gameplayDialog.close());
  gameplayDialog.addEventListener('click', event => {
    const bounds = gameplayDialog.getBoundingClientRect();
    if (event.target === gameplayDialog && (event.clientX < bounds.left || event.clientX > bounds.right || event.clientY < bounds.top || event.clientY > bounds.bottom)) gameplayDialog.close();
  });
  gameplayDialog.addEventListener('close', () => {
    document.documentElement.classList.remove('gameplay-modal-open');
    gameplayTrigger?.focus();
  });
}

// Paired clips share a timeline; switching effects preserves playback position.
document.querySelectorAll('[data-motion-demo]').forEach(figure => {
  const video = figure.querySelector('video');
  const play = figure.querySelector('.motion-play');
  const variants = [...figure.querySelectorAll('[data-motion-src]')];
  let pendingSeek;
  let switchVersion = 0;
  const syncPlay = () => { play.hidden = !video.paused; };
  play.hidden = false;
  figure.querySelector('.motion-controls').hidden = false;
  play.addEventListener('click', () => video.play().catch(syncPlay));
  video.addEventListener('play', () => {
    figure.classList.add('motion-started');
    play.textContent = 'Resume animation';
    // Keep paused comparison frames unobscured after the initial play overlay.
    figure.querySelector('.motion-controls').append(play);
    syncPlay();
  });
  video.addEventListener('pause', syncPlay);
  figure.querySelector('[data-motion-replay]').addEventListener('click', () => {
    video.currentTime = 0;
    video.play().catch(syncPlay);
  });
  variants.forEach(button => button.addEventListener('click', () => {
    if (button.getAttribute('aria-pressed') === 'true') return;
    const version = ++switchVersion;
    const time = video.currentTime;
    const resume = !video.paused;
    if (pendingSeek) video.removeEventListener('loadedmetadata', pendingSeek);
    pendingSeek = () => {
      if (version !== switchVersion) return;
      video.currentTime = Math.min(time, Math.max(0, video.duration - 0.05));
      if (resume) video.play().catch(syncPlay);
    };
    video.addEventListener('loadedmetadata', pendingSeek, {once: true});
    variants.forEach(choice => choice.setAttribute('aria-pressed', String(choice === button)));
    figure.querySelector('.motion-state').textContent = button.textContent;
    video.poster = button.dataset.motionPoster;
    // Fetch after an explicit toggle so paused comparisons can seek too.
    video.preload = 'auto';
    video.src = button.dataset.motionSrc;
    video.load();
    syncPlay();
  }));
});
