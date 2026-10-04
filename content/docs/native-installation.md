+++
title = 'Native setup and saved games'
description = 'Requirements, game folders, updates, saved games and troubleshooting for the Windows, Mac and Linux beta.'
type = 'guide'
related = '/docs/keyboard-shortcuts'
+++

## Install the beta

Use [Get started](/get-started/#install) to choose your computer and copy its
install command. The installer downloads a private Go compiler, builds the
latest commit on the engine’s main branch, and creates a shortcut. You do not
need to install Go or Git separately. Keep the terminal open until it finishes.

The native beta supports single-player campaigns and skirmish. Multiplayer is
not available yet. To try Nanolathe without installing it or buying game data,
use the [three-mission browser demo](/play/).

## Computer requirements

| Platform | Supported computers |
| --- | --- |
| Windows | 64-bit Intel/AMD or ARM64; use PowerShell for installation. |
| Mac | Apple Silicon or Intel, running macOS 13 or newer. |
| Linux | x86-64 or ARM64, with a working graphical desktop, graphics drivers, and window-system and audio runtime libraries. |

The installer uses your user account and keeps its compiler and cache separate
from an existing Go installation. Linux may still need runtime packages from
your distribution; building the engine does not supply graphics drivers.

## Choose your game folder

Use an installed Total Annihilation folder containing the original HPI archives
and expansion data. Keep these files together; do not unpack the archives.
A store installer or CD image is not an installed game folder.

The installer looks in common Steam, GOG, Wine and CrossOver locations. If it
cannot find the game, it asks you to choose a folder and remembers your choice.
If that folder is later moved, the shortcut asks again.

On Mac or Linux, you can bring an installed Windows game folder from another
computer or a Wine/CrossOver installation. Nanolathe itself runs natively.
The development reference installation includes the base game, Core Contingency,
Battle Tactics and the 3.1 patch; other combinations are still being tested.

## Launch and update

Launch Nanolathe from its app or menu shortcut after installation. When a newer
commit on main is available, the shortcut offers **Update & play** or the option
to keep your installed version. Offline launches use the installed build.

Updates reuse the compiler and build cache, preserve saves and settings, and
keep the previous working build if an update fails. You can also close the game
and rerun the [install command](/get-started/#install-details).

## Settings, saves and logs

The default installation folders are:

| Platform | Folder |
| --- | --- |
| Windows | `%LOCALAPPDATA%\Nanolathe` |
| Mac | `~/Library/Application Support/Nanolathe` |
| Linux | `$XDG_DATA_HOME/nanolathe`, or `~/.local/share/nanolathe` if that variable is unset. |

Each contains `settings.json`, a `saves` folder and a `logs` folder. Native saves
are separate from browser saves and from your retail Total Annihilation folder.

To try an existing retail save, copy its `.SAV` file into Nanolathe’s `saves`
folder while the game is closed. Save compatibility is still a work in progress.
Back up Nanolathe saves with their accompanying `.nanolathe.json` files when
present—for example, keep `MySave.SAV` and `MySave.SAV.nanolathe.json` together.
The [browser guide](/docs/browser-demo/#settings-and-saved-games) explains browser
storage and downloads; importing desktop saves into the browser is not available.

## Troubleshooting

### App warnings

These are locally built, unsigned beta apps. Your computer may show an app
warning, and some security or managed-device policies block unsigned apps.
The installer does not change those settings. If the app is blocked, check the
message and your device’s app policy before trying to launch it again.

### Missing game content

Choose the installed game folder containing the original archives. Repair an
incomplete or corrupt retail installation before trying to load it in Nanolathe.

### Missing Linux libraries

Install the named graphics, window-system or audio runtime package through your
distribution’s package manager. Launch from a working graphical desktop.

### A download or build fails

Read the error and the log path shown in the terminal, check your connection,
and rerun the install command. A failed update keeps the previous build selected.

### An in-game bug

[Report an issue](https://github.com/nanolathe-gg/nanolathe/issues) with your
operating system, the installed revision from `current/source-revision` on Mac
or Linux (or `releases/<selected release>/source-revision` on Windows), and the
relevant log or error. Keep retail game archives out of the report.

## Build from source

For development, install Git and the Go version specified by the engine’s
[go.mod](https://github.com/nanolathe-gg/nanolathe/blob/main/go.mod), then run:

```sh
git clone https://github.com/nanolathe-gg/nanolathe.git
cd nanolathe
go build -o nanolathe ./cmd/nanolathe
./nanolathe
```

On Windows, build with `-o nanolathe.exe` and run `.\nanolathe.exe`.
Use `--root "/path/to/TotalAnnihilation"` to select game data and
`--save-dir "/path/to/saves"` for a separate save directory. Run `--help` for
other options. Desktop builds use Go without a separate C compiler; Linux still
needs its graphics, window-system and audio runtime libraries.

See the engine’s [contribution rules](https://github.com/nanolathe-gg/nanolathe/blob/main/AGENTS.md)
before changing code or adding research.
