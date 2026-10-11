+++
title = 'Playing online'
description = 'Create or join an online game, set up the lobby and computer players, play skirmish or Survival together, and watch replays.'
type = 'guide'
related = '/docs/native-installation'
+++

## What you need

You can play online in the native beta for Windows, Mac and Linux, or in your
browser with your own game folder. Native and browser players can play in the
same game.

Every player needs:

- Nanolathe: the native beta from [Get started](/get-started/), or
  [the browser version](/play/) with a game folder imported. When the native
  shortcut offers **Update & play**, take it, so everyone has a recent build.
- Their own installed Total Annihilation game files. Everyone’s game content
  has to match, so players with different expansions can’t play together.
- The host’s mod, if the game uses one.

You don’t need to change any router settings. Every player connects out to
Nanolathe’s server.

### In a browser

Online play in the browser has been tested in desktop Chrome and Edge. Phones
and tablets aren’t supported.

The three-mission demo has no skirmish maps, so **MULTI** stays grayed out
there. [Import your game folder](/docs/browser-demo/#your-own-game-folder)
first; **MULTI** then works as it does in the native beta.

Switching to another tab doesn’t pause the match or drop you from it: the game
keeps up in the background. Still, keep the tab open and don’t let your
computer sleep. A browser may freeze a tab left in the background for a long
time, especially with energy- or memory-saving settings on, and a frozen game
ends the match for everyone.

## Mods and maps

If the host uses a mod, every player needs the same copy of it. Install mods
with **Get more mods** on the **Content** card of the **Nanolathe** screen, or
from the same `.zip` file. If you have the room’s mod but aren’t using it,
Nanolathe switches to it when you join and keeps it selected. A mod installed
as a folder, or game files added with extra `--root` folders, can’t be used
online. The browser version can’t use mods yet, so browser players can only
join games without one.

If the host picks a map you don’t have, the lobby names it and **Ready** stays
grayed out. In the native beta, download community maps beforehand from
**More maps** on the map selection screen.

## Create a game

1. On the main menu, choose **MULTI**, then **Create Game**.
2. The lobby opens right away. Its six-character room code appears next to the
   title.
3. Send the code to your friends. **Copy** puts it on your clipboard.

The code is an invitation, so share it only with the people you want to play
with. A lobby stays open for up to 30 minutes before the game starts.

On Linux, copying and pasting use a clipboard program: `wl-clipboard` under
Wayland, or `xclip` or `xsel` under X11. Without one, **Copy** is hidden, and
you can read the code out instead.

## Join a game

1. On the main menu, choose **MULTI**, then **Join Game**.
2. Type or paste the code and press **Join** or Enter. Paste with Ctrl+V,
   Cmd+V on a Mac, or Shift+Insert. In a browser, its Paste menu works too.

Letter case, spaces and dashes don’t matter. Codes never contain 0, 1, O, I,
L, D or Q, and a typed S, Z, B or G counts as 5, 2, 8 or 6.

If you can’t join, the window stays open and explains why: no game has that
code, the game is full or has started, a mod is missing, or the server can’t
be reached.

## The lobby

Each player has a row: Player 1, Player 2 and so on, with **(You)** and
**(Host)** marked. Until you press **Ready**, you can click your own:

- **Side** to switch sides.
- **Team** symbol to choose no team or one of teams 1–5.
- **Color** to step to the next free color. Right-click steps back. Every
  player has a color of their own.

The host picks the game type (**Skirmish** or **Survival**), the map with
**Select Map**, and the Commander, Location, Mapping and Line of Sight options.
Survival adds Wave Pace, Air Waves and Naval Waves. Other players see these
settings but can’t change them. Hover over a control to see what it does.

The mod, mutators and unit restrictions come from the host’s setup when the
game is created, and they can’t change in the lobby. To use a different mod,
the host creates a new game.

### Computer players

The host can add computer players with **Add computer**, below the last row.
A new computer is played by the Modern AI at the host’s skirmish difficulty,
with no team. Click its name to switch it to the Classic AI, and click again
to remove it. The host sets each computer’s side, team and color the same way
as their own, and its difficulty (Easy, Medium or Hard) in the **Difficulty**
column. Other players see the computers but can’t change them.

A skirmish can have up to eight computers, as long as the map has a start
position for every player, computers included. In Survival, two players can
add one computer as the third survivor.

### Ready and Start

Press **Ready** when you’re set. Any change clears everyone’s Ready, so press
it again after a player joins or leaves, or after a setting, team, side or
color changes. When everyone is ready, the host presses **Start**.

Ready stays grayed out, with the reason shown, while:

- fewer than two players are in the lobby;
- a skirmish has more players, computers included, than the map has start
  positions;
- everyone in a skirmish, computers included, is on the same team;
- Survival has more than three players, computers included.

### The pre-game check

When you press Ready, Nanolathe quietly plays a short practice battle with the
room’s settings and compares the result with everyone else’s. If your games
would play the battle differently, the lobby tells you before the match
starts: “Your games simulate differently. Every player needs the same
version.” Update Nanolathe, and check that everyone has the same game files and
mod.

Players don’t need identical builds. Different builds can play together as
long as they compute the same battle. During the match, the games keep
comparing results, and the match stops if they ever disagree.

## Skirmish online

A skirmish takes 2 to 10 players, computers included, up to the number of
start positions on the map. At least two players are people. Players on the
same team are allies: they win together and share what their units see, radar
included. Players with no team fight for themselves.

Teams are fixed for the whole battle. Changing alliances and sharing
resources, units or maps aren’t available online yet.

## Survival online

In Survival, 2 or 3 players hold out together against waves of attackers.
The waves arrive from the map edges and grow stronger over time. The survivors
are one side, sharing sight, radar and income, so there are no teams to
choose.

There’s no victory. Hold out as long as you can; each player then sees the
Survival result. Survival battles can’t be saved.

## During the battle

- Online battles run at normal speed. There’s no pause, and the game-speed keys
  don’t apply.
- Online games use Nanolathe’s default Modern gameplay.
- Cheat commands are turned off.
- There’s no chat between players yet, so use a voice or messaging app.
- Press Enter, type `+net` and press Enter again to show network figures,
  including each player’s ping and how far behind they are. The `+fps` display
  shows them too.

## Leaving and disconnects

Before the game starts, **Leave** (or Escape) takes you out of the lobby and
frees your seat. If the host leaves, the lobby closes for everyone.

Once the game starts, a defeated player sees their result and may leave while
the others play on. Any other disconnect ends the match for everyone: a player
quitting early, losing their connection or their game stopping. Reconnecting
isn’t possible yet, and a server restart also ends games in progress.

Afterward, you return to the online menu. It says whether the game ended,
stopped or was left.

## If a match stops

When a match stops unexpectedly, the online menu shows the reason. To report
it, [open an issue](https://github.com/nanolathe-gg/nanolathe/issues) with the
message you saw, what was happening, and your operating system or browser.
Attach your [replay](#replays) of that battle, and ask the other players to
send theirs too: comparing every player’s replay shows where the games
differed. Online replays end in `_online.nlreplay`.

## Replays

Nanolathe records every skirmish and Survival battle you play, single-player
and online, as a replay on your own computer. In an online game, each
player’s game records its own copy. Campaign missions and battles loaded from
a saved game aren’t recorded.

To watch one, choose **REPLAYS** on the main menu, pick a battle and choose
**Watch**. The screen shows each battle’s map, game type, players and length.
A replay needs the game files, map and mod it was recorded with; if it used a
mod you have installed, Nanolathe switches to it first. If your version of
Nanolathe plays the battle differently, for example after an update, playback
stops where the two differ.

You can’t give orders while watching. The buttons at the top left pause,
change speed from ¼× to 8×, skip ahead a minute, switch between each
player’s view and the whole map, and exit. The
[keyboard reference](/docs/keyboard-shortcuts/#watching-a-replay) lists their
keys.

Nanolathe keeps your newest 100 replays. The
[native setup guide](/docs/native-installation/#settings-saves-and-logs) shows
where they’re stored. In a browser, they’re kept with your
[browser settings](/docs/browser-demo/#settings-and-saved-games).

## Server and status

Nanolathe uses the server at `relay.nanolathe.gg`. The small **Server** button
on the online menu changes it; leave it alone unless you’re testing your own
server. Everyone in a game must use the same server. To go back to the
default, clear the address and choose **OK**.

The [server status page](https://relay.nanolathe.gg/status) shows how many
players, lobbies and matches are active, along with recent matches and how
they ended. It never shows room codes or player addresses.

## Current limits

Online play is new, and some things aren’t available yet:

- Only the host can add computer players.
- Online games use Nanolathe’s default Modern gameplay. Strict 3.1 and
  Community 3.9 aren’t offered online yet.
- There’s no chat, no player names and no list of open games. Friends join
  with a code.
- Teams are fixed: you can’t change alliances or share resources, units or
  maps.
- There’s no pausing, saving, reconnecting or spectating.
- Browser players can’t use mods.
- Online play connects Nanolathe players only. It doesn’t work with the
  original game or other engines.

The engine’s [multiplayer design](https://github.com/nanolathe-gg/nanolathe/blob/main/docs/DESIGN_MULTIPLAYER.md)
describes what is built and what comes next.
