// A silent, native engine recording. The image remains a complete fallback.
(() => {
  const picture = document.querySelector('[data-hero-media]');
  if (!picture) return;
  const video = picture.querySelector('video');
  const button = document.querySelector('.hero-motion');
  const reducedMotion = matchMedia('(prefers-reduced-motion: reduce)');
  let visible = false, choice = null, failed = false;
  const desired = () => choice ?? (!reducedMotion.matches && !navigator.connection?.saveData);
  const shouldPlay = () => !failed && desired() && visible && !document.hidden;
  const updateButton = () => { button.textContent = desired() ? 'Pause video' : 'Play video'; };
  function sync() {
    updateButton();
    if (!shouldPlay()) { video.pause(); return; }
    if (!video.getAttribute('src')) video.src = video.dataset.src;
    // Set the property too: Safari's autoplay policy checks the live state.
    video.muted = true;
    video.play()?.catch(() => {
      if (!shouldPlay()) return;
      choice = false;
      updateButton();
    });
  }
  button.hidden = false;
  button.addEventListener('click', () => { choice = !desired(); sync(); });
  video.addEventListener('playing', () => {
    if (!shouldPlay()) { video.pause(); return; }
    picture.classList.add('has-video');
  });
  video.addEventListener('error', () => {
    failed = true;
    video.pause();
    picture.classList.remove('has-video');
    button.hidden = true;
  });
  reducedMotion.addEventListener('change', () => {
    choice = null;
    if (reducedMotion.matches) picture.classList.remove('has-video');
    sync();
  });
  document.addEventListener('visibilitychange', sync);
  if ('IntersectionObserver' in window) {
    new IntersectionObserver(([entry]) => {
      visible = entry.isIntersecting && entry.intersectionRatio >= .05;
      sync();
    }, { threshold: .05 }).observe(picture);
  } else { visible = true; sync(); }
})();
