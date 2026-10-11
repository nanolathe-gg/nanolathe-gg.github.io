+++
title = 'Playing online'
description = 'Create or join an online game, set up the lobby and computer players, chat, share and ally in skirmish or Survival, and watch replays.'
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

## Your name

On the online menu that **MULTI** opens, choose **Name** to set the name other
players see, up to 16 characters. Nanolathe remembers it. Your name appears in
the lobby, in chat, on the results and in the `+net` figures. Without one,
you appear as Player 1, Player 2 and so on.

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

Each player has a row showing their name, with **(You)** and **(Host)** marked.
Until you press **Ready**, you can click your own:

- **Side** to switch sides.
- **Team** symbol to choose no team or one of teams 1–5.
- **Color** to step to the next free color. Right-click steps back. Every
  player has a color of their own.

The host picks the gameplay rules, the game type (**Skirmish** or
**Survival**), the map with **Select Map**, and the Commander, Location,
Mapping and Line of Sight options. **Rules** steps through **Strict 3.1**,
**Community 3.9** and **Modern**; a new game starts with the rules you play
single-player, and a mod that needs newer rules leaves out the older ones.
Survival adds Wave Pace, Air Waves and
Naval Waves. Other players see these
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
add one computer as the third survivor. Under Strict 3.1, a room can have only
one computer player.

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

Teams chosen in the lobby last the whole battle. During the battle you can
also [share](#sharing) with any player and make or break
[alliances](#alliances) with players outside your team.

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
- Everyone plays by the gameplay rules the host chose.
- Cheat commands are turned off.
- Press Enter, type `+net` and press Enter again to show network figures,
  including each player’s ping and how far behind they are. The `+fps` display
  shows them too.

In an online battle, Tab opens the multiplayer strip at the bottom of the
screen, with **Options Menu**, **Allies**, **Share** and **Control**, when Tab
is set to open options, as it is by default. **Control** is the original
game's host controls, which online games don't offer, so it stays grayed
out. If you’ve set Tab to show the overview, Tab keeps doing that,
and F2 opens the strip instead.

### Chat

In the lobby, press Enter to open the message line under the chat, type,
and press Enter to send it to everyone in the room. Escape or a right click
drops the line.

In battle, press Enter to open the message line. A line goes to everyone
unless it starts with:

- `a,` to send it to your allies;
- `e,` to send it to your enemies;
- a player’s slot number followed by `,`, `:` or `;` to send it to that
  player only. Slots count from 0, so `0:` sends to Player 1 and `2:` to
  Player 3.

Defeated players who stay to watch the battle can’t chat.

### Sharing

Press H to open the **Share** screen, and pick any player. Use the sliders to
give them metal and energy, tick **Chosen Units** to give them the units you
have selected, and tick **Map Info** to give them your explored map, then
choose **OK**. Commanders,
aircraft in flight and units in or carrying a transport stay with you.

You can also share with your allies automatically, using typed commands:

- `+ShareMetal` and `+ShareEnergy` turn sharing of surplus metal or energy on
  or off.
- `+ShareMapping` does the same for your explored map, and `+ShareRadar` for
  your radar.
- `+ShareAll` switches all four.
- `+SetShareMetal n` and `+SetShareEnergy n` share metal or energy above `n`,
  for example `+SetShareMetal 500`.

### Alliances

In the **Allies** window, click the button beside another person to declare
or break an alliance with them; everyone sees a message when you do. The
button shows whether you, they or both of you have declared. Declaring an
alliance doesn’t make the other player your ally in return; they declare
theirs separately. Teams chosen in the lobby can’t be broken, so a teammate’s
button is grayed out.

**Allied Victory** lets allies win together: the battle is won when every
player still standing has it turned on and all of them have declared
alliances with each other. It’s grayed out for players on a lobby team of two
or more, who already have it.

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
player’s game records its own copy, without the chat. Campaign missions and
battles loaded from a saved game aren’t recorded.

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

- Only the host can add computer players, and under Strict 3.1 a room can
  have only one.
- There’s no list of open games. Friends join with a code.
- Teams chosen in the lobby can’t be broken.
- There’s no pausing, saving, reconnecting or spectating.
- Chat isn’t saved in replays.
- Browser players can’t use mods.
- Online play connects Nanolathe players only. It doesn’t work with the
  original game or other engines.

The engine’s [multiplayer design](https://github.com/nanolathe-gg/nanolathe/blob/main/docs/DESIGN_MULTIPLAYER.md)
describes what is built and what comes next.
