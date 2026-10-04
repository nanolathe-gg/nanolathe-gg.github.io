(() => {
  const welcome = document.getElementById('welcome');
  if (!welcome) return;
  const demo = document.getElementById('demo');
  const folder = document.getElementById('folder');
  const drop = document.getElementById('drop');
  const support = document.getElementById('browser-support');
  const status = document.getElementById('status');
  const view = document.getElementById('game-view');
  const heading = document.getElementById('demo-title');
  const fallbackFolder = document.getElementById('fallback-folder');
  const mobile = navigator.userAgentData?.mobile === true || /Android|iPhone|iPad|iPod/i.test(navigator.userAgent) ||
    (/Mac/i.test(navigator.platform) && navigator.maxTouchPoints > 1);
  const unsupported = mobile || !window.isSecureContext || !window.WebAssembly || !navigator.locks || !window.crypto?.subtle;
  const automatic = !unsupported;
  let requested = false;
  if (automatic) document.body.classList.add('demo-starting');
  const update = () => {
    const stop = document.getElementById('stop');
    if (stop?.onclick) stop.remove();
    // A stopped or failed engine retires its viewport. Expose retry and local
    // folder controls without automatically launching the same failed source.
    if (welcome.hidden && view.hidden) welcome.hidden = false;
    document.body.classList.toggle('is-running', welcome.hidden);
    if (welcome.hidden || (requested && !demo.disabled) || /unavailable|failed|already running/i.test(demo.textContent + status.textContent)) {
      document.body.classList.remove('demo-starting');
    }
    if (!unsupported) {
      const unavailable = /unavailable/i.test(demo.textContent);
      if (!welcome.hidden && (unavailable || (requested && !demo.disabled))) {
        const title = unavailable ? 'The demo is unavailable.' : 'The demo couldn’t start.';
        if (heading.textContent !== title) heading.textContent = title;
        if (!demo.disabled && demo.textContent === 'Try the demo') demo.textContent = 'Retry demo';
      }
      if (automatic && !requested && !demo.disabled) {
        requested = true;
        queueMicrotask(() => demo.click());
      }
      return;
    }
    document.body.classList.add('unsupported-browser');
    if (!demo.disabled) demo.disabled = true;
    const label = mobile ? 'Desktop computer required' : 'Supported browser required';
    if (demo.textContent !== label) demo.textContent = label;
    if (!folder.disabled) folder.disabled = true;
    if (!fallbackFolder.disabled) fallbackFolder.disabled = true;
    const title = mobile ? 'Play on a desktop computer.' : 'Use a supported browser.';
    if (heading.textContent !== title) heading.textContent = title;
    const message = mobile
      ? 'Open this page on a desktop computer with a keyboard and mouse to play. Chrome, Edge and Safari are supported.'
      : 'This browser cannot start the demo here. Use desktop Chrome, Edge or Safari over HTTPS, or install the native beta.';
    if (support.textContent !== message) support.textContent = message;
  };
  update();
  new MutationObserver(update).observe(welcome, {subtree: true, childList: true, attributes: true, attributeFilter: ['disabled', 'hidden']});
  new MutationObserver(update).observe(status, {subtree: true, childList: true, characterData: true});
  if (unsupported) {
    for (const type of ['pointerover', 'focusin', 'dragenter', 'click', 'drop']) welcome.addEventListener(type, event => {
      if (type === 'pointerover' || type === 'focusin' || type === 'dragenter') {
        event.stopImmediatePropagation(); return;
      }
      if (event.target.closest('a, summary')) return;
      event.stopImmediatePropagation();
      if (type === 'click' || type === 'drop') event.preventDefault();
    }, true);
  }
  for (const id of ['choose-folder', 'fallback-folder']) document.getElementById(id)?.addEventListener('click', () => { if (!folder.disabled) folder.click(); });
  const parentEntry = entry => {
    if (!entry) return null;
    if (entry.isFile) return {isFile: true, isDirectory: false, name: entry.name,
      file: (resolve, reject) => entry.file(file => resolve(new File([file], file.name, {
        type: file.type, lastModified: file.lastModified,
      })), reject)};
    return {isFile: false, isDirectory: true, name: entry.name, createReader: () => {
      const reader = entry.createReader();
      return {readEntries: (resolve, reject) => reader.readEntries(entries => resolve(entries.map(parentEntry)), reject)};
    }};
  };
  const incoming = event => {
    if (unsupported || !Array.from(event.dataTransfer?.types || []).includes('Files')) return;
    event.preventDefault(); event.stopImmediatePropagation();
    if (event.type === 'drop') {
      document.body.classList.remove('folder-drag', 'demo-starting');
      // Reuse the engine's normal folder collector and source-switch lifecycle.
      // It retires the prior runtime before mounting the new local handles.
      // Files dropped into the game arrive from its iframe. Bind their Blob
      // handles to this parent before the engine discards that browsing
      // context, so later arrayBuffer reads survive the source switch.
      const items = Array.from(event.dataTransfer.items, item => ({
        webkitGetAsEntry: () => parentEntry(item.webkitGetAsEntry?.()),
      }));
      drop.ondrop?.({preventDefault: () => event.preventDefault(), dataTransfer: {items}});
    } else if (event.type === 'dragleave') {
      if (!event.relatedTarget) document.body.classList.remove('folder-drag');
    } else document.body.classList.add('folder-drag');
  };
  for (const type of ['dragenter', 'dragover', 'dragleave', 'drop']) document.addEventListener(type, incoming, true);
  document.addEventListener('dragend', () => document.body.classList.remove('folder-drag'));
  const frames = new WeakSet();
  const bindFrame = () => {
    const frame = document.getElementById('game');
    if (!frame || frames.has(frame)) return;
    frames.add(frame);
    frame.addEventListener('load', () => {
      const child = frame.contentDocument;
      if (!child || frame.contentWindow.location.origin !== location.origin) return;
      for (const type of ['dragenter', 'dragover', 'dragleave', 'drop']) child.addEventListener(type, incoming, true);
      let pointerSeen = false;
      for (const type of ['mousemove', 'mousedown', 'pointerdown']) child.addEventListener(type, event => {
        if (event.isTrusted && event.target.tagName === 'CANVAS') pointerSeen = true;
      }, true);
      const focus = () => {
        const canvas = child.querySelector('canvas');
        if (!canvas) return false;
        // The browser engine starts with cursor (0, 0) until its first mouse
        // event. Seed a neutral position while its input adapter initializes,
        // or immediate focus would edge-scroll away from the first battle.
        // A real pointer event takes over immediately. No click/order is sent.
        const until = performance.now() + 2000;
        const seed = () => {
          if (pointerSeen || !frame.isConnected || performance.now() >= until) return;
          const rect = canvas.getBoundingClientRect();
          if (rect.width && rect.height) canvas.dispatchEvent(new child.defaultView.MouseEvent('mousemove', {
            clientX: rect.left + rect.width / 2, clientY: rect.top + rect.height / 2, bubbles: true,
          }));
          child.defaultView.requestAnimationFrame(seed);
        };
        seed();
        frame.focus(); canvas.focus(); return true;
      };
      if (!focus()) {
        const observer = new MutationObserver(() => { if (focus()) observer.disconnect(); });
        observer.observe(child.body, {subtree: true, childList: true});
      }
    });
  };
  bindFrame();
  new MutationObserver(() => { bindFrame(); update(); }).observe(view, {childList: true, attributes: true, attributeFilter: ['hidden']});
})();
