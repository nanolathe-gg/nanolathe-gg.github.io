// Original fixture decoded at build time. This is an explanatory renderer,
// not an emulation of retail projection, primitive ordering, SHD, or culling.
const explorer = document.querySelector('[data-model]');
if (explorer) {
  const model = JSON.parse(explorer.dataset.model);
  const canvas = explorer.querySelector('[data-model-canvas]');
  const ctx = canvas.getContext('2d');
  // A real depth buffer resolves visibility at each pixel. Sorting whole faces
  // by a centroid cannot handle a mast or deck crossing another piece's face.
  const depthRenderer=makeDepthRenderer();
  function makeDepthRenderer() {
    const surface=document.createElement('canvas');
    const gl=surface.getContext('webgl',{alpha:true,antialias:true,preserveDrawingBuffer:true});
    if(!gl)return null;
    function shader(type,source) {
      const value=gl.createShader(type);gl.shaderSource(value,source);gl.compileShader(value);
      if(!gl.getShaderParameter(value,gl.COMPILE_STATUS))return null;
      return value;
    }
    const vertex=shader(gl.VERTEX_SHADER,`attribute vec3 position; attribute vec3 color; varying vec3 faceColor; void main(){gl_Position=vec4(position,1.0);faceColor=color;}`);
    const fragment=shader(gl.FRAGMENT_SHADER,`precision mediump float; varying vec3 faceColor; void main(){gl_FragColor=vec4(faceColor,1.0);}`);
    if(!vertex||!fragment)return null;
    const program=gl.createProgram();gl.attachShader(program,vertex);gl.attachShader(program,fragment);gl.linkProgram(program);
    if(!gl.getProgramParameter(program,gl.LINK_STATUS))return null;
    const buffer=gl.createBuffer();
    const positionLocation=gl.getAttribLocation(program,'position'),colorLocation=gl.getAttribLocation(program,'color');
    function submit(values,mode) {
      gl.bindBuffer(gl.ARRAY_BUFFER,buffer);gl.bufferData(gl.ARRAY_BUFFER,new Float32Array(values),gl.DYNAMIC_DRAW);
      gl.enableVertexAttribArray(positionLocation);gl.vertexAttribPointer(positionLocation,3,gl.FLOAT,false,24,0);
      gl.enableVertexAttribArray(colorLocation);gl.vertexAttribPointer(colorLocation,3,gl.FLOAT,false,24,12);
      gl.drawArrays(mode,0,values.length/6);
    }
    return {render(polygons,selected,wire,width,height,dpr,scale,bounds) {
      if(surface.width!==width||surface.height!==height){surface.width=width;surface.height=height;}
      gl.viewport(0,0,width,height);gl.useProgram(program);gl.enable(gl.DEPTH_TEST);gl.depthFunc(gl.LEQUAL);
      gl.clearColor(0,0,0,0);gl.clearDepth(1);gl.clear(gl.COLOR_BUFFER_BIT|gl.DEPTH_BUFFER_BIT);
      const triangles=[],edges=[];
      function push(target,p,color) {
        const x=(p[0]*scale+(bounds.width-720*scale)/2)*dpr;
        const y=(p[1]*scale+(bounds.height-460*scale)/2)*dpr;
        target.push(x/width*2-1,1-y/height*2,p[2]/128,...color);
      }
      for(const poly of polygons) {
        const [a,b,c]=poly.world;
        const ab=b.map((v,i)=>v-a[i]),ac=c.map((v,i)=>v-a[i]);
        const normal=[ab[1]*ac[2]-ab[2]*ac[1],ab[2]*ac[0]-ab[0]*ac[2],ab[0]*ac[1]-ab[1]*ac[0]];
        const shade=.72+.18*Math.abs(normal[1]/(Math.hypot(...normal)||1));
        const dim=selected<0||selected===poly.piece?1:.28;
        const hex=model.palette[poly.face.color]||'#87967a';
        const color=[1,3,5].map(i=>parseInt(hex.slice(i,i+2),16)/255*shade*dim);
        // The sample is made of convex flat quads. Triangulation here belongs
        // only to this teaching viewer, never to the retained 3DO records.
        for(let j=1;j<poly.points.length-1;j++)for(const p of [poly.points[0],poly.points[j],poly.points[j+1]])push(triangles,p,color);
        const edgeColor=wire?(selected===poly.piece?[.91,.71,.44]:[.71,.94,.39]):[.08,.125,.09];
        for(let j=0;j<poly.points.length;j++) {
          push(edges,poly.points[j],edgeColor);push(edges,poly.points[(j+1)%poly.points.length],edgeColor);
        }
      }
      if(!wire) {
        // Bias fills away very slightly so their own edges remain visible;
        // rear edges still fail the depth test against nearer geometry.
        gl.enable(gl.POLYGON_OFFSET_FILL);gl.polygonOffset(1,1);submit(triangles,gl.TRIANGLES);gl.disable(gl.POLYGON_OFFSET_FILL);
      }
      submit(edges,gl.LINES);
      return surface;
    }};
  }
  const controls = Object.fromEntries(['piece','wire','origins','plate','explode','orbit','turret'].map(name => [name,explorer.querySelector(`[data-${name}]`)]));
  const readout = explorer.querySelector('[data-model-readout]');
  const radians = degrees => degrees * Math.PI / 180;
  function rotate(v, angle) {
    const c=Math.cos(angle),s=Math.sin(angle);
    return [v[0]*c+v[2]*s,v[1],-v[0]*s+v[2]*c];
  }
  function position(vertex, pieceIndex) {
    const piece=model.pieces[pieceIndex];
    let v=piece.name==='turret' ? rotate(vertex,radians(Number(controls.turret.value))) : [...vertex];
    v=v.map((n,i)=>n+piece.translation[i]);
    if (controls.explode.checked && piece.parent!==null) v[1]+=9;
    return piece.parent===null ? v : position(v,piece.parent);
  }
  function project(v) {
    const [x,y,z]=rotate(v,radians(Number(controls.orbit.value)));
    const elevation=radians(28);
    return [360+x*7,310-(y*Math.cos(elevation)+z*Math.sin(elevation))*7,z*Math.cos(elevation)-y*Math.sin(elevation)];
  }
  function path(points) {
    ctx.beginPath();points.forEach((p,i)=>i ? ctx.lineTo(p[0],p[1]) : ctx.moveTo(p[0],p[1]));ctx.closePath();
  }
  function line(a,b,color,dashed=false) {
    const p=project(a),q=project(b);ctx.beginPath();ctx.moveTo(p[0],p[1]);ctx.lineTo(q[0],q[1]);ctx.strokeStyle=color;ctx.lineWidth=1;ctx.setLineDash(dashed?[5,5]:[]);ctx.stroke();ctx.setLineDash([]);
  }
  function draw(announce=false) {
    if (!ctx||!depthRenderer) return;
    const bounds=canvas.getBoundingClientRect();if(!bounds.width||!bounds.height)return;
    const dpr=Math.min(devicePixelRatio||1,2);
    canvas.width=Math.round(bounds.width*dpr);canvas.height=Math.round(bounds.height*dpr);
    ctx.setTransform(dpr,0,0,dpr,0,0);ctx.fillStyle='#151c1b';ctx.fillRect(0,0,bounds.width,bounds.height);
    const scale=Math.min(bounds.width/(bounds.width<500?480:720),bounds.height/460);
    ctx.translate((bounds.width-720*scale)/2,(bounds.height-460*scale)/2);ctx.scale(scale,scale);
    for(let n=-30;n<=30;n+=5) {line([n,0,-30],[n,0,30],'#2b3831');line([-30,0,n],[30,0,n],'#2b3831');}
    const selected=Number(controls.piece.value),polygons=[];
    model.pieces.forEach((piece,i)=>piece.faces.forEach((face,fi)=> {
      if (fi===piece.selection) return;
      const world=face.indexes.map(j=>position(piece.vertices[j],i));
      const points=world.map(project);
      polygons.push({points,face,piece:i,world});
    }));
    const surface=depthRenderer.render(polygons,selected,controls.wire.checked,canvas.width,canvas.height,dpr,scale,bounds);
    ctx.save();ctx.setTransform(1,0,0,1,0,0);ctx.drawImage(surface,0,0);ctx.restore();
    ctx.globalAlpha=1;
    if(controls.plate.checked) {
      model.pieces.forEach((piece,i)=> {
        if(piece.selection<0)return;
        const face=piece.faces[piece.selection];
        path(face.indexes.map(j=>project(position(piece.vertices[j],i))));
        ctx.fillStyle='#b6ef6333';ctx.fill();ctx.strokeStyle='#b6ef63';ctx.lineWidth=2;ctx.setLineDash([6,4]);ctx.stroke();ctx.setLineDash([]);
      });
    }
    const labels=[];
    if(controls.origins.checked) model.pieces.forEach((piece,i)=> {
      const origin=position([0,0,0],i),p=project(origin);
      if(piece.parent!==null)line(position([0,0,0],piece.parent),origin,'#c4d8ab',true);
      ctx.fillStyle=selected===i?'#e7b66f':'#edf0e7';ctx.beginPath();ctx.arc(p[0],p[1],3.5,0,Math.PI*2);ctx.fill();
      const fontSize=Math.max(12,10/scale);ctx.font=`${fontSize}px monospace`;ctx.textAlign='left';
      const width=ctx.measureText(piece.name).width;
      let label;
      for(const [dx,dy] of [[8,-12],[-width-8,-12],[8,fontSize+12],[-width-8,fontSize+12],[8,-fontSize-24]]) {
        label={x:p[0]+dx,y:p[1]+dy,w:width,h:fontSize};
        if(!labels.some(r=>label.x<r.x+r.w+5&&label.x+label.w+5>r.x&&label.y-fontSize<r.y+5&&label.y+5>r.y-r.h))break;
      }
      labels.push(label);ctx.lineWidth=4;ctx.strokeStyle='#151c1b';ctx.strokeText(piece.name,label.x,label.y);ctx.fillText(piece.name,label.x,label.y);
    });
    explorer.querySelector('[data-orbit-value]').textContent=`${controls.orbit.value}°`;
    explorer.querySelector('[data-turret-value]').textContent=`${controls.turret.value}°`;
    const pose=controls.explode.checked?'exploded display':Number(controls.turret.value)!==0?'preview rotation':'bind pose';
    readout.setAttribute('aria-live',announce?'polite':'off');
    if(selected<0)readout.textContent=`${model.pieces.length} pieces · ${model.pieces.reduce((n,p)=>n+p.vertices.length,0)} vertices · ${model.pieces.reduce((n,p)=>n+p.faces.length,0)} primitives · ${pose}`;
    else {
      const piece=model.pieces[selected];const origin=position([0,0,0],selected).map(v=>Math.abs(v)<.005?'0':Number(v.toFixed(2))).join(', ');
      readout.textContent=`${piece.name} · ${piece.vertices.length} ${piece.vertices.length===1?'vertex':'vertices'} / ${piece.faces.length} faces · origin (${origin}) · ${pose}${piece.faces.length===0?' · locator, no visible surface':''}`;
    }
  }
  if(ctx&&depthRenderer) {
    canvas.hidden=false;explorer.querySelector('[data-model-fallback]').hidden=true;
    explorer.querySelector('[data-model-controls]').hidden=false;
    Object.values(controls).forEach(control=>control.addEventListener('input',()=>draw(true)));
    explorer.querySelector('[data-model-reset]').addEventListener('click',()=> {
      controls.piece.value='-1';controls.orbit.value='-38';controls.turret.value='0';
      ['wire','plate','explode'].forEach(name=>controls[name].checked=false);controls.origins.checked=true;draw(true);
    });
    new ResizeObserver(()=>draw()).observe(canvas);draw();
  }
}
const texture=document.querySelector('[data-texture-preview]');
if(texture) {
  let turn=0;
  const update=()=> {
    const order=[0,1,2,3].map(i=>(i+turn)%4);
    const corners=[0,1,2,3].map(i=>'ABCD'[(i-turn+4)%4]);
    texture.style.transform=`rotate(${turn*90}deg)`;
    texture.alt=`Cycled index order: ${corners.join(', ')} at top-left, top-right, bottom-right and bottom-left`;
    document.querySelector('[data-texture-order]').textContent=`[${order.join(', ')}]`;
    document.querySelector('[data-texture-description]').textContent=`Index order [${order.join(', ')}] → ${corners.join(', ')} around the fixed face.`;
  };
  document.querySelector('[data-texture-rotate]').addEventListener('click',()=>{turn=(turn+1)%4;update();});
  document.querySelector('[data-texture-reset]').addEventListener('click',()=>{turn=0;update();});
  document.querySelector('[data-texture-controls]').hidden=false;
}
