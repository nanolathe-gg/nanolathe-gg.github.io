+++
title = 'Keyboard shortcuts'
description = 'All implemented keyboard bindings, command keys, and modifiers, with modern GPU controls in their own section.'
type = 'guide'
related = '/docs/strategic-icons'
+++

## Before you start

This reference covers Nanolathe’s implemented window, battle, menu, and text-entry bindings. **Classic and modern GPU modes share the controls below**, except for the [modern-only controls](#modern-gpu-mode-only). Switch renderers with **F10** during a battle.

Key names refer to the physical keyboard: **Ctrl means Control, including on macOS**. Letter keys are written in uppercase for readability; press them without Shift unless it is listed. Punctuation aliases assume a US keyboard layout. Chat, dialogs, and the active command panel get first use of their keys, so the same letter can do different things in different contexts.

## Window and battle controls

| Key | Action |
| --- | --- |
| Alt + Enter | Toggle fullscreen. Also works in menus and chat. |
| Tab | Open or close battle options. When paused with no options window open, resume directly. |
| F2 | Open or close battle options; use this to reach options from a paused game. |
| Escape | Cancel the current command or build placement. If no command is armed, clear selection. In dialogs, use that dialog’s cancel action. |
| Pause | Pause or resume the battle. |
| + or = | Increase requested game speed, up to 20. |
| − or _ | Decrease requested game speed, down to 1. |
| F10 | Switch between classic and modern GPU rendering. |
| F9 | Cycle zoom. Classic: 1× → 1.5× → 2× → 1×. For modern’s different cycle, see [below](#modern-gpu-mode-only). |
| Ctrl + Shift + F11 | Pause and write a diagnostic bundle under `~/Nanolathe/diagnostics`. Works while paused and in battle dialogs; resume manually afterward. This is a development capture, not a saved game. |

The `+` and `−` characters can also come from the numeric keypad. Options and other modal dialogs own input while open; ordinary battle shortcuts do not bypass them.

## Selection and categories

| Key | Action |
| --- | --- |
| Ctrl + A | Add all your selectable units to the selection. |
| Ctrl + S | Replace the selection with your selectable units on screen. |
| Ctrl + Z | Select your units whose types match any currently selected type. |
| Ctrl + C | Select the authored commander category, then follow the commander. |
| Ctrl + D | Toggle self-destruct for the selected units. |
| Ctrl + B | Select the authored builder category. |
| Ctrl + F | Select the authored factory category. |
| Ctrl + M | Select the authored mine category. |
| Ctrl + P | Select the authored `CTRL_P` category, primarily combat aircraft in stock data. |
| Ctrl + R | Select the authored radar/sensor category. |
| Ctrl + V | Select the authored aircraft category. |
| Ctrl + W | Select the authored weapon-unit category. |
| Ctrl + E, G, H, I, J, K, L, N, O, Q, T, U, X, or Y | Select the corresponding `CTRL_<letter>` category. These categories are empty in the audited stock catalog, so these bindings normally clear selection. Mods may populate them. |
| Ctrl + Shift + category letter | Add that category to the selection instead of replacing it. An empty category leaves selection unchanged. Modern reserves Ctrl + Shift + G for metallic glint. |

Category shortcuts follow **the installed unit data**, not a guessed class or current activity: Ctrl+B is not an “idle builders” filter. The `CTRL_P` set even includes Thud in the audited catalog. Shift’s additive behavior applies to category keys, including Ctrl+C; it does not change the replacing behavior of Ctrl+S or Ctrl+Z.

## Squads and build pages

There are nine squad slots and nine numbered build-page keys. **By default, plain digits choose build pages and Alt+digits recall squads.** The “SwitchAlt” option swaps those two actions.

| Key | Default setting | SwitchAlt enabled |
| --- | --- | --- |
| Ctrl + 1–9 | Assign selected units to that squad. | Same. |
| 1–9 | Choose build page 1–9. | Recall squad 1–9. |
| Alt + 1–9 | Recall squad 1–9. | Choose build page 1–9. |
| Shift + Alt + 1–9 | Recall squad with additive/toggle selection behavior. | Choose build page; additive squad recall is unavailable from the keyboard in this setting. |
| . or Page Up or Shift + Right arrow | Next build page. | Same. |
| , or Page Down or Shift + Left arrow | Previous build page. | Same. |

Ctrl+Shift+1–9 still assigns the squad. There is no squad 0 binding. **Shift+1, Shift+3, and Shift+8 toggle unit labels**; Shift+digit alone is not additive squad recall. Other shifted digits have no residual battle action. Build-page keys only have an effect when a suitable build menu is available.

## Camera and information

| Key | Action |
| --- | --- |
| Hold arrow keys | Pan the camera. Chat suppresses this. Shift+Left/Right also changes build pages. |
| T | Follow the next selected unit. |
| Shift + T | Follow the previous selected unit. |
| N | Glide to the next unvisited owned unit without changing selection. Uppercase N (Shift+N) has no battle action. |
| Ctrl + F5, F6, F7, or F8 | Save the current camera position in one of four bookmarks. |
| F5, F6, F7, or F8 | Recall the matching bookmark. |
| F1 | Show information for the hovered unit or hovered build-button product. Requires no Ctrl or Shift. |
| F3 | Glide to the latest available message source. |
| Hold Space | Show the score panel. |
| F4 | Keep the score panel visible and enable kill/loss number flashes; press again to toggle off. |
| Backtick (&#96;) or ~ | Toggle labels/health bars for all units. |
| !, #, or * | The same label toggle (Shift+1, Shift+3, or Shift+8 on US keyboards). |
| F12 | Clear the message history. |

## Command-panel keys

Commands use the **active panel’s button shortcuts**. They are available only when the selected unit and displayed panel offer that button. Installed GUI files and localized captions can change the keys; use the button’s highlighted letter for the current binding. Letter matching is case-insensitive, and Alt+letter can activate an admitted button shortcut while a text field owns input.

| Usual key | Command |
| --- | --- |
| M | Move. |
| S | Stop. |
| A | Attack. |
| D | Special attack / D-gun, where available. |
| P | Patrol. |
| G | Guard / defend. Some authored build panels use Q (ARM) or D (CORE) instead. |
| R | Repair / help build. |
| E | Reclaim; resurrection-capable units use their supported reclaim/resurrect action. |
| C | Capture. |
| L | Load a transport. |
| U | Unload a transport. |
| X | Toggle activation (on/off), where available. |
| K | Toggle cloaking, where available. |
| F | Cycle fire stance. |
| V | Cycle movement stance. |
| B | Show the build panel. |
| O | Show the orders panel. |
| Other highlighted button keys | Queue stockpile ammunition or choose an authored build product. These are panel-specific, not additional global bindings. |

A targeting command arms the cursor; click a valid target or location to issue it. Stop and toggles act immediately. **Do not substitute Shift+N for stockpile production**: ammunition is queued through the relevant stockpile button.

## Shared mouse modifiers

These keyboard modifiers accompany mouse actions in both renderers.

| Modifier and gesture | Action |
| --- | --- |
| Shift + unit click / selection drag | Add to or toggle the selection rather than starting a fresh selection. |
| Shift + command click | Append the order to the queue; keep the command armed for more targets while Shift remains held. |
| Shift + build placement | Queue another building and keep placement armed while Shift remains held. |
| Shift + factory product button | Add five units; right-click subtracts five. |
| Alt + factory product button | Add twenty units; right-click subtracts twenty. Alt takes precedence over Shift. |
| Ctrl + right-drag | Drag-scroll in the classic left-click order interface (Interface Type 0), when no selection or command takes precedence. |

Without a modifier, factory product buttons add one unit, or subtract one on right-click. Middle-button dragging also pans the camera in both renderers.

## Modern GPU mode only

These controls require the **modern GPU renderer**. F9 also exists in classic mode, but uses the different zoom cycle listed above.

| Key or gesture | Action |
| --- | --- |
| F9 | Animate through 1× → 2× → 0.25× tactical view → 1×. Map size can limit the furthest zoom-out. |
| Mouse wheel over the battlefield | Zoom between tactical, native, and detail stops. Trackpad zoom gestures also work where supported by the host. |
| Left double-click with an idle mobile builder selected | Queue an extractor on a metal deposit, geothermal plant near a vent, or solar collector on ordinary ground, if available to that builder. Always appends, with or without Shift; Ctrl or Alt prevents this shortcut. |
| Hold Shift | Show tactical range guides for your selection, the hovered identified unit, and an armed build product. Selection and queue modifiers still apply. Guides hide during command drags, dialogs, and chat. |
| Ctrl + Shift + G | Toggle metallic glint on unit materials. |
| Alt + left-drag on the battlefield | Draw a movement formation from idle. Releasing Alt during the drag does not turn it into box selection. Ctrl prevents this shortcut. |
| Alt + left-click on the battlefield | Issue an explicit point Move, including over a unit or feature. |
| M, then left-drag | Draw a movement formation with Move armed. |
| Left-drag while placing a building | Lay out a straight row of buildings. |
| Alt + left-drag while placing a building | Lay out a rectangular building grid. |
| R, then left-drag | Queue repair for your visible damaged or unfinished units in a rectangular area. |
| E, then left-drag | Queue reclaim for visible reclaimable features in a rectangular area. |
| Shift when releasing a command drag | Append its commands instead of replacing existing orders. |
| Escape during a command drag | Cancel the preview. A right-click also cancels a left-button command drag. |

Armed commands take precedence over idle Alt movement: Alt chooses a grid during construction, and Repair/Reclaim retain their area actions. Range guides return after a drag if Shift remains held. With Interface Type 1, an idle right-drag on empty ground also draws a formation.

For the symbols visible at tactical zoom, see [Strategic icons]({{< relref "/docs/strategic-icons" >}}).

## Chat, menus, and text entry

| Key | Context and action |
| --- | --- |
| Enter | In battle, open chat. In chat, submit the text. In menus, activate the usable default action or focused control. |
| Escape | Cancel chat; a captured text editor clears its text and exits. In menus, activate the available cancel/back action. |
| Tab / Shift + Tab | Move focus forward/backward in menus that enable keyboard navigation. |
| Space | Activate a supported focused button, list, or surface in menus. |
| Left / Right arrow | Move menu focus, adjust a focused horizontal slider, or move the caret in a text field. |
| Up / Down arrow | Move through a focused list or navigate between controls. Lists stop at their ends. |
| Home / End | Move to the start/end of a text field. |
| Backspace / Delete | Delete before/at the caret. |
| Highlighted letter, or Alt + letter | Activate that dialog’s available button or linked label; bindings depend on the panel and localized caption. |
| Any printable character, Enter, Escape, Tab, or Backspace | Skip an intro movie. |
| Alt + F4 | Quit during an intro movie. Other OS window-close shortcuts depend on the platform. |
| Any key | Skip a supported post-battle tally/transition when its input gate opens. |

Chat accepts text and a bounded set of `+` commands; these are typed commands, not keyboard shortcuts. Text entry currently supports the ASCII character range. **Insert and Ctrl+V do not paste yet** in the portable host.

## Unavailable retail bindings

For completeness, these familiar or reserved keys do **not** currently provide their retail action in Nanolathe:

| Key | Status |
| --- | --- |
| H | Multiplayer sharing dialog is not implemented. |
| Shift + F2 | Retail Unit Builder Probe is not implemented. |
| Backslash, Ctrl + F10, F11 | Retail developer controls are not implemented. |
| Ctrl + F9 | Retail screenshot binding has no capture writer; use Ctrl+Shift+F11 for a diagnostic capture. |
| Ctrl + 0 | No squad assignment action. |
| Shift + N | No stockpile action or next-unit action. |

## Reference version

Verified against engine revision [5839714](https://github.com/nanolathe-gg/nanolathe/tree/58397146593069d7f8ca50f3f371bc816d04e796). The implemented bindings are defined by the [battle input dispatcher](https://github.com/nanolathe-gg/nanolathe/blob/58397146593069d7f8ca50f3f371bc816d04e796/cmd/nanolathe/battle_input.go), [interface and input design](https://github.com/nanolathe-gg/nanolathe/blob/58397146593069d7f8ca50f3f371bc816d04e796/docs/DESIGN_INTERFACE_HUD_INPUT.md), [GPU renderer design](https://github.com/nanolathe-gg/nanolathe/blob/58397146593069d7f8ca50f3f371bc816d04e796/docs/DESIGN_GPU_RENDERER.md), and [diagnostic capture guide](https://github.com/nanolathe-gg/nanolathe/blob/58397146593069d7f8ca50f3f371bc816d04e796/docs/DEBUG_CAPTURE.md). Catalog-dependent descriptions reflect the 278-definition reference installation; mods and localization may differ.
