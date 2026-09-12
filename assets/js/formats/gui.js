(() => {
  for (const demo of document.querySelectorAll('[data-gui-demo]')) {
    fetch('example.json').then(r => { if (!r.ok) throw new Error('Missing fixture'); return r.json(); }).then(data => {
      const q = s => demo.querySelector(s);
      const types = {0: 'panel', 1: 'button', 2: 'listbox', 4: 'scrollbar', 5: 'label'};
      const draw = () => {
        const index = Number(q('#gui-record').value), record = data.gadgets[index];
        const common = {...record.common}, fields = {...record.fields};
        const active = q('[data-gui-active]').checked, grey = q('[data-gui-grey]').checked;
        if (index === 3) { common.active = active ? '1' : '0'; fields.grayedout = grey ? '1' : '0'; }
        const rect = q('[data-gui-outline]');
        for (const [attr, key] of [['x','xpos'],['y','ypos'],['width','width'],['height','height']]) rect.setAttribute(attr, common[key]);
        rect.style.display = q('[data-gui-bounds]').checked ? '' : 'none';
        q('[data-gui-button]').style.display = active ? '' : 'none';
        q('[data-gui-button] rect').setAttribute('fill', grey ? '#697d70' : '#98f5a8');
        q('[data-gui-status]').textContent = `Button: ${active ? (grey ? 'visible but disabled; hover help is still available in retail.' : 'visible and enabled.') : 'hidden (active=0).'}`;
        q('[data-gui-source]').textContent = `[${record.section}] {\n  [COMMON] {\n${Object.entries(common).map(([k,v]) => `    ${k}=${v};`).join('\n')}\n  }\n${Object.entries(fields).map(([k,v]) => `  ${k}=${v};`).join('\n')}\n}`;
        q('[data-gui-description]').textContent = `Record ${index} is a ${types[common.id]} (id ${common.id}). Its authored rectangle is (${common.xpos}, ${common.ypos}), ${common.width} × ${common.height}.${common.assoc ? ` Association ${common.assoc} links the listbox and scrollbar.` : ''} The bracket name does not set its index.`;
        q('svg').setAttribute('aria-label', `Original panel schematic. Selected ${common.name}, bounds ${common.width} by ${common.height} at ${common.xpos}, ${common.ypos}. Deploy button is ${active ? (grey ? 'visible but disabled' : 'visible and enabled') : 'hidden'}.`);
      };
      for (const input of demo.querySelectorAll('input, select')) input.addEventListener('change', draw);
      draw(); q('[data-gui-controls]').hidden = false;
    }).catch(() => { /* Keep the complete static diagram and source record. */ });
  }
})();
