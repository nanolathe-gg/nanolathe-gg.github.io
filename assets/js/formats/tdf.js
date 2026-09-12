(() => {
  fetch('example.json').then(r => { if (!r.ok) throw new Error('Missing example'); return r.json(); }).then(data => {
    for (const demo of document.querySelectorAll('[data-tdf-duplicates]')) {
      let step = data.states.length - 1; const q = s => demo.querySelector(s);
      const draw = () => {
        const state = data.states[step];
        q('[data-tdf-rows]').replaceChildren(...state.entries.map((entry, i) => {
          const tr = document.createElement('tr'); if (!i) tr.className = 'tdf-selected';
          for (const value of [i ? String(i) : '0 → read', entry.key, entry.value]) { const td = document.createElement('td'); td.textContent = value; tr.append(td); }
          return tr;
        }));
        for (const line of demo.querySelectorAll('[data-tdf-line]')) line.classList.toggle('tdf-current', Number(line.dataset.tdfLine) === step);
        q('[data-tdf-action]').textContent = `After ${state.assignment}: ${state.action}.`;
        q('[data-tdf-result]').textContent = state.lookup;
        q('[data-tdf-prev]').disabled = step === 0; q('[data-tdf-next]').disabled = step === data.states.length - 1;
      };
      q('[data-tdf-prev]').addEventListener('click', () => { step = Math.max(0,step-1); draw(); });
      q('[data-tdf-next]').addEventListener('click', () => { step = Math.min(data.states.length-1,step+1); draw(); });
      draw(); q('[data-tdf-controls]').hidden = false;
    }
    for (const demo of document.querySelectorAll('[data-tdf-values]')) {
      const q = s => demo.querySelector(s);
      const draw = () => {
        const item = data.cases[Number(q('#tdf-value-case').value)];
        q('[data-tdf-authored]').textContent = item.value === null ? '(no x assignment)' : `x=${item.value};`;
        q('[data-tdf-integer]').textContent = item.integer;
        q('[data-tdf-bit]').textContent = `${item.lowBit} · ${item.lowBit ? 'set' : 'clear'}`;
        q('[data-tdf-value-note]').textContent = `${item.value === null ? 'Absent key: return default 7.' : `Present key: parse its decimal prefix to ${item.integer}; the default does not apply.`} The illustrative packed store keeps ${item.integer} & 1 = ${item.lowBit}.`;
      };
      q('select').addEventListener('change',draw); draw(); q('[data-tdf-controls]').hidden=false;
    }
  }).catch(() => { /* Static tables and final source state remain useful. */ });
})();
