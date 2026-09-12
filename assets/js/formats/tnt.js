(() => {
  const root = document.querySelector('[data-tnt-inspector]'); if (!root) return;
  fetch(root.dataset.source).then(r => { if (!r.ok) throw Error('Fixture unavailable'); return r.json(); }).then(data => {
    const layer = root.querySelector('[data-tnt-layer]'), grid = root.querySelector('[data-tnt-grid]'), sea = root.querySelector('[data-tnt-sea]'), water = root.querySelector('[data-tnt-water]');
    const update = () => {
      const level = Number(sea.value), view = layer.value;
      const picture = root.querySelector('[data-tnt-image]'); picture.src = `${view}.svg`;
      picture.alt = {terrain:'Original TNT repeated tile art, a stylized island', heights:'Decoded corner heights; brighter cells are higher', features:'Source words: pale anchor, amber authored fringe, outlined dark void'}[view];
      root.querySelector('[data-tnt-caption]').textContent = {terrain:'Terrain art · 16 × 12 tile placements · 4 unique 32 × 32 tiles',heights:'Corner height · 32 × 24 samples · brighter means higher',features:'Source words · pale: live index 0 · amber: FFFE fringe · dark outline: FFFC void · other cells: FFFF empty'}[view];
      const svg = root.querySelector('[data-tnt-overlay]'); svg.replaceChildren();
      let wet = 0;
      const node = (name, attrs) => { const el = document.createElementNS('http://www.w3.org/2000/svg', name); Object.entries(attrs).forEach(([k,v])=>el.setAttribute(k,v)); svg.append(el); };
      data.heights.forEach((h,i) => { if (h < level) { wet++; if (water.checked) node('rect',{x:i%data.width*16,y:Math.floor(i/data.width)*16,width:16,height:16,fill:'#3facff','fill-opacity':'.48'}); } });
      if (grid.value !== 'none') {
        const step = Number(grid.value); let d='';
        for(let x=0;x<=512;x+=step)d+=`M${x} 0V384`;
        for(let y=0;y<=384;y+=step)d+=`M0 ${y}H512`;
        node('path',{d,fill:'none',stroke:'#e2f1d3','stroke-opacity':'.55','stroke-width':1});
      }
      root.querySelector('[data-tnt-level]').textContent = level;
      root.querySelector('[data-tnt-readout]').textContent = `${wet} / ${data.width*data.height} corner samples below ${level}. Blue marks this byte comparison; it does not simulate interpolated water rendering. Source file sea level remains 35.`;
    };
    [layer,grid,sea,water].forEach(el => el.addEventListener('input',update)); update();root.querySelector('[data-tnt-controls]').hidden=false;
  }).catch(() => { /* Keep the static art and downloads useful when data is unavailable. */ });
})();
