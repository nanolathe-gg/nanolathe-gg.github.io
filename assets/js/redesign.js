(() => {
const $ = (selector) => document.querySelector(selector);
const $$ = (selector) => [...document.querySelectorAll(selector)];
if ($('#platform-status')) {
const commands = { windows: '& ([scriptblock]::Create((irm https://nanolathe.gg/install.ps1)))', mac: 'curl -fsSL https://nanolathe.gg/install.sh | bash', linux: 'curl -fsSL https://nanolathe.gg/install.sh | bash' };
const requirements = { windows: 'Windows: 64-bit Intel/AMD or ARM64. The installer selects a native build.', mac: 'Mac: Apple Silicon or Intel, running macOS 13 or newer.', linux: 'Linux: x86-64 or ARM64 with a working graphical desktop, graphics drivers, and window-system and audio runtime libraries. Some runtime packages may be needed from your distribution.' };
const platformNames = { windows: 'Windows', mac: 'Mac', linux: 'Linux' };
const detection = NanolathePlatform.detectPlatform({
 userAgent: navigator.userAgent,
 platform: navigator.platform,
 userAgentDataPlatform: navigator.userAgentData?.platform,
 mobile: navigator.userAgentData?.mobile,
 maxTouchPoints: navigator.maxTouchPoints
});
let platform = null;
let manualPlatform = null;
function updatePlatformSelection() {
 const selection = NanolathePlatform.choosePlatform(detection, manualPlatform);
 platform = selection.platform;
 const hasPlatform = !!platform;
 $$('[name="platform"]').forEach(input => { input.checked = input.value === platform; });
 $('#command-instruction').hidden = !hasPlatform;
 $('.command-box').hidden = !hasPlatform;
 $('.script-note').hidden = !hasPlatform;
 $('#copy-command').disabled = !hasPlatform;
 $('#install-command').textContent = hasPlatform ? commands[platform] : '';
 $('#copy-command').textContent = 'Copy';
 $('#copy-status').textContent = '';
 const status = $('#platform-status');
 status.dataset.source = selection.source;
 if (selection.source === 'detected') status.textContent = `Looks like you’re using ${platformNames[platform]}. We’ve selected it for you; you can choose another computer above.`;
 else if (selection.source === 'manual') status.textContent = `${platformNames[platform]} selected. Run this command on that computer when you’re ready.`;
 else if (detection.kind === 'mobile') status.textContent = 'Installation needs a Windows, Mac or Linux computer. Choose that computer’s operating system above to preview its command.';
 else if (detection.kind === 'chromeos') status.textContent = 'ChromeOS isn’t listed as a supported platform. Choose a Windows, Mac or Linux computer above to preview its install command.';
 else status.textContent = 'We couldn’t confidently detect your operating system. Choose Windows, Mac or Linux above to see the matching command.';
 if (!hasPlatform) return;
 $('#command-instruction').textContent = platform === 'windows' ? 'Open PowerShell and paste this command:' : 'Open Terminal and paste this command:';
 $('#script-link').href = `https://nanolathe.gg/install.${platform === 'windows' ? 'ps1' : 'sh'}`;
 $('#platform-requirements').textContent = requirements[platform];
 $('#copy-command').setAttribute('aria-label', `Copy ${platformNames[platform]} installation command`);
}
$$('[name="platform"]').forEach(input => input.addEventListener('change', () => {
 manualPlatform = input.value;
 updatePlatformSelection();
}));
updatePlatformSelection();
$$('[name="ownership"]').forEach(input => input.addEventListener('change', () => { $('#data-ready').hidden = input.value !== 'yes'; $('#data-needed').hidden = input.value !== 'no'; }));
$('#copy-command').addEventListener('click', async () => {
 if (!platform) return;
 try { await navigator.clipboard.writeText(commands[platform]); $('#copy-command').textContent = 'Copied'; $('#copy-status').textContent = 'Copied. Run it only when you’re ready to install on your computer.'; }
 catch { const selection = window.getSelection(); const range = document.createRange(); range.selectNodeContents($('#install-command')); selection.removeAllRanges(); selection.addRange(range); $('#copy-status').textContent = 'Select and copy the highlighted command.'; }
});
}
$$('[data-redesign-comparison]').forEach(module => {
 const surface = module.querySelector('.comparison');
 const range = module.querySelector('input[type="range"]');
 function setSplit(value) {
  surface.style.setProperty('--split', `${value}%`);
  range.value = value;
  range.setAttribute('aria-valuetext', `${value} percent ${module.dataset.beforeLabel}, ${100-value} percent ${module.dataset.afterLabel}`);
  module.querySelectorAll('[data-split]').forEach(button => {
   const active = Number(button.dataset.split) === Number(value);
   button.classList.toggle('active',active); button.setAttribute('aria-pressed',String(active));
  });
 }
 setSplit(range.value);
 range.addEventListener('input', e => setSplit(e.target.value));
 module.querySelectorAll('[data-split]').forEach(button => button.addEventListener('click',()=>setSplit(button.dataset.split)));
});
let previousFocus;
function openDialog(dialog){previousFocus=document.activeElement;dialog.showModal();document.body.classList.add('modal-open');}
function closeDialog(dialog){dialog.close();}
$$('#video-dialog').forEach(dialog=>{dialog.querySelector('.dialog-close').addEventListener('click',()=>closeDialog(dialog));dialog.addEventListener('click',e=>{if(e.target===dialog){const r=dialog.getBoundingClientRect();if(e.clientX<r.left||e.clientX>r.right||e.clientY<r.top||e.clientY>r.bottom)closeDialog(dialog);}});dialog.addEventListener('close',()=>{document.body.classList.remove('modal-open');if(dialog.id==='video-dialog')$('#video-container').replaceChildren();previousFocus?.focus();});});
$$('[data-watch]').forEach(button=>button.addEventListener('click',event=>{if(event.metaKey||event.ctrlKey||event.shiftKey||event.altKey)return;if(typeof $('#video-dialog')?.showModal!=='function')return;event.preventDefault();const iframe=document.createElement('iframe');iframe.title='Nanolathe announcement reel, actual engine footage';iframe.src='https://www.youtube-nocookie.com/embed/bMWSCOY0dTc?autoplay=0&rel=0';iframe.allow='accelerometer; encrypted-media; gyroscope; picture-in-picture; fullscreen';iframe.allowFullscreen=true;$('#video-container').replaceChildren(iframe);openDialog($('#video-dialog'));}));

})();
