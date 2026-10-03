const assert = require('node:assert/strict');
const {detectPlatform, choosePlatform} = require('../assets/js/platform.js');
const cases = [
 ['Windows UA', {userAgent:'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',platform:'Win32'}, 'windows', 'desktop'],
 ['Windows hints', {userAgentDataPlatform:'Windows'}, 'windows', 'desktop'],
 ['Windows touchscreen', {userAgentDataPlatform:'Windows',platform:'Win32',maxTouchPoints:10}, 'windows', 'desktop'],
 ['Mac Safari', {userAgent:'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)',platform:'MacIntel',maxTouchPoints:0}, 'mac', 'desktop'],
 ['Mac hints', {userAgentDataPlatform:'macOS'}, 'mac', 'desktop'],
 ['Linux UA', {userAgent:'Mozilla/5.0 (X11; Linux x86_64)',platform:'Linux x86_64'}, 'linux', 'desktop'],
 ['Linux hints', {userAgentDataPlatform:'Linux'}, 'linux', 'desktop'],
 ['iPhone', {userAgent:'Mozilla/5.0 (iPhone; CPU iPhone OS 18_0 like Mac OS X)',platform:'iPhone'}, null, 'mobile'],
 ['iPad traditional', {userAgent:'Mozilla/5.0 (iPad; CPU OS 18_0 like Mac OS X)',platform:'iPad'}, null, 'mobile'],
 ['iPad desktop UA', {userAgent:'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15)',platform:'MacIntel',maxTouchPoints:5}, null, 'mobile'],
 ['iPad desktop UA no platform', {userAgent:'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15)',maxTouchPoints:5}, null, 'mobile'],
 ['Android phone', {userAgent:'Mozilla/5.0 (Linux; Android 15; Pixel 9) Mobile',platform:'Linux armv8l'}, null, 'mobile'],
 ['Android tablet', {userAgent:'Mozilla/5.0 (Linux; Android 14; SM-X710)',platform:'Linux aarch64'}, null, 'mobile'],
 ['Mobile hint', {userAgentDataPlatform:'Linux',mobile:true}, null, 'mobile'],
 ['ChromeOS Linux platform', {userAgent:'Mozilla/5.0 (X11; CrOS x86_64 16093.0.0)',platform:'Linux x86_64'}, null, 'chromeos'],
 ['ChromeOS hint', {userAgentDataPlatform:'Chrome OS',platform:'Linux x86_64'}, null, 'chromeos'],
 ['Tablet with Linux UA', {userAgent:'Mozilla/5.0 (X11; Linux aarch64; Tablet)',platform:'Linux aarch64'}, null, 'mobile'],
 ['Kindle', {userAgent:'Mozilla/5.0 (Linux; Kindle)',platform:'Linux'}, null, 'mobile'],
 ['Silk tablet', {userAgent:'Mozilla/5.0 (X11; Linux) Silk/3.0',platform:'Linux'}, null, 'mobile'],
 ['Windows tablet UA', {userAgent:'Mozilla/5.0 (Windows NT 10.0; ARM; Tablet)',platform:'Win32'}, null, 'mobile'],
 ['Mobile privacy browser', {userAgent:'PrivacyBrowser/1.0 Mobile',platform:'Linux'}, null, 'mobile'],
 ['Unknown', {userAgent:'PrivacyBrowser/1.0'}, null, 'unknown'],
 ['No hints', {}, null, 'unknown']
];
for(const [name,hints,platform,kind] of cases) assert.deepEqual(detectPlatform(hints),{platform,kind},name);
assert.deepEqual(choosePlatform(detectPlatform({userAgentDataPlatform:'macOS'})),{platform:'mac',source:'detected'});
for(const platform of ['windows','mac','linux']) {
 assert.deepEqual(choosePlatform({platform:'mac',kind:'desktop'},platform),{platform,source:'manual'});
 assert.deepEqual(choosePlatform({platform:null,kind:'mobile'},platform),{platform,source:'manual'});
}
for(const kind of ['mobile','chromeos','unknown']) assert.deepEqual(choosePlatform({platform:null,kind}),{platform:null,source:'unselected'});
assert.deepEqual(choosePlatform({platform:null,kind:'unknown'},'android'),{platform:null,source:'unselected'});
console.log(`${cases.length} detection cases + 11 selection assertions passed.`);
