// A browser material study, not the complete game renderer. Finish and glint
// equations and their quantization match Nanolathe 801c8b2, model_finish.go and
// metal_glint.go. Projection, depth testing, and antialiasing are WebGL's.
(() => {
  const root = document.querySelector('[data-material-viewer]');
  if (!root) return;
  const q = selector => root.querySelector(selector);
  const canvas = q('[data-material-canvas]');
  const status = q('[data-material-status]');
  const rotation = q('[data-material-rotation]');
  const tilt = q('[data-material-tilt]');
  const spinButton = q('[data-material-spin]');
  const lightButton = q('[data-material-light-spin]');
  const lightControl = q('[data-material-light]');
  let gl, model, program, buffer, texture, locations;
  let yaw = 68, elevation = 35, finish = 1, spin = false, lightSpin = false, lightAngle = 0;
  let pending = 0, previousTime = 0, visible = false, started = false, ready = false, lost = false;
  let pointer = null;

  const vertexSource = `
    attribute vec3 aPosition;
    attribute vec3 aNormal;
    attribute vec2 aUV;
    attribute float aMaterial;
    uniform vec3 uCenter, uLight;
    uniform float uYaw, uTilt, uScale, uAspect, uShadow, uFloor;
    varying vec2 vUV;
    varying float vMaterial, vResponse, vGlint;
    vec3 turn(vec3 p) {
      float c=cos(uYaw), s=sin(uYaw);
      return vec3(c*p.x+s*p.z,p.y,-s*p.x+c*p.z);
    }
    void main() {
      vec3 p=turn(aPosition-uCenter);
      vec3 n=turn(aNormal);
      float response=clamp(dot(n,uLight),0.0,1.0);
      vResponse=floor(response*7.0+0.5)/7.0;
      float glint=response;
      glint*=glint; glint*=glint; glint*=glint; glint*=glint; glint*=glint;
      vGlint=floor(glint*255.0+0.5);
      vMaterial=aMaterial;
      vUV=aUV;
      if(uShadow>0.5) {
        float height=max(0.0,p.y-uFloor);
        p.x-=height*uLight.x/uLight.y;
        p.z-=height*uLight.z/uLight.y;
        p.y=uFloor;
      }
      float y=p.y*cos(uTilt)-p.z*sin(uTilt);
      float z=p.y*sin(uTilt)+p.z*cos(uTilt);
      gl_Position=vec4(p.x*uScale/uAspect,y*uScale,-z*uScale*0.25,1.0);
    }`;
  const fragmentSource = `
    precision highp float;
    uniform sampler2D uAtlas;
    uniform float uFinish, uShadow;
    varying vec2 vUV;
    varying float vMaterial, vResponse, vGlint;
    void main() {
      vec4 texel=texture2D(uAtlas,vUV);
      if(texel.a<0.5) discard;
      if(uShadow>0.5) { gl_FragColor=vec4(0.038,0.057,0.052,1.0); return; }
      vec3 albedo=texel.rgb, lit=albedo;
      if(uFinish>0.5) {
        // The game applies glints to every face through its neutral-color mask,
        // then applies the curated material finish. Preserve that order.
        if(vGlint>=0.5) {
          float peak=max(albedo.r,max(albedo.g,albedo.b));
          float low=min(albedo.r,min(albedo.g,albedo.b));
          float saturation=(peak-low)/max(peak,0.001);
          float mask=smoothstep(0.12,0.35,peak)*(1.0-smoothstep(0.2,0.65,saturation));
          vec3 tint=mix(vec3(1.0),albedo,0.65);
          lit=min(lit+tint*(vGlint/255.0)*0.48*mask,vec3(1.0));
        }
        float response=vResponse;
        if(vMaterial>0.5 && vMaterial<1.5) {
          float lobe=response*response; lobe*=lobe;
          float peak=max(albedo.r,max(albedo.g,albedo.b));
          lit=lit*0.87+albedo*vec3(0.05,0.10,0.16)*(1.0-response)
            +vec3(0.72,0.84,1.0)*lobe*0.42*smoothstep(0.06,0.3,peak);
        } else if(vMaterial>1.5) {
          lit=lit*0.93+albedo*0.035+vec3(0.075)*response*response;
        }
        lit=min(lit,vec3(1.0));
      }
      gl_FragColor=vec4(lit,1.0);
    }`;

  function compile(type, source) {
    const shader = gl.createShader(type);
    gl.shaderSource(shader, source); gl.compileShader(shader);
    if (!gl.getShaderParameter(shader, gl.COMPILE_STATUS)) {
      const message = gl.getShaderInfoLog(shader); gl.deleteShader(shader); throw new Error(message);
    }
    return shader;
  }
  function setup() {
    const vertex = compile(gl.VERTEX_SHADER, vertexSource), fragment = compile(gl.FRAGMENT_SHADER, fragmentSource);
    program = gl.createProgram(); gl.attachShader(program, vertex); gl.attachShader(program, fragment); gl.linkProgram(program);
    gl.deleteShader(vertex); gl.deleteShader(fragment);
    if (!gl.getProgramParameter(program, gl.LINK_STATUS)) throw new Error(gl.getProgramInfoLog(program));
    gl.useProgram(program);
    buffer = gl.createBuffer(); gl.bindBuffer(gl.ARRAY_BUFFER, buffer);
    gl.bufferData(gl.ARRAY_BUFFER, new Float32Array(model.vertices), gl.STATIC_DRAW);
    for (const [name,size,offset] of [['aPosition',3,0],['aNormal',3,3],['aUV',2,6],['aMaterial',1,8]]) {
      const location = gl.getAttribLocation(program,name);
      gl.enableVertexAttribArray(location); gl.vertexAttribPointer(location,size,gl.FLOAT,false,36,offset*4);
    }
    locations = Object.fromEntries(['Center','Light','Yaw','Tilt','Scale','Aspect','Finish','Shadow','Floor','Atlas'].map(n => [n,gl.getUniformLocation(program,`u${n}`)]));
    texture = gl.createTexture(); gl.bindTexture(gl.TEXTURE_2D,texture);
    gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_MIN_FILTER,gl.NEAREST);
    gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_MAG_FILTER,gl.NEAREST);
    gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_WRAP_S,gl.CLAMP_TO_EDGE);
    gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_WRAP_T,gl.CLAMP_TO_EDGE);
    gl.pixelStorei(gl.UNPACK_COLORSPACE_CONVERSION_WEBGL,gl.NONE);
    gl.texImage2D(gl.TEXTURE_2D,0,gl.RGBA,gl.RGBA,gl.UNSIGNED_BYTE,model.image);
    gl.uniform1i(locations.Atlas,0);
    gl.enable(gl.DEPTH_TEST); gl.depthFunc(gl.LEQUAL);
    gl.clearColor(0.08235,0.1098,0.10588,1);
  }
  function controls() {
    rotation.value = String(Math.round(yaw)); tilt.value = String(Math.round(elevation));
    q('[data-material-angle]').value = `${Math.round(yaw)}°`;
    q('[data-material-elevation]').value = `${Math.round(elevation)}°`;
    lightControl.value=String(Math.round(lightAngle));
    lightControl.setAttribute('aria-valuetext',`${Math.round(lightAngle)} degrees from the default light direction`);
    q('[data-material-light-angle]').value=`${Math.round(lightAngle)}°`;
    q('[data-material-light-state]').textContent=lightSpin ? 'Orbiting light' : (lightAngle===0 ? 'Fixed light' : 'Light adjusted');
    canvas.setAttribute('aria-label',`ARM mobile Annihilator, rotated ${Math.round(yaw)} degrees, tilt ${Math.round(elevation)} degrees, finish ${finish ? 'on' : 'off'}, light ${Math.round(lightAngle)} degrees from default.`);
  }
  function schedule() {
    if (!pending && ready && !lost && visible && !document.hidden) pending = requestAnimationFrame(draw);
  }
  function setMotion(mode) {
    // Move one thing at a time so the changing highlight is easy to read.
    spin = mode==='unit'; lightSpin = mode==='light'; previousTime = 0;
    spinButton.setAttribute('aria-pressed',String(spin));
    spinButton.textContent = spin ? 'Pause unit' : 'Rotate unit';
    lightButton.setAttribute('aria-pressed',String(lightSpin));
    lightButton.textContent=lightSpin ? 'Pause light' : 'Orbit light';
    schedule();
  }
  function draw(time) {
    pending = 0;
    if (!ready || lost || !visible || document.hidden) return;
    if (previousTime) {
      const advance=Math.min(time-previousTime,50)*0.0225;
      if(spin) yaw=(yaw+advance)%360;
      if(lightSpin) lightAngle=(lightAngle+advance)%360;
    }
    previousTime = time;
    const rect = canvas.getBoundingClientRect(), dpr = Math.min(window.devicePixelRatio||1,2);
    const width = Math.max(1,Math.round(rect.width*dpr)), height = Math.max(1,Math.round(rect.height*dpr));
    if (canvas.width!==width || canvas.height!==height) { canvas.width=width; canvas.height=height; }
    gl.viewport(0,0,width,height); gl.clear(gl.COLOR_BUFFER_BIT|gl.DEPTH_BUFFER_BIT);
    gl.uniform3fv(locations.Center,model.center);
    // Orbit the production half-vector around the vertical axis for this
    // browser study. Zero restores the exact fixed direction used in-game.
    const lightRadians=lightAngle*Math.PI/180, c=Math.cos(lightRadians), s=Math.sin(lightRadians);
    gl.uniform3f(locations.Light,-0.35*c-0.15*s,0.9246621,0.35*s-0.15*c);
    gl.uniform1f(locations.Yaw,yaw*Math.PI/180); gl.uniform1f(locations.Tilt,elevation*Math.PI/180);
    gl.uniform1f(locations.Scale,0.80/model.radius); gl.uniform1f(locations.Aspect,width/height);
    gl.uniform1f(locations.Floor,model.floor-model.center[1]); gl.uniform1f(locations.Finish,finish);
    gl.uniform1f(locations.Shadow,1); gl.disable(gl.CULL_FACE);
    gl.drawArrays(gl.TRIANGLES,0,model.vertices.length/9);
    gl.uniform1f(locations.Shadow,0); gl.enable(gl.CULL_FACE); gl.cullFace(gl.BACK);
    gl.drawArrays(gl.TRIANGLES,0,model.vertices.length/9);
    controls();
    if (spin || lightSpin) schedule();
  }
  function unavailable(message) {
    ready = false; setMotion(null);
    if (pending) cancelAnimationFrame(pending); pending=0;
    canvas.hidden=true; q('[data-material-poster]').hidden=false;
    q('.material-controls').hidden=true; q('.material-badge').hidden=true; q('.material-drag').hidden=true;
    q('#material-instructions').hidden=true;
    status.textContent=message;
  }
  async function start() {
    started = true;
    status.textContent='Loading interactive unit…';
    try {
      gl = canvas.getContext('webgl',{alpha:false,antialias:true,powerPreference:'low-power'});
      if (!gl) throw new Error('WebGL unavailable');
      const response = await fetch(root.dataset.modelSrc);
      if (!response.ok) throw new Error(`Model request failed: ${response.status}`);
      model = await response.json();
      model.image = new Image(); model.image.src=root.dataset.atlasSrc; await model.image.decode();
      if (gl.isContextLost()) throw new Error('Context lost while loading');
      setup(); activate();
    } catch (error) {
      console.warn('Material viewer unavailable:',error);
      unavailable('Live 3D is unavailable. Watch the in-game comparison below.');
    }
  }
  function activate() {
    lost=false; ready=true; canvas.hidden=false; q('[data-material-poster]').hidden=true;
    q('.material-controls').hidden=false; q('.material-badge').hidden=false; q('.material-drag').hidden=false;
    q('#material-instructions').hidden=false;
    status.textContent='Live browser material study · based on the modern renderer’s finish and glint formulas.';
    schedule();
  }
  function reset() { setMotion(null); yaw=68; elevation=35; lightAngle=0; schedule(); }
  function move(dx,dy) {
    yaw=(yaw+dx+360)%360; elevation=Math.max(15,Math.min(75,elevation+dy)); schedule();
  }
  root.querySelectorAll('[data-material-finish]').forEach(button => button.addEventListener('click',() => {
    setMotion(null);
    finish=Number(button.dataset.materialFinish);
    root.querySelectorAll('[data-material-finish]').forEach(b => b.setAttribute('aria-pressed',String(b===button)));
    q('[data-material-state]').textContent=finish ? 'Finish on' : 'Finish off'; schedule();
  }));
  rotation.addEventListener('input',() => {setMotion(null); yaw=Number(rotation.value);schedule();});
  tilt.addEventListener('input',() => {setMotion(null);elevation=Number(tilt.value);schedule();});
  spinButton.addEventListener('click',() => setMotion(spin ? null : 'unit'));
  lightButton.addEventListener('click',() => setMotion(lightSpin ? null : 'light'));
  lightControl.addEventListener('input',() => {setMotion(null);lightAngle=Number(lightControl.value);schedule();});
  q('[data-material-reset]').addEventListener('click',reset);
  canvas.addEventListener('pointerdown',event => {
    if (event.button!==0 || pointer!==null) return;
    pointer={id:event.pointerId,x:event.clientX,y:event.clientY};
    setMotion(null);canvas.focus({preventScroll:true});canvas.setPointerCapture(event.pointerId);
    canvas.classList.add('is-dragging');
  });
  canvas.addEventListener('pointermove',event => {
    if (!pointer || pointer.id!==event.pointerId) return;
    move((event.clientX-pointer.x)*0.5,(event.clientY-pointer.y)*0.3);
    pointer.x=event.clientX;pointer.y=event.clientY;
  });
  function release() { pointer=null;canvas.classList.remove('is-dragging'); }
  canvas.addEventListener('lostpointercapture',release);
  canvas.addEventListener('pointercancel',release);
  canvas.addEventListener('keydown',event => {
    const steps={ArrowLeft:[-5,0],ArrowRight:[5,0],ArrowUp:[0,5],ArrowDown:[0,-5]};
    if (steps[event.key]) {event.preventDefault();setMotion(null);move(...steps[event.key]);}
    else if (event.key.toLowerCase()==='r') {event.preventDefault();reset();}
  });
  canvas.addEventListener('webglcontextlost',event => {
    event.preventDefault();lost=true;unavailable('Live 3D paused while graphics recover. The in-game comparison is available below.');
  });
  canvas.addEventListener('webglcontextrestored',() => {
    if (!model?.image?.complete || !model.image.naturalWidth) return;
    try {setup();activate();} catch(error) {unavailable('Live 3D is unavailable. Watch the in-game comparison below.');}
  });
  new ResizeObserver(schedule).observe(canvas);
  document.addEventListener('visibilitychange',() => {if(document.hidden)setMotion(null);else schedule();});
  if ('IntersectionObserver' in window) {
    const loader = new IntersectionObserver(entries => {
      if (entries[0].isIntersecting && !started) { start(); loader.disconnect(); }
    }, {rootMargin:'160px'});
    loader.observe(root);
    new IntersectionObserver(entries => {
      visible=entries[0].isIntersecting;
      if (!visible) setMotion(null);
      else schedule();
    }).observe(q('.material-stage'));
  } else {visible=true;start();}
})();
