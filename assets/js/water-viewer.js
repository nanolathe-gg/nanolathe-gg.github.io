// Browser water study: original frozen 3DO meshes, palette textures and real
// projected water mask. Water equations ported from Nanolathe 617540c5;
// WebGL raster/depth and reflection resolve differ from the native renderer.
(() => {
  const root = document.querySelector('[data-water-viewer]');
  if (!root) return;
  const q = s => root.querySelector(s), canvas = q('canvas');
  const status = q('[data-water-status]'), phaseControl = q('[data-water-phase]');
  const playButton = q('[data-water-play]'), checks = [...root.querySelectorAll('[data-water-effect]')];
  const reducedMotion=window.matchMedia('(prefers-reduced-motion: reduce)');
  const defaults = { surface: 1, motion: 1, foam: 1, reflections: 1 };
  let modelsDirty = true;
  let effects = { ...defaults }, scene, resources, gl, programs, quad, textures, models, layers;
  let phase = 0, playing = !reducedMotion.matches, visible = false, ready = false, lost = false;
  let started = false, pending = 0, previous = 0;

  const quadVS = `attribute vec2 aPosition; varying vec2 vUV;
    void main() { gl_Position=vec4(aPosition,0.0,1.0); vUV=(vec2(aPosition.x,-aPosition.y)+1.0)*0.5; }`;
  const waterMath = `
    float noise(vec2 p) {
      vec2 f=fract(p),a=floor(p); a-=floor(a/289.0)*289.0;
      vec2 b=a+1.0; b-=floor(b/289.0)*289.0; f=f*f*(3.0-2.0*f);
      vec4 h=vec4(dot(a,vec2(43.17,97.53)),dot(vec2(b.x,a.y),vec2(43.17,97.53)),dot(vec2(a.x,b.y),vec2(43.17,97.53)),dot(b,vec2(43.17,97.53)));
      h=fract(sin(h)*17341.23); return mix(mix(h.x,h.y,f.x),mix(h.z,h.w,f.x),f.y);
    }
    vec3 field(vec2 pattern,vec2 drift,float t) {
      float gust=smoothstep(0.30,0.80,noise((pattern-drift*22.0)*0.0055+vec2(3.0,7.0)));
      vec2 p=(pattern-drift*6.0)*0.07;
      float a=noise(pattern*0.018+vec2(7.0,13.0))*6.283185, b=noise(pattern*0.023+vec2(31.0,3.0))*6.283185;
      vec2 warp=0.5+vec2(sin(t*0.65+a),sin(t*0.83+b))*2.5;
      p+=(warp-0.5)*1.6; float broad=noise(p);
      vec2 r=(pattern-drift*11.0)*0.166;
      r=vec2(r.x*0.7986-r.y*0.6018,r.x*0.6018+r.y*0.7986)+(warp-0.5)*0.9;
      return vec3(broad,noise(r),gust);
    }
    vec2 waterOffset(vec3 f) { return (f.xy-0.5)*4.4*(0.7+0.5*f.z); }
    vec3 waterShade(vec3 c,vec3 f,float deep) {
      float ripple=f.x*0.65+f.y*0.35-0.5;
      float shade=1.0+ripple*0.152*(0.7+0.5*f.z)*deep-0.025*f.z*deep;
      float crest=smoothstep(0.10,0.32,ripple);
      return mix(c*shade,vec3(0.40,0.67,0.78),clamp(crest*0.06*deep,0.0,1.0));
    }`;
  const sceneFS = `precision highp float; varying vec2 vUV;
    uniform sampler2D uTerrain,uMask,uDamp,uAbove,uSub,uReflection;
    uniform vec2 uSize,uCamera,uMaskOrigin,uMaskSize,uDrift;
    uniform float uMaskStep,uZoom,uPhase,uSurface,uMotion,uFoam,uReflections,uEnergy;
    ${waterMath}
    vec4 layer(sampler2D image,vec2 p) { return texture2D(image,vec2(p.x,1.0-p.y)); }
    vec4 over(vec4 a,vec4 b) { return a+b*(1.0-a.a); }
    vec4 wet(vec2 world) {
      vec2 uv=(world-uMaskOrigin)/uMaskStep/uMaskSize;
      return vec4(texture2D(uMask,uv).rgb,texture2D(uDamp,uv).r);
    }
    void main() {
      vec2 screen=vUV*uSize,world=uCamera+screen/uZoom;
      vec4 mask=wet(world),base=texture2D(uTerrain,vUV),original=base;
      float rawCover=smoothstep(0.8,1.0,mask.r);
      float cover=rawCover*smoothstep(0.0,0.35,mask.g),deep=smoothstep(0.05,0.55,mask.g);
      float dry=smoothstep(0.05,0.5,mask.b)*(1.0-rawCover),damp=mask.a*dry*uSurface;
      float lapDry=pow(max(0.0,sin(uPhase*1.6+noise(world/0.5*0.025)*3.0)),2.0);
      base.rgb*=1.0-0.12*damp*(0.5+0.5*lapDry);
      vec3 f=field(world/0.5,uDrift*3.0*uMotion,uPhase*uMotion);
      vec2 offset=waterOffset(f)*uZoom*deep*cover*uMotion;
      vec2 warpedUV=clamp((screen+offset)/uSize,0.5/uSize,1.0-0.5/uSize);
      vec3 result=texture2D(uTerrain,warpedUV).rgb;
      if(uSurface>0.5) result=waterShade(result,f,deep);
      result=mix(result,vec3(0.62,0.80,0.84),uSurface*0.08*smoothstep(0.0,0.10,mask.g)*(1.0-smoothstep(0.10,0.40,mask.g)));
      vec3 surface=mix(original.rgb,mix(base.rgb,min(result,vec3(1.0)),cover),0.5);
      float shore=(1.0-smoothstep(0.35,0.95,mask.g))*smoothstep(0.0,0.25,mask.g);
      float patch=noise(world*0.025),lap=pow(max(0.0,sin(mask.g*10.0+uPhase*1.6+patch*3.0)),2.0);
      float foam=shore*lap*(0.09+uEnergy*0.105)*(0.5+0.5*patch)*cover*uFoam*(1.0-smoothstep(0.1,0.4,mask.b));
      surface=mix(surface,vec3(0.72,0.84,0.87),clamp(foam*0.6*cover,0.0,1.0));
      vec4 outColor=vec4(surface,1.0);
      float t=uPhase*uMotion;
      float ripple=sin(world.y*0.19+t*1.9+sin(world.x*0.07-t*0.6))*0.65+sin(world.y*0.37-t*1.3)*0.35;
      vec2 rUV=vUV+vec2(ripple*(0.65+uEnergy*0.65)*uZoom,0.0)/uSize;
      vec4 reflection=layer(uReflection,rUV)*0.5+layer(uReflection,rUV+vec2(uZoom/uSize.x,0.0))*0.25+layer(uReflection,rUV-vec2(uZoom/uSize.x,0.0))*0.25;
      reflection.rgb*=vec3(0.76,0.88,0.94);
      reflection*=0.25*rawCover*uReflections;
      outColor=over(reflection,outColor);
      vec4 sub=layer(uSub,vUV+offset*0.5/uSize);
      if(uSurface>0.5 && sub.a>0.0) {
        vec3 shaded=waterShade(sub.rgb/max(sub.a,0.0001),f,deep);
        sub.rgb=mix(sub.rgb,shaded*sub.a,0.5*cover);
      }
      outColor=over(sub,outColor);
      gl_FragColor=over(layer(uAbove,vUV),outColor);
    }`;
  const modelVS = `attribute vec3 aPosition; attribute vec2 aUV;
    uniform vec3 uPosition; uniform vec2 uCamera,uSize;
    uniform float uZoom,uSea,uLayer;
    varying vec2 vUV; varying float vHeight;
    void main() {
      vec3 p=aPosition+uPosition; vHeight=p.y-uSea; vUV=aUV;
      float height=uLayer>1.5 ? 2.0*uSea-p.y : p.y;
      vec2 screen=vec2(p.x-uCamera.x,p.z-height*0.5-uCamera.y)*uZoom;
      float depth=-(p.y+0.5*(p.z-704.0))/256.0;
      gl_Position=vec4(screen.x/uSize.x*2.0-1.0,1.0-screen.y/uSize.y*2.0,depth,1.0);
    }`;
  const modelFS = `precision highp float; uniform sampler2D uAtlas;
    uniform float uLayer; varying vec2 vUV; varying float vHeight;
    void main() {
      if(uLayer<0.5 && vHeight<0.0) discard;
      if(uLayer>0.5 && uLayer<1.5 && vHeight>=0.0) discard;
      if(uLayer>1.5 && vHeight<=0.0) discard;
      vec4 c=texture2D(uAtlas,vUV); if(c.a<0.5) discard;
      if(uLayer>1.5) c.a*=1.0-smoothstep(64.0,320.0,vHeight);
      gl_FragColor=vec4(c.rgb*c.a,c.a);
    }`;

  function shader(kind, source) {
    const s=gl.createShader(kind); gl.shaderSource(s,source); gl.compileShader(s);
    if (!gl.getShaderParameter(s,gl.COMPILE_STATUS)) throw new Error(gl.getShaderInfoLog(s)||'shader unavailable');
    return s;
  }
  function program(vs,fs) {
    const p=gl.createProgram(); gl.attachShader(p,shader(gl.VERTEX_SHADER,vs)); gl.attachShader(p,shader(gl.FRAGMENT_SHADER,fs)); gl.linkProgram(p);
    if (!gl.getProgramParameter(p,gl.LINK_STATUS)) throw new Error(gl.getProgramInfoLog(p)||'shader linking unavailable');
    const uniforms={}; for(let i=0;i<gl.getProgramParameter(p,gl.ACTIVE_UNIFORMS);i++){ const u=gl.getActiveUniform(p,i); uniforms[u.name]=gl.getUniformLocation(p,u.name); }
    return {p,uniforms};
  }
  function texture(img, filter=gl.LINEAR) {
    const t=gl.createTexture(); gl.bindTexture(gl.TEXTURE_2D,t);
    gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_MIN_FILTER,filter); gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_MAG_FILTER,filter);
    gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_WRAP_S,gl.CLAMP_TO_EDGE); gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_WRAP_T,gl.CLAMP_TO_EDGE);
    gl.pixelStorei(gl.UNPACK_PREMULTIPLY_ALPHA_WEBGL,false); gl.pixelStorei(gl.UNPACK_COLORSPACE_CONVERSION_WEBGL,gl.NONE);
    gl.texImage2D(gl.TEXTURE_2D,0,gl.RGBA,gl.RGBA,gl.UNSIGNED_BYTE,img); return t;
  }
  function target(w,h) {
    const t=gl.createTexture(); gl.bindTexture(gl.TEXTURE_2D,t);
    gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_MIN_FILTER,gl.LINEAR); gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_MAG_FILTER,gl.LINEAR);
    gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_WRAP_S,gl.CLAMP_TO_EDGE); gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_WRAP_T,gl.CLAMP_TO_EDGE);
    gl.texImage2D(gl.TEXTURE_2D,0,gl.RGBA,w,h,0,gl.RGBA,gl.UNSIGNED_BYTE,null);
    const fb=gl.createFramebuffer(); gl.bindFramebuffer(gl.FRAMEBUFFER,fb); gl.framebufferTexture2D(gl.FRAMEBUFFER,gl.COLOR_ATTACHMENT0,gl.TEXTURE_2D,t,0);
    const depth=gl.createRenderbuffer(); gl.bindRenderbuffer(gl.RENDERBUFFER,depth); gl.renderbufferStorage(gl.RENDERBUFFER,gl.DEPTH_COMPONENT16,w,h); gl.framebufferRenderbuffer(gl.FRAMEBUFFER,gl.DEPTH_ATTACHMENT,gl.RENDERBUFFER,depth);
    if(gl.checkFramebufferStatus(gl.FRAMEBUFFER)!==gl.FRAMEBUFFER_COMPLETE) throw new Error('framebuffer unavailable');
    return {t,fb,w,h};
  }
  function bindTexture(p,name,t,index) {
    gl.activeTexture(gl.TEXTURE0+index);gl.bindTexture(gl.TEXTURE_2D,t);gl.uniform1i(p.uniforms[name],index);
  }
  function attribute(p,name,size,stride,offset) {
    const a=gl.getAttribLocation(p.p,name);gl.enableVertexAttribArray(a);gl.vertexAttribPointer(a,size,gl.FLOAT,false,stride,offset);
  }
  function build() {
    gl=canvas.getContext('webgl',{alpha:false,antialias:false,depth:true,preserveDrawingBuffer:false});
    if(!gl || !gl.getShaderPrecisionFormat(gl.FRAGMENT_SHADER,gl.HIGH_FLOAT).precision) throw new Error('WebGL unavailable');
    programs={scene:program(quadVS,sceneFS),model:program(modelVS,modelFS)};
    quad=gl.createBuffer();gl.bindBuffer(gl.ARRAY_BUFFER,quad);gl.bufferData(gl.ARRAY_BUFFER,new Float32Array([-1,-1,1,-1,-1,1,-1,1,1,-1,1,1]),gl.STATIC_DRAW);
    textures={}; for(const name of ['terrain','mask','damp']) textures[name]=texture(resources[name]);
    models=resources.models.map(m=>{ const b=gl.createBuffer();gl.bindBuffer(gl.ARRAY_BUFFER,b);gl.bufferData(gl.ARRAY_BUFFER,new Float32Array(m.mesh.vertices),gl.STATIC_DRAW);return {...m,buffer:b,count:m.mesh.vertices.length/5,atlas:texture(m.atlas,gl.NEAREST),blue:texture(m.blue,gl.NEAREST)}; });
    // A two-sample raster in each direction, resolved to native output size.
    const scale=2; layers=[0,1,2].map(()=>target(scene.width*scale,scene.height*scale));
    if(gl.getError()!==gl.NO_ERROR) throw new Error('WebGL resource allocation failed');
    canvas.width=scene.width;canvas.height=scene.height;ready=true;lost=false;modelsDirty=true;
  }
  function render() {
    if(!ready || lost)return;
    if(modelsDirty) {
    const mp=programs.model;gl.useProgram(mp.p);gl.enable(gl.DEPTH_TEST);gl.depthFunc(gl.LESS);gl.disable(gl.CULL_FACE);gl.enable(gl.BLEND);gl.blendFunc(gl.ONE,gl.ONE_MINUS_SRC_ALPHA);
    gl.uniform2f(mp.uniforms.uCamera,scene.camera.X,scene.camera.Z);gl.uniform2f(mp.uniforms.uSize,scene.width,scene.height);gl.uniform1f(mp.uniforms.uZoom,2);gl.uniform1f(mp.uniforms.uSea,scene.sea);
    layers.forEach((l,i)=>{
      gl.bindFramebuffer(gl.FRAMEBUFFER,l.fb);gl.viewport(0,0,l.w,l.h);gl.clearColor(0,0,0,0);gl.clear(gl.COLOR_BUFFER_BIT|gl.DEPTH_BUFFER_BIT);gl.uniform1f(mp.uniforms.uLayer,i);
      for(const m of models){ gl.bindBuffer(gl.ARRAY_BUFFER,m.buffer);attribute(mp,'aPosition',3,20,0);attribute(mp,'aUV',2,20,12);gl.uniform3f(mp.uniforms.uPosition,m.unit.x,m.unit.y,m.unit.z);bindTexture(mp,'uAtlas',i===1?m.blue:m.atlas,0);gl.drawArrays(gl.TRIANGLES,0,m.count); }
    });
    modelsDirty=false;
    }
    const sp=programs.scene;gl.bindFramebuffer(gl.FRAMEBUFFER,null);gl.viewport(0,0,canvas.width,canvas.height);gl.disable(gl.DEPTH_TEST);gl.disable(gl.BLEND);gl.useProgram(sp.p);gl.bindBuffer(gl.ARRAY_BUFFER,quad);attribute(sp,'aPosition',2,8,0);
    const samplers=[['uTerrain',textures.terrain],['uMask',textures.mask],['uDamp',textures.damp],['uAbove',layers[0].t],['uSub',layers[1].t],['uReflection',layers[2].t]];
    samplers.forEach(([name,t],i)=>bindTexture(sp,name,t,i));
    gl.uniform2f(sp.uniforms.uSize,scene.width,scene.height);gl.uniform2f(sp.uniforms.uCamera,scene.camera.X,scene.camera.Z);gl.uniform2f(sp.uniforms.uMaskOrigin,scene.mask.x,scene.mask.z);gl.uniform2f(sp.uniforms.uMaskSize,scene.mask.width,scene.mask.height);gl.uniform1f(sp.uniforms.uMaskStep,scene.mask.step);gl.uniform1f(sp.uniforms.uZoom,2);
    const water=scene.phase.record,elapsed=phase-scene.tick/30;
    gl.uniform1f(sp.uniforms.uEnergy,water.Energy);
    gl.uniform2f(sp.uniforms.uDrift,water.TidalDriftX+scene.phase.rate[0]*elapsed,water.TidalDriftZ+scene.phase.rate[1]*elapsed);gl.uniform1f(sp.uniforms.uPhase,phase);
    for(const [name,value] of Object.entries(effects)) gl.uniform1f(sp.uniforms['u'+name[0].toUpperCase()+name.slice(1)],value);
    gl.drawArrays(gl.TRIANGLES,0,6);
  }
  function labels() {
    for(const input of checks)input.checked=!!effects[input.dataset.waterEffect];
    if(phase>Number(phaseControl.max))phaseControl.max=String(Math.ceil(phase/30)*30);
    q('[data-water-time]').value=phase.toFixed(1)+' s';phaseControl.value=phase.toFixed(2);
    playButton.textContent=playing?'Pause water':'Animate water';playButton.setAttribute('aria-pressed',String(playing));
    const enabled=checks.filter(c=>c.checked).length;
    q('[data-water-badge]').textContent=enabled===4?'All effects on':enabled===0?'All effects off':enabled+' effects on';
    for(const b of root.querySelectorAll('[data-water-preset]')) b.setAttribute('aria-pressed',String(b.dataset.waterPreset==='on'?enabled===4:enabled===0));
  }
  function frame(now) {
    pending=0;if(!ready||lost||!visible||document.hidden){previous=0;return;}
    if(playing && previous)phase+=Math.min((now-previous)/1000,0.05);
    previous=now;render();labels();if(playing)request();
  }
  function request() { if(!pending&&ready&&!lost&&visible&&!document.hidden)pending=requestAnimationFrame(frame); }
  function failure(message) {
    ready=false;playing=false;previous=0;
    if(pending)cancelAnimationFrame(pending);pending=0;
    canvas.hidden=true;q('[data-water-poster]').hidden=false;q('.water-controls').hidden=true;q('.water-live-badge').hidden=true;
    status.textContent=message+' The native engine recording is available below.';
  }
  const loadImage=src=>new Promise((resolve,reject)=>{ const img=new Image();img.onload=()=>resolve(img);img.onerror=reject;img.src=src; });
  async function start() {
    if(started)return;started=true;status.textContent='Loading the live water study…';
    try {
      const response=await fetch(root.dataset.sceneSrc);if(!response.ok)throw new Error('scene unavailable');scene=await response.json();
      function url(src) { return new URL(src,new URL('.',new URL(root.dataset.sceneSrc,location.href))).href; }
      const [terrain,mask,damp,...modelResources]=await Promise.all([loadImage(url(scene.terrain)),loadImage(url(scene.maskTexture)),loadImage(url(scene.dampTexture)),...scene.models.map(async unit=>{
        const response=await fetch(url(unit.mesh));if(!response.ok)throw new Error('model unavailable');const mesh=await response.json();const [atlas,blue]=await Promise.all([loadImage(url(unit.atlas)),loadImage(url(unit.blueAtlas))]);return {unit,mesh,atlas,blue};
      })]);
      resources={terrain,mask,damp,models:modelResources};phase=scene.tick/30;build();labels();
      q('[data-water-poster]').hidden=true;canvas.hidden=false;q('.water-controls').hidden=false;q('.water-live-badge').hidden=false;
      status.textContent='Live WebGL study · transport + submarine · effects change independently.';request();
    }catch(e){root.dataset.waterFailure=e.message;failure('The live WebGL study could not load.');}
  }
  for(const input of checks) input.addEventListener('change',()=>{effects[input.dataset.waterEffect]=input.checked?1:0;labels();request();});
  for(const b of root.querySelectorAll('[data-water-preset]'))b.addEventListener('click',()=>{for(const key of Object.keys(effects))effects[key]=b.dataset.waterPreset==='on'?1:0;labels();request();});
  playButton.addEventListener('click',()=>{playing=!playing;previous=0;labels();request();});
  phaseControl.addEventListener('input',()=>{playing=false;phase=Number(phaseControl.value);previous=0;labels();request();});
  q('[data-water-reset]').addEventListener('click',()=>{effects={...defaults};playing=!reducedMotion.matches;phaseControl.max="30";phase=scene.tick/30;previous=0;labels();request();});
  reducedMotion.addEventListener('change',e=>{if(e.matches){playing=false;previous=0;labels();request();}});
  document.addEventListener('visibilitychange',()=>{previous=0;request();});
  canvas.addEventListener('webglcontextlost',e=>{e.preventDefault();lost=true;failure('The live graphics context was interrupted.');});
  canvas.addEventListener('webglcontextrestored',()=>{try{build();labels();canvas.hidden=false;q('[data-water-poster]').hidden=true;q('.water-controls').hidden=false;q('.water-live-badge').hidden=false;status.textContent='Live WebGL study · graphics restored.';request();}catch(e){failure('The live graphics context could not recover.');}});
  if('IntersectionObserver' in window){const observer=new IntersectionObserver(entries=>{visible=entries[0].isIntersecting;previous=0;if(visible){start();request();}}, {rootMargin:'150px'});observer.observe(root);}else{visible=true;start();}
})();
