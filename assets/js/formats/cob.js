(() => {
  for (const demo of document.querySelectorAll('[data-cob-demo]')) {
    fetch('example.json').then(r => { if (!r.ok) throw new Error('Missing fixture'); return r.json(); }).then(data => {
      let step = 0;
      const q = s => demo.querySelector(s);
      const draw = () => {
        const state = data.states[step];
        q('[data-turret]').setAttribute('transform', `rotate(${state.angle * 360 / 65536} 180 103)`);
        q('svg').setAttribute('aria-label', `Schematic top view: turret target is ${state.angle * 360 / 65536} degrees. This diagram shows the encoded angle, not retail coordinate conversion.`);
        q('[data-cob-angle]').textContent = `Turret target: ${state.angle * 360 / 65536}°`;
        q('[data-cob-action]').textContent = state.action;
        q('[data-cob-stack]').textContent = `[ ${state.stack.length ? state.stack.join(', ') : 'empty'} ]`;
        q('[data-cob-address]').textContent = `word ${state.word} → file byte 0x${(data.codeOffset + state.word * 4).toString(16).toUpperCase()}`;
        q('[data-cob-back]').disabled = step === 0;
        q('[data-cob-next]').disabled = step === data.states.length - 1;
      };
      q('[data-cob-back]').addEventListener('click', () => { step = Math.max(0, step - 1); draw(); });
      q('[data-cob-next]').addEventListener('click', () => { step = Math.min(data.states.length - 1, step + 1); draw(); });
      q('[data-cob-reset]').addEventListener('click', () => { step = 0; draw(); });
      draw(); q('[data-cob-controls]').hidden = false;
    }).catch(() => { /* Keep the static source and diagram readable. */ });
  }
})();

// These laboratories replay bounded, generated teaching traces. They are not
// a general COB VM and do not compile the displayed BOS in the browser.
(() => {
  const motion = document.querySelector('[data-cob-motion]');
  const threads = document.querySelector('[data-cob-threads]');
  const signals = document.querySelector('[data-cob-signals]');
  const reveal = root => root.querySelectorAll('[data-lab-options], [data-lab-controls]').forEach(el => { el.hidden = false; });
  const highlight = (list, indexes) => [...list.children].forEach((li, i) => {
    li.classList.toggle('cob-current-line', indexes.includes(i));
    if (indexes.includes(i)) li.setAttribute('aria-current', 'step');
    else li.removeAttribute('aria-current');
  });
  if (motion && threads) fetch('laboratory.json').then(response => {
    if (!response.ok) throw new Error('Missing laboratory traces');
    return response.json();
  }).then(data => {
    {
      const q = selector => motion.querySelector(selector);
      const mode = q('[data-motion-mode]'), wait = q('[data-motion-wait]');
      const previous = q('[data-prev]'), next = q('[data-next]'), play = q('[data-play]'), progress = q('[data-progress]');
      const reduced = matchMedia('(prefers-reduced-motion: reduce)');
      let index = 0, timer = null;
      const states = () => data.motion[`${mode.value}-${Number(wait.checked)}`];
      const stop = () => {
        clearInterval(timer); timer = null; play.textContent = 'Play motion';
        q('[data-lab-state]').setAttribute('aria-live', 'polite');
      };
      function draw() {
        const trace = states(), state = trace[index];
        const degrees = state.angle * 360 / 65536;
        const angle = `${Number(degrees.toFixed(2))}°`;
        q('[data-motion-angle]').textContent = angle;
        q('[data-motion-busy]').textContent = String(state.busy);
        q('[data-motion-thread]').textContent = index === 0 ? 'Ready' : state.done ? 'Returned' : 'Waiting';
        q('[data-motion-turret]').setAttribute('transform', `rotate(${degrees} 180 155)`);
        q('[data-motion-beacon]').setAttribute('fill', state.done ? '#b6ef63' : '#26362c');
        q('[data-beacon-label]').textContent = state.done ? 'beacon shown' : 'beacon hidden';
        q('[data-motion-picture]').setAttribute('aria-label', `Turret at ${angle}, target 90 degrees. Beacon ${state.done ? 'shown' : 'hidden'}. Turn-speed word ${state.busy}.`);
        q('[data-motion-phase]').textContent = index === 0 ? state.phase : `Tick ${state.tick} · ${state.phase}`;
        q('[data-motion-action]').textContent = state.action;
        q('[data-motion-command]').textContent = `turn turret to y-axis <90> speed <${mode.value}>;`;
        q('[data-wait-line]').classList.toggle('cob-omitted-line', !wait.checked);
        q('[data-wait-line] code').textContent = wait.checked ? 'wait-for-turn turret around y-axis;' : '// wait-for-turn omitted';
        highlight(q('[data-motion-source]'), index === 0 ? [] : state.done ? [2, 3] : [1]);
        previous.disabled = index === 0; next.disabled = index === trace.length - 1;
        progress.max = String(trace.length - 1); progress.value = String(index);
        progress.setAttribute('aria-valuetext', `${q('[data-motion-phase]').textContent}; angle ${angle}; ${state.done ? 'script returned' : 'script not finished'}`);
        if (index === trace.length - 1) stop();
      }
      function restart() { stop(); index = 0; draw(); }
      previous.addEventListener('click', () => { stop(); index = Math.max(0, index - 1); draw(); });
      next.addEventListener('click', () => { stop(); index = Math.min(states().length - 1, index + 1); draw(); });
      progress.addEventListener('input', () => { stop(); index = Number(progress.value); draw(); });
      q('[data-reset]').addEventListener('click', restart);
      mode.addEventListener('change', restart); wait.addEventListener('change', restart);
      play.addEventListener('click', () => {
        if (timer) { stop(); return; }
        if (index === states().length - 1) index = 0;
        q('[data-lab-state]').setAttribute('aria-live', 'off');
        play.textContent = 'Pause motion';
        timer = setInterval(() => { index++; draw(); }, 180);
      });
      // Explicit playback only. Reduced motion keeps the manual step/scrub UI.
      const motionPreference = () => { stop(); play.hidden = reduced.matches; };
      reduced.addEventListener('change', motionPreference); motionPreference();
      document.addEventListener('visibilitychange', () => { if (document.hidden) stop(); });
      new IntersectionObserver(entries => { if (!entries[0].isIntersecting) stop(); }).observe(motion);
      draw(); reveal(motion);
    }
    {
      const q = selector => threads.querySelector(selector);
      const mode = q('[data-thread-mode]'), full = q('[data-thread-full]');
      let index = 0;
      const states = () => data.threads[`${mode.value}-${Number(full.checked)}`];
      function draw() {
        const trace = states(), state = trace[index];
        q('[data-thread-command]').textContent = `${mode.value === '1' ? 'call-script' : 'start-script'} Worker(42);`;
        [...q('[data-thread-slots]').children].forEach((slot, i) => {
          slot.querySelector('strong').textContent = state.slots[i];
          slot.dataset.status = state.slots[i] === 'Free' ? 'free' : /Waiting|Blocked|Occupied/.test(state.slots[i]) ? 'waiting' : 'running';
        });
        q('[data-parent-flag]').textContent = `parentDone = ${Number(state.parent)}`;
        q('[data-child-flag]').textContent = `childDone = ${Number(state.child)}`;
        q('[data-parent-flag]').classList.toggle('cob-flag-set', state.parent);
        q('[data-child-flag]').classList.toggle('cob-flag-set', state.child);
        highlight(q('[data-parent-source]'), state.line === 1 ? [0] : state.line === 2 ? [1, 2] : []);
        highlight(q('[data-worker-source]'), state.line === 3 ? [0, 1] : []);
        q('[data-thread-phase]').textContent = state.phase;
        q('[data-thread-action]').textContent = state.action;
        q('[data-thread-stack]').textContent = state.stack;
        q('[data-prev]').disabled = index === 0; q('[data-next]').disabled = index === trace.length - 1;
      }
      function restart() { index = 0; draw(); }
      q('[data-prev]').addEventListener('click', () => { index = Math.max(0, index - 1); draw(); });
      q('[data-next]').addEventListener('click', () => { index = Math.min(states().length - 1, index + 1); draw(); });
      q('[data-reset]').addEventListener('click', restart);
      mode.addEventListener('change', restart); full.addEventListener('change', restart);
      draw(); reveal(threads);
    }
  }).catch(() => { /* The diagrams, source and prose remain readable. */ });
  if (signals) {
    const q = selector => signals.querySelector(selector);
    let sent = false;
    function draw() {
      const value = [...signals.querySelectorAll('[data-signal-bit]:checked')].reduce((sum, el) => sum | Number(el.value), 0);
      const masks = [Number(q('[data-sender-mask]').value), 2, 3, 4];
      let victims = 0;
      [...q('[data-signal-rows]').children].forEach((row, i) => {
        const match = masks[i] & value;
        if (match) victims++;
        row.querySelector('[data-mask]').textContent = `${masks[i].toString(2).padStart(3, '0')} · mask ${masks[i]}`;
        row.querySelector('[data-intersection]').textContent = `${masks[i]} & ${value} = ${match}`;
        row.querySelector('[data-outcome]').textContent = sent ? match ? 'Terminated' : 'Still active' : match ? 'Would terminate' : 'Would survive';
        row.dataset.victim = String(sent && match !== 0);
      });
      q('[data-send]').textContent = `Send signal ${value}`; q('[data-send]').disabled = sent;
      q('[data-signal-title]').textContent = sent ? `${victims} terminated · ${4 - victims} still active` : `Preview signal ${value} · ${value.toString(2).padStart(3, '0')}`;
      q('[data-signal-action]').textContent = sent ?
        `${masks[0] & value ? 'The sender also matches and stops executing.' : 'The sender survives and can continue.'} Matching slots are released; threads waiting for those slots are woken. Signal termination delivers no completion value to an engine receiver.` :
        'Each row compares its mask with the signal using bitwise AND. The four remaining VM slots are inactive. Changing a control starts a fresh snapshot.';
    }
    q('[data-send]').addEventListener('click', () => { sent = true; draw(); });
    q('[data-reset]').addEventListener('click', () => { sent = false; draw(); });
    signals.querySelectorAll('input, select').forEach(control => control.addEventListener('change', () => { sent = false; draw(); }));
    draw(); reveal(signals);
  }
})();
