(() => {
  for (const demo of document.querySelectorAll('[data-fbi-yard]')) {
    fetch('example.json').then(r => { if (!r.ok) throw new Error('Missing fixture'); return r.json(); }).then(data => {
      const q = s => demo.querySelector(s);
      const draw = () => {
        const preset = data.presets[Number(q('#fbi-yard-case').value)];
        q('[data-fbi-source]').textContent = preset.source;
        q('[data-fbi-cells]').replaceChildren(...preset.cells.map((cell,i) => {
          const li=document.createElement('li'),strong=document.createElement('strong'),span=document.createElement('span');
          li.dataset.char=cell.character;li.dataset.repeat=String(cell.repeated);
          li.setAttribute('aria-label',`Cell ${i+1}: ${cell.character}, byte ${cell.byte}${cell.repeated?', repeated final character':''}`);
          strong.textContent=cell.character;span.textContent=cell.byte;li.append(strong,span);return li;
        }));
        q('[data-fbi-cells]').classList.toggle('fbi-hide-hex',!q('[data-fbi-hex]').checked);
        const repeated=preset.cells.filter(c=>c.repeated).length;
        q('[data-fbi-status]').textContent=`16 cells decoded; spaces and lowercase g consume no cells. ${repeated ? `${repeated} cells repeat the final recognized character, ${preset.source.at(-1)}.` : 'No final-character repetition is needed.'}`;
      };
      for(const input of demo.querySelectorAll('select,input'))input.addEventListener('change',draw);
      draw();q('[data-fbi-controls]').hidden=false;
    }).catch(()=>{ /* Keep the original static source and sixteen decoded cells. */ });
  }
})();
