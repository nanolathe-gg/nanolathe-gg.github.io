+++
title = 'Strategic icons'
description = 'Read the modern GPU strategic view: unit shapes, weapon and support symbols, level notches, and worked examples.'
type = 'guide'
related = '/docs/keyboard-shortcuts'
+++

## Reading an icon

When you zoom out in **modern GPU mode**, strategic icons keep units readable after their models become too small to recognize. Press **F9** to cycle 1× → 2× → tactical view, or use the mouse wheel over the battlefield. Switch to modern with **F10** if needed.

Read each icon in three parts: **the outer shape tells you the unit family, the inner symbol tells you its primary role or weapon type, and the bottom notches tell you its presentation level**. Color identifies the owner; the surrounding selection/hover highlight is separate from those three parts.

The examples below show the engine’s actual generated icon art, enlarged **3×** beside its normal **24-pixel** size. Cyan is a sample owner color. The shape and symbol together describe a class of unit; multiple unit types can share an icon. Hover a visible unit for its exact identity.

## Base shapes

Family comes from the unit’s structure identity and explicit family metadata. A builder can be a kbot, vehicle, aircraft, hovercraft, ship, or submarine: **construction is a role, not an outer shape**. These shape samples use the same neutral support symbol in the center, except for the commander crown.

{{< icon-legend "families" >}}

A hexagon is a deliberate fallback when the available family information is missing or contradictory. It does not mean “elite” or a special tech tier. Commander and decoy appearances share the same crown and have no level notches.

## Weapon types

Combat icons display the **first active weapon slot**, in the unit’s authored order. Later weapons do not add badges or form a combined symbol. These samples all use a square frame to make the inner glyphs easy to compare; the same glyph can appear inside any unit-family shape.

{{< icon-legend "weapons" >}}

If that first weapon has several relevant flags, the glyph uses this priority: **interceptor → paralyzer → dropped → water → beam → ballistic → self-propelled → other projectile**.

These are weapon descriptions, not guarantees about target restrictions. A rocket glyph alone does not mean anti-air, and a large circle does not establish an artillery role. Dedicated AA, fighter, artillery, and heavy-unit distinctions are not inferred from weapon range, cost, damage, or unit names.

## Construction, economy, and other roles

A unit’s primary purpose can take precedence over its weapons. Constructors keep their wrench despite incidental resource production, factories keep their factory symbol despite storage capacity, and all factory types share the same inner silhouette. The square frames here are comparison samples; mobile units use their own family’s shape.

{{< icon-legend "roles" >}}

The constructor and assist roles intentionally share a wrench; mine and kamikaze roles also share one glyph. Radar, sonar, and jamming symbols require qualified sensor-role evidence rather than any nonzero sensor range. The fallback support symbol is used when the catalog cannot establish a more specific purpose.

## Level notches

The short light ticks across the **lower border** encode a presentation level. Their dark outlines keep them readable against bright terrain and dark team colors.

{{< icon-legend "levels" >}}

**Level is the minimum number of factories on a build path from a true commander.** Moving along the final build menu into a factory adds one; other steps add zero. The destination counts if it is itself a factory. In the standard kbot and vehicle lines, that gives basic constructors and their factories level 1, advanced constructors and their factories level 2, and units behind a third factory level 3. Other families can follow different build paths.

For example, Krogoth’s shortest route is:

**CORE Commander → Kbot Lab → Construction Kbot → Advanced Kbot Lab → Advanced Construction Kbot → Gantry → Krogoth.**

The Kbot Lab, Advanced Kbot Lab, and Gantry contribute three factory steps, so Krogoth shows three notches. The constructors between them do not add levels.

If a unit cannot be reached from a commander, a single positive numeric `LEVEL` category is used as a fallback. If neither source resolves a level, it stays unmarked. Commanders and decoy commanders always suppress level marks. **No marks can therefore mean level 0, level 1, an unresolved level, or a commander appearance.**

This is not a direct display of the original game’s authored level number or a measurement of unit power. The Moho Mine, for example, authors `LEVEL3` but has a two-factory build path, so it receives **two** notches. The final installed build menus determine the graph, including changes from mods and downloads.

## Representative examples

These combinations come from the 278-definition reference installation. They show how the same shape or glyph can carry different meanings when the other parts change.

{{< icon-legend "examples" >}}

## Visibility and zoom

Icons normally fade in below **0.625×** and reach full opacity at **0.5×**. Tactical view requests **0.25×**, but the map’s size and the window can limit how far out the camera goes. When that tactical request reaches its map limit, the full strategic view still appears even if the actual scale is higher. Icon size stays **24 framebuffer pixels** as you zoom.

Only identified, visible, completed units receive their descriptive icon. **A sensor-only contact remains a small team-colored square** and reveals no unit type, weapon, level, or remembered identity. Losing visibility does not preserve a unit’s previous descriptive icon. Visible units under construction have no strategic icon until completed; construction progress remains available through the existing selection UI.

Commander and decoy appearances share the crown so icon art does not reveal a disguise. Owner tint and selection/hover highlights are independent of role, weapon, and level. These symbols are a Nanolathe modern-renderer feature; classic mode retains its existing presentation.

## Reference version

This guide uses **icon vocabulary revision 6**, verified against engine revision [5839714](https://github.com/nanolathe-gg/nanolathe/tree/58397146593069d7f8ca50f3f371bc816d04e796). The samples use the engine’s [generated atlas geometry and preview sampler](https://github.com/nanolathe-gg/nanolathe/blob/58397146593069d7f8ca50f3f371bc816d04e796/internal/client/strategic_icon_art.go). Classification is defined by the [catalog rules](https://github.com/nanolathe-gg/nanolathe/blob/58397146593069d7f8ca50f3f371bc816d04e796/internal/client/strategic_icon_catalog.go) and [build-path levels](https://github.com/nanolathe-gg/nanolathe/blob/58397146593069d7f8ca50f3f371bc816d04e796/internal/client/strategic_icon_levels.go); the [renderer design](https://github.com/nanolathe-gg/nanolathe/blob/58397146593069d7f8ca50f3f371bc816d04e796/docs/DESIGN_GPU_RENDERER.md) records the presentation and visibility rules.
