(() => {
  const root=document.querySelector('[data-tad-smartpak]');
  if(root)fetch('example.json').then(r=>{if(!r.ok)throw Error('Fixture unavailable');return r.json();}).then(data=>{
    let index=0;const prev=root.querySelector('[data-tad-previous]'),next=root.querySelector('[data-tad-next]');
    const render=()=>{const step=data.steps[index];root.querySelector('[data-tad-step]').textContent=`${index+1} / ${data.steps.length} · ${step.name}`;root.querySelector('[data-tad-token]').textContent=step.bytes;root.querySelector('[data-tad-output]').textContent=step.output;root.querySelector('[data-tad-counter]').textContent=`Next tick: ${step.counter}. FE sets the counter; FD and FF each emit one sync and advance it.`;prev.disabled=index===0;next.disabled=index===data.steps.length-1;};
    prev.addEventListener('click',()=>{index=Math.max(0,index-1);render();});next.addEventListener('click',()=>{index=Math.min(data.steps.length-1,index+1);render();});render();root.querySelector('[data-tad-controls]').hidden=false;
  }).catch(()=>{});
  const cat=document.querySelector('[data-tad-catalog]');if(!cat)return;
  const rows=cat.querySelector('[data-tad-rows]'),max=cat.querySelector('[data-tad-max]');
  const update=()=>{
    if(!rows.validity.valid||!max.validity.valid||rows.value===''||max.value===''){cat.querySelector('[data-tad-catalog-output]').textContent='Enter positive whole numbers from 1 to 65535 to inspect the illustrative context.';return;}
    const c=Number(rows.value),m=Number(max.value),w=Math.floor(Math.log2(c))+1;
    cat.querySelector('[data-tad-width]').textContent=`${c} retained rows, including row zero → W = ${w} bits`;
    const bits=cat.querySelector('[data-tad-bits]');bits.replaceChildren();for(let i=0;i<w;i++)bits.append(document.createElement('span'));
    cat.querySelector('[data-tad-catalog-output]').textContent=`At tick 600, scheduled slot = 600 mod ${m} = ${600%m}. With no movement entries and present nonempty status, health starts at absolute bit ${73+w}. Changing maxUnits does not change W. This is a grammar calculator, not a claim that every combination is a viable session.`;
  };[rows,max].forEach(el=>el.addEventListener('input',update));update();cat.querySelector('[data-tad-catalog-controls]').hidden=false;
})();
