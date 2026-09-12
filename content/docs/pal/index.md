+++
title = 'One palette, every pixel'
seoTitle = 'PAL file format — illustrated Total Annihilation palette reference'
description = 'Follow a color index from an image byte to the screen, then explore the lookup tables that blend, brighten, and shade it.'
type = 'format'
url = '/docs/formats/pal/'
format = 'PAL'
extension = '.pal · .alp · .lht · .shd'
sourcePath = 'research/formats/pal.md'
sourceRevision = 'c1b934071e15fc3156d9aa92ba91db26368768ac'
[[facts]]
label = 'Palette'
value = '256 colors · 1,024 bytes'
[[facts]]
label = 'Channels'
value = '8-bit RGB + reserved byte'
[[facts]]
label = 'Headers'
value = 'None in any of the four files'
[[facts]]
label = 'Lookup outputs'
value = 'Palette indexes, never RGB'
+++

## A pixel names a color {#overview}

Total Annihilation uses a shared **256-entry palette**. GAF images, TNT terrain, minimaps, font colors, and model face colors ultimately resolve through it. An image byte stores a slot number; the palette supplies its RGB color. Change the table and the same image bytes can produce a different picture.

{{< format-demo name="pal-comparison" id="palette-comparison" title="Same pixels. Different table." label="Before / after" >}}
Both images decode the same original [32 × 20 index buffer](indices.bin). Only the table changes: [day.pal](day.pal) or [night.pal](night.pal). Each palette is a complete 1,024-byte file. The beacon and both color schemes were authored for this guide; they are not retail assets or a demonstration of retail palette switching.
{{< /format-demo >}}

For the beacon light, a pixel byte of `06` selects entry 6, at file offset `6 × 4 = 24` (`0x18`). In the day palette those four bytes are `FA B9 48 00`, giving opaque RGB **(250, 185, 72)**. The pixel contains neither those channels nor an alpha value.

{{< callout kind="established" title="Transparency belongs to the consumer" >}}
The fourth PAL byte is **not alpha**. Ordinary raw GAF drawing skips its frame's color key; RLE skip runs also leave the destination alone. A literal RLE index 0 is opaque black in the reference palette. Terrain and model texture spans do not inherit GAF transparency tests. See the [GAF reference]({{< research "research/formats/gaf.md" >}}), [03 R-REN-03A §5].
{{< /callout >}}

## Four files, four table shapes {#table-shapes}

The logical filename and its consumer establish the role. **Size alone cannot distinguish LHT from SHD.** None has a magic value, version, row count, or header.

| File | Shape | Total bytes | Lookup | Output |
| --- | --- | ---: | --- | --- |
| `PALETTE.PAL` | 256 × 4-byte entries | 1,024 | `4 × index` | RGB + reserved byte |
| `PALETTE.ALP` | 256 rows × 256 columns | 65,536 | `a × 256 + b` | Blend result index |
| `PALETTE.LHT` | 32 rows × 256 columns | 8,192 | `level × 256 + index` | Lighting result index |
| `PALETTE.SHD` | 32 rows × 256 columns | 8,192 | `row × 256 + index` | Shading result index |

The renderer also holds a generated 256-entry **gray table** and a 256-entry **blue table**. They are not additional shipped `palettes/` files. The gray table supports palette color searches. Session initialization builds the blue table for submerged hull tint from `(r >> 1, g >> 1, (b >> 1) + 50)`, finding a nearest palette color through the gray table's search [03 §4.3.3; R-WATER-01 §2].

## Byte layouts {#byte-layouts}

### PAL entry

Offsets below are relative to entry `index × 4`.

| Offset | Bytes | Type | Field | Meaning |
| --- | --- | --- | --- | --- |
| `+0x00` | 1 | `u8` | Red | Full channel range 0–255. |
| `+0x01` | 1 | `u8` | Green | Full channel range 0–255. |
| `+0x02` | 1 | `u8` | Blue | Full channel range 0–255. |
| `+0x03` | 1 | `u8` | Reserved | Observed zero in inspected retail palettes; preserved as source data. |

These are full **8-bit channels**, not 6-bit VGA channel values. The reference palette's entry 255 is `(255, 255, 255, 0)`. During display installation the outgoing fourth byte is generated as zero; derived color searches use RGB only.

{{< figure src="palette-grid.svg" alt="A 16-column grid of all 256 original day-palette colors, read left to right and top to bottom." width="640" height="480" >}}
The complete authored day palette. Read indexes left to right: the first row is 0–15, the last 240–255. The first eight slots color the beacon; the remaining slots complete the file. This grid is not the retail palette.
{{< /figure >}}

### Lookup-table cells

Each cell is one unsigned byte, storing a **palette index**. Row-major storage means that each next row starts 256 bytes later.

| File | Offset | Bytes | Type | Meaning |
| --- | --- | --- | --- | --- |
| ALP | `a × 256 + b` | 1 | `u8` | Result for operands in the consumer's order. |
| LHT | `level × 256 + source` | 1 | `u8` | Remap source through level 0–31. |
| SHD | `row × 256 + source` | 1 | `u8` | Remap source through row 0–31. |

For example, `LHT[31][1]` is byte `31 × 256 + 1 = 7,937` (`0x1F01`). A value of `249` means **look up PAL slot 249**; it does not mean a channel intensity of 249.

## Blend, brighten, shade {#lookup-behavior}

### ALP: two indexes become one

`ALP[a × 256 + b]` approximates a blend in palette space. It is a precomputed lookup, not exact channel arithmetic. It need not be symmetric: swapping `a` and `b` is not generally safe.

The inspected reference table maps every `ALP[i][i]` to `i`; the recovery builder explicitly preserves this diagonal, even for duplicate RGB entries [03 §4.3.4]. Structure anti-alias downscaling depends on it: four background pixels must remain the same background index after three ALP lookups. Other consumers include the minimap supersample composite and translucency effects.

{{< callout kind="note" title="Why a building edge can turn red-purple" >}}
With `Anti_Alias` enabled, the `BMcode=0` image downscale blends silhouette-straddling blocks against background index 1, which is `(128, 0, 0)` in the reference palette. That lookup sequence can color the fringe. This is a renderer and reference-palette interaction, not a special edge-color field in PAL [03 R-REN-03A §§6–7].
{{< /callout >}}

### LHT: a brightening remap

Lighting performs one byte lookup after the logical-to-physical source mapping. The reference LHT's **mean** brightness increases with row; individual cells can still darken because the result is quantized to an available palette entry.

| LHT row | Mean luminance change | Entries mapping to themselves |
| ---: | ---: | ---: |
| 0 | +0.00 | 242 / 256 |
| 1 | +0.24 | 230 / 256 |
| 3 | +6.83 | 125 / 256 |
| 5 | +12.60 | 52 / 256 |
| 15 | +31.37 | 8 / 256 |
| 31 | +51.51 | 8 / 256 |

These are bounded measurements from `totala1.hpi`, using `0.299R + 0.587G + 0.114B`; they are not validation rules for authored replacements. As a counterexample to per-cell monotonicity, `LHT[3][161] = 66` lowers luminance by 10.764 in those tables.

The calculated explosion flash uses `LHT[(discByte − 0x4F) × 256 + destination]`: visible disc bytes `0x4F…0x6E` select rows 0–31; transparent pixels preserve the destination. The pool submits this secondary flash after projectile drawing and before its primary art, after the unit passes. Its shrinking frames and tick countdown supply the whole envelope; there is no additional age-based fade in this path [03 §4.3.1; R-FX-01 §4; 06 R-WFX-01 §2].

### SHD: darkness through brightness

SHD's reference ramp crosses identity around **row 15**, then continues into brightening. Row 15 preserves 232 of 256 indexes; row 0 is near-black, while row 31 has a mean luminance increase of about 54. It does not simply approach identity from darkness.

| Rendering case | SHD behavior |
| --- | --- |
| `BMcode=0` structure, `Shading` enabled | Interpolated rows remap textured and flat-colored faces. |
| Same structure, `dont-shade` piece | Select row 15 directly. |
| Unshaded structure renderer | Bypass SHD. |
| `BMcode=1` mobile renderer | No face SHD step; `dont-shade` is inert. |
| Model shadow | Uses ALP tint, not a special SHD row. |

`canmove` does not choose this renderer: factories can author `canmove=1`, `MaxVelocity=0`, and `BMcode=0`. The row comes from the face-averaged smooth normal: `trunc(dot(N, L) × 5.0) mod 32`, with shipped default `L = (−0.8, 1.0, 0.25)`. The renderer interpolates rows over faces. These contracts belong to [03 §4.3.2; R-REN-03A §5; R-RND-02A] and the [3DO research]({{< research "research/formats/3do.md" >}}).

LHT and the upper half of SHD overlap in mean brightening range, but they are distinct files. Do not synthesize one from the other.

## Palette roles and recovery {#loading}

`PALETTE.PAL` supplies the display colors. `GUIPAL.PAL` supplies **semantic GUI color fields** that retail maps into active `PALETTE.PAL` indexes before drawing primitives or glyphs. GAF, PCX, and TNT image bytes already contain active indexes and bypass that GUI map. An OTA does not select a terrain palette.

Model team textures select source-authored player frames from `LOGOS.GAF`, with SHD applied only by the shaded renderer. They do not use a global palette substitution. Beam colors and sidebar energy/metal colors reference palette slots through their TDF fields.

| Situation | Retail behavior | Nanolathe behavior |
| --- | --- | --- |
| Nonempty PAL exists | Read whole, without size/content validation. | Preserve source entries; resolved colors are opaque. |
| PAL missing or empty | Decode same-name PCX; pack its trailer into 1,024 PAL bytes. | Recover in memory. |
| Successful PCX recovery | Attempt host PAL write; delete host ALP/LHT/SHD files to regenerate. | Do not write or delete original assets. |
| Derived table missing or empty | Recovery behavior belongs to [03 §4.3.4]. | Build each missing/empty table individually; nonempty authored tables remain authoritative. |

The retail fallback is fatal, with the path as its message, if PCX decoding also fails [02 R-MALF-01 §9].

{{< callout kind="policy" title="768-byte RGB palettes are an import extension" >}}
Nanolathe accepts plain RGB-triplet palettes intentionally. Retail expects four-byte entries and does not validate the file size; a 768-byte PAL is misread, including reads beyond the loaded block. Three-byte palettes are not the retail PAL contract.
{{< /callout >}}

{{< callout kind="unknown" title="The reserved byte's authoring name is still unknown" >}}
Bounded installer and builder traces establish that it supplies neither alpha nor display flags to those consumers. Its original producer-side convention remains unverified; a period authoring tool or specification could settle it.
{{< /callout >}}

## Sources and example files {#sources}

This page adapts the [owning PAL research]({{< research >}}) at the pinned revision shown in the sidebar; its evidence IDs above retain their original scope. A [complete source snapshot](research-source.txt) includes the upstream bibliography and publication omissions. No omitted retail-derived image was recreated here.

The [day palette](day.pal), [night palette](night.pal), and [index buffer](indices.bin) are original reproducible fixtures generated by `scripts/pal-example.py`. The two beacon SVGs are resolved directly from those bytes.
