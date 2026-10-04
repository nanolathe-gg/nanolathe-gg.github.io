+++
title = 'Playing in your browser'
description = 'Start the original three-mission demo, use your own game folder, and understand browser controls and saved games.'
type = 'guide'
related = '/docs/keyboard-shortcuts'
+++

## Try the demo

Open [Play the demo](/play/) on a desktop computer with a keyboard and mouse.
The game starts directly: Nanolathe downloads the original demo files,
verifies them and starts the first ARM campaign mission. Continue through the
campaign using the normal in-game result screens.

Desktop Chromium is the verified browser family. Chrome and Edge are
recommended. Safari, Firefox, mobile and tablet play have not been verified.

The browser demo contains three original single-player missions. No purchased
game or installation is needed to try it. For full campaigns and skirmish,
provide your own installed game folder or [install the native beta](/get-started/).

## Focus and fullscreen

Click inside the game to focus it. Losing focus pauses play. Use **F2** to open
battle options, including from a paused game. The [keyboard reference](/docs/keyboard-shortcuts/)
describes Nanolathe's in-game controls; your browser may reserve some shortcuts.

Use the launcher's **Fullscreen** button for browser fullscreen. Its **Exit
fullscreen** button remains visible; your browser's Escape shortcut can also
leave fullscreen.

With the modern renderer, two-finger trackpad scrolling pans the camera and
pinch/spread zooms. A mouse wheel reported by the browser in pixels also pans;
line-based wheel events zoom. This camera support does not provide a complete
mobile control scheme.

**Restart game** starts a fresh engine session. Save your progress in-game before
restarting or switching to your own folder. Only one Nanolathe game can run at a time at the same
website address; close the other game tab before starting here.

## Your own game folder

Drag your installed TotalA folder onto the running game, or use **Choose game
folder** in the toolbar. Nanolathe closes the current demo session and starts
your local game. Keep the original archives
together; there is no need to unpack them. Your files remain local browser
handles and are not uploaded. There is no separate launcher page.

The imported full game uses its normal menus, campaigns and skirmish. Original
game data is separate from the engine's MIT license.

## Settings and saved games

Browser settings and saves stay in this browser at this website address. The
demo and imported full game have separate save lists. A different browser,
domain or local preview port uses different storage. Clearing site data can
remove browser saves and cached demo files.

Expand **Browser settings and saved games** to download stored files. Keep both
a saved game's `.SAV` file and its Nanolathe sidecar when backing it up. Desktop
save import into the browser is not implemented yet.

If the launcher reports a browser storage failure, the newest changes have not
been stored. Try saving again before restarting; a previous browser save may be
older. This warning also stays visible in fullscreen.

## Browser limits

The browser uses original texture detail; runtime terrain synthesis is disabled
in this host. The native beta provides synthesized terrain and the full native
experience. Browser memory and larger battles remain more constrained, and
long sessions and other browsers still need further acceptance testing.

If demo acquisition or startup fails, the launcher displays the error. Check
your connection and retry, use a supported desktop browser, or install Nanolathe.
No game files are uploaded when reporting an error.
