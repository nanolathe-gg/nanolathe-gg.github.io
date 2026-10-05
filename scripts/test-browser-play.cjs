// Exercise the asynchronous engine/shell boundary without downloading game data.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const source = fs.readFileSync(require.resolve('../static/js/browser-play.js'), 'utf8');

function launcher({mobile = false} = {}) {
  const elements = new Map(), observers = [], microtasks = [], classes = new Set();
  const get = id => {
    if (!elements.has(id)) elements.set(id, {
      hidden: false, disabled: false, textContent: '', listeners: new Map(),
      addEventListener(type, callback) { this.listeners.set(type, callback); },
      click() { if (!this.disabled) { this.listeners.get('click')?.(); this.onclick?.(); } },
    });
    return elements.get(id);
  };
  get('demo').disabled = true;
  get('demo').textContent = 'Checking demo availability…';
  get('demo-title').textContent = 'Play the demo.';
  get('game-view').hidden = true;
  get('status').textContent = 'Opening browser host…';
  let clicks = 0;
  get('demo').onclick = () => {
    clicks++; get('demo').disabled = true; get('start').disabled = true;
  };
  vm.runInNewContext(source, {
    document: {getElementById: get, addEventListener() {}, body: {classList: {
      add(...names) { names.forEach(name => classes.add(name)); },
      remove(...names) { names.forEach(name => classes.delete(name)); },
      toggle(name, enabled) { if (enabled) classes.add(name); else classes.delete(name); },
    }}},
    navigator: {userAgent: mobile ? 'iPhone' : 'Chrome', platform: '', locks: {}},
    window: {isSecureContext: true, WebAssembly: {}, crypto: {subtle: {}}},
    MutationObserver: class { constructor(callback) { observers.push(callback); } observe() {} },
    queueMicrotask(callback) { microtasks.push(callback); },
  });
  const update = () => observers[0]();
  return {get, classes, update, clicks: () => clicks, flush: () => { microtasks.splice(0).forEach(fn => fn()); update(); }};
}

const page = launcher();
const loading = () => assert.ok(page.classes.has('demo-starting'));
loading();
page.get('demo').disabled = false;
page.get('demo').textContent = 'Try the demo';
page.update();
// Multiple observers can run before the automatic click's microtask.
page.update();
loading();
assert.equal(page.get('demo-title').textContent, 'Play the demo.');
page.flush();
assert.equal(page.clicks(), 1);
page.get('status').textContent = 'Preparing demo: 1.0 / 32.0 MiB';
page.update();
loading();
assert.equal(page.get('demo-loading-progress').textContent, page.get('status').textContent);
// The iframe opens before the engine download/compilation completes.
page.get('welcome').hidden = true;
page.get('game-view').hidden = false;
page.get('demo').disabled = false;
page.get('start').disabled = false;
page.update();
loading();
page.get('status').textContent = 'Running Official TA demo. Click the game to focus it.';
page.update();
assert.ok(!page.classes.has('demo-starting'));
// A real engine failure restores recovery controls without auto-relaunching.
page.get('game-view').hidden = true;
page.get('status').textContent = 'Startup failed: network connection lost';
page.update();
assert.equal(page.get('welcome').hidden, false);
assert.equal(page.get('demo-title').textContent, 'The demo couldn’t start.');
assert.equal(page.get('demo').textContent, 'Retry demo');
page.get('demo').click();
page.update();
loading();
assert.equal(page.get('demo-title').textContent, 'Play the demo.');
// A failed asset download finishes while the welcome screen is still present.
page.get('status').textContent = 'Failed to fetch';
page.get('demo').disabled = false;
page.get('start').disabled = false;
page.update();
assert.ok(!page.classes.has('demo-starting'));
assert.equal(page.get('demo-title').textContent, 'The demo couldn’t start.');
assert.equal(page.clicks(), 2);

const unavailable = launcher();
unavailable.get('demo').textContent = 'Demo unavailable';
unavailable.update();
assert.ok(!unavailable.classes.has('demo-starting'));
assert.equal(unavailable.get('demo-title').textContent, 'The demo is unavailable.');
const mobile = launcher({mobile: true});
assert.ok(!mobile.classes.has('demo-starting'));
assert.equal(mobile.get('demo-title').textContent, 'Play on a desktop computer.');
console.log('Demo startup race, slow download, engine readiness, failure, retry, availability and mobile checks passed.');
