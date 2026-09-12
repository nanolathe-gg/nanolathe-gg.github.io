(() => {
  const root=document.querySelector('[data-ota-schemas]');
  if(root) fetch('example.json').then(r=>{if(!r.ok)throw Error('Fixture unavailable');return r.json();}).then(data=>{
    const select=root.querySelector('select');
    const update=()=>{
      const schema=data.schemas[Number(select.value)], svg=root.querySelector('[data-ota-markers]');svg.replaceChildren();
      const label=`${schema.type}: ${schema.starts.map(([x,z],i)=>`StartPos${i+1} at X ${x} Z ${z}`).join('; ')}`;svg.setAttribute('aria-label',label);
      schema.starts.forEach(([x,z],i)=>{
        const cx=x*640/data.mapWidth,cy=z*480/data.mapHeight;
        const circle=document.createElementNS('http://www.w3.org/2000/svg','circle');Object.entries({cx,cy,r:18,fill:'#d2ec9c',stroke:'#14211a','stroke-width':3}).forEach(([k,v])=>circle.setAttribute(k,v));svg.append(circle);
        const text=document.createElementNS('http://www.w3.org/2000/svg','text');Object.entries({x:cx,y:cy+7,'text-anchor':'middle',fill:'#14211a','font-family':'monospace','font-size':20}).forEach(([k,v])=>text.setAttribute(k,v));text.textContent=i+1;svg.append(text);
      });
      root.querySelector('[data-ota-metal]').textContent=schema.metal;root.querySelector('[data-ota-human-metal]').textContent=schema.humanMetal;root.querySelector('[data-ota-human-energy]').textContent=schema.humanEnergy;root.querySelector('[data-ota-positions]').textContent=label;
    };select.addEventListener('change',update);update();root.querySelector('[data-ota-controls]').hidden=false;
  }).catch(()=>{});
  const discovery=document.querySelector('[data-ota-discovery]');
  if(discovery){
    const middle=discovery.querySelector('[data-ota-middle]'),count=discovery.querySelector('[data-ota-count]');
    const update=()=>{
      const found=middle.checked?3:1,list=discovery.querySelector('[data-ota-probes]');list.replaceChildren();
      for(let i=0;i<=found;i++){const li=document.createElement('li');li.dataset.found=String(i<found);li.textContent=`Schema ${i} → ${i<found?'found':'missing; stop'}`;list.append(li);}
      discovery.querySelector('[data-ota-discovery-result]').textContent=`${found} schema${found===1?'':'s'} discovered. SCHEMACOUNT=${count.value || '(empty)'} is not read.${found===1?' Schema 2 still exists, but the gap prevents discovering it.':''}`;
    };[middle,count].forEach(el=>el.addEventListener('input',update));update();discovery.querySelector('[data-ota-discovery-controls]').hidden=false;
  }
})();
