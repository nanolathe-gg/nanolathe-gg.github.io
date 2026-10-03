/* Local, low-entropy browser hints only. No tracking, storage or network calls. */
(function (root, factory) {
 const api = factory();
 if (typeof module === 'object' && module.exports) module.exports = api;
 else root.NanolathePlatform = api;
})(typeof globalThis !== 'undefined' ? globalThis : this, function () {
 const supported = ['windows', 'mac', 'linux'];
 function detectPlatform(hints = {}) {
  const ua = String(hints.userAgent || '').toLowerCase();
  const legacy = String(hints.platform || '').toLowerCase();
  const modern = String(hints.userAgentDataPlatform || '').toLowerCase();
  const touch = Number(hints.maxTouchPoints) || 0;
  // iPadOS can request desktop pages and identify itself as a Mac.
  if (/iphone|ipad|ipod|android|windows phone|tablet|kindle|silk|playbook|bb10|mobile/.test(ua) || /iphone|ipad|ipod|android/.test(legacy) || /android|ios|ipados/.test(modern) || ((/mac/.test(legacy) || /macintosh/.test(ua)) && touch > 1) || hints.mobile === true) {
   return { platform: null, kind: 'mobile' };
  }
  // ChromeOS UAs include Linux; exclude them before Linux detection.
  if (/cros|chrome ?os|chromium ?os/.test(`${ua} ${legacy} ${modern}`)) return { platform: null, kind: 'chromeos' };
  if (modern === 'windows') return { platform: 'windows', kind: 'desktop' };
  if (modern === 'macos' || modern === 'mac os' || modern === 'mac os x') return { platform: 'mac', kind: 'desktop' };
  if (modern === 'linux') return { platform: 'linux', kind: 'desktop' };
  if (/windows nt|win32|win64|windows/.test(`${ua} ${legacy}`)) return { platform: 'windows', kind: 'desktop' };
  if (/macintosh|mac os x|macintel|macppc/.test(`${ua} ${legacy}`)) return { platform: 'mac', kind: 'desktop' };
  if (/linux|x11.*(?:ubuntu|debian|fedora)/.test(`${ua} ${legacy}`)) return { platform: 'linux', kind: 'desktop' };
  return { platform: null, kind: 'unknown' };
 }
 function choosePlatform(detection, manualChoice = null) {
  if (supported.includes(manualChoice)) return { platform: manualChoice, source: 'manual' };
  if (supported.includes(detection?.platform)) return { platform: detection.platform, source: 'detected' };
  return { platform: null, source: 'unselected' };
 }
 return { detectPlatform, choosePlatform };
});
