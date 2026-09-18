+++
title = 'Small fonts, packed tight'
seoTitle = 'FNT file format — illustrated Total Annihilation bitmap font reference'
description = 'Read a letter one bit at a time. A four-byte header and a table of offsets are enough to turn a compact font into GUI text.'
type = 'format'
url = '/docs/formats/fnt/'
format = 'FNT'
extension = '.fnt'
sourcePath = 'research/formats/fnt.md'
sourceRevision = '23332234bf03c8f0fd9a90d6b12b03323fbd3a13'
[[facts]]
label = 'Pixels'
value = '1 bit · MSB first'
[[facts]]
label = 'Metrics'
value = 'Fixed height · variable width'
[[facts]]
label = 'Character slots'
value = 'Byte codes up to 255'
[[facts]]
label = 'Offsets'
value = 'Absolute · little-endian u16'
+++

## A letter is a stream of bits {#overview}

FNT stores the bitmap fonts used for menu and in-game GUI text. Each glyph is a rectangle of **on/off pixels** with a shared height and its own width. Its on bits select pixels; the GUI supplies their color.

The pixels are packed continuously. A row can end halfway through a byte, and the next row starts at the very next bit. This small detail decides whether a letter decodes correctly.

{{< figure src="packing-comparison.svg" alt="Correct continuous decoding produces a five-column letter A; incorrectly starting each row at a new byte produces a broken letter." width="760" height="340" >}}
The same five bitmap bytes, interpreted two ways. Left: the format's continuous bitstream. Right: an intentionally incorrect row-aligned interpretation, with unavailable rows shown blank. Both come from the original [example.fnt](example.fnt).
{{< /figure >}}

{{< callout kind="note" title="Original glyphs, traced format" >}}
The A, B, and space in this guide were authored from scratch. The format layout comes from retail-file reverse engineering and rendered validation, supplemented by traced executable consumers [03 R-FONT-01 §§1, 4]. No public TA FNT layout note survives in the owning research's source set.
{{< /callout >}}

A GUI font gadget resolves a basename such as `filename=SMLFONT;` to `fonts/SMLFONT.FNT`. See the [GUI research]({{< research "research/formats/gui.md" >}}) for selection and the owning runtime evidence for text drawing.

## Find the glyph, then draw it {#addressing}

```text
4-byte header
  height, unused byte, signed y_offset, first_code
            ↓
u16 offset table: 256 − first_code entries
  table slot = character_code − first_code
            ↓
absolute glyph-record offset (0 means absent)
  advance byte + ceil(advance × height / 8) bitmap bytes
```

All offsets are measured from the **start of the file**. Codes below `first_code` are absent; a zero table entry also means absent. A blank space can instead be a present glyph with a positive advance and an all-zero bitmap.

## Byte layouts {#byte-layouts}

### Four-byte header

| Offset | Bytes | Type | Field | Meaning |
| --- | --- | --- | --- | --- |
| `0x00` | 1 | `u8` | `height` | Shared glyph height in pixel rows. |
| `0x01` | 1 | `u8` | Unused byte | Not read by traced font consumers; observed zero in surveyed retail fonts. |
| `0x02` | 1 | `i8` | `y_offset` | First glyph row is drawn at `penY − y_offset`. |
| `0x03` | 1 | `u8` | `first_code` | Starting code for the shortened offset table. |

{{< callout kind="warning" title="Four bytes, not two 16-bit words" >}}
Reading `u16 height` and `u16 unknown` happens to fit surveyed retail files because bytes 1 and 3 are zero. The executable actually reads height from byte 0, a **signed** vertical offset from byte 2, and the table's first character code from byte 3. Preserve all four separately.
{{< /callout >}}

### Character-offset table

| Offset | Bytes | Type | Field | Meaning |
| --- | --- | --- | --- | --- |
| `0x04` | `2 × (256 − first_code)` | `u16[]` | Glyph offsets | One entry for each code from `first_code` through 255. |
| `0x04 + 2 × (code − first_code)` | 2 | `u16` | Selected entry | Absolute glyph-record offset; zero means absent. |

With `first_code=0`, the table ends at `0x204`. With the example's `first_code=32`, it ends at `0x1C4`. Retail applies no upper bound to table indexing, so a font must provide all entries through code 255, even when most are zero.

A nonzero glyph start fits in **1–65,535**, because its offset is a `u16`. That does not impose a 64 KiB file-size limit: a bitmap may extend past its start, and trailing bytes may be unreferenced.

### Glyph record

Offsets below are relative to the selected glyph record.

| Offset | Bytes | Type | Field | Meaning |
| --- | --- | --- | --- | --- |
| `+0x00` | 1 | `u8` | `advance` | Both bitmap width and exact horizontal pen advance. |
| `+0x01` | `ceil(advance × height / 8)` | Packed bits | Bitmap | Top-to-bottom, left-to-right, MSB first; rows are not byte-aligned. |

There is no separate left bearing, kerning pair table, inter-character spacing field, or per-glyph height. Only the header's signed vertical offset shifts the glyph relative to the caller's pen position.

## Walk through an A {#worked-example}

The downloadable [468-byte font](example.fnt) has header `07 00 02 20`: height 7, unused byte 0, vertical offset +2, and first code 32. It contains a three-pixel space and two five-pixel letters. Every other table entry is zero.

| Character | Code | Table entry offset | Stored offset bytes | Glyph starts | Record size |
| --- | ---: | --- | --- | --- | ---: |
| Space | 32 | `0x004` | `C4 01` | `0x1C4` | 4 bytes |
| A | 65 | `0x046` | `C8 01` | `0x1C8` | 6 bytes |
| B | 66 | `0x048` | `CE 01` | `0x1CE` | 6 bytes |

At `0x1C8`, the record is **`05 74 63 F8 C6 20`**. `05` is the advance. The remaining five bytes contain 35 visible bits and five trailing pad bits.

{{< figure src="bit-packing.svg" alt="A five-by-seven letter A with cells grouped by packed byte; the bytes are 74, 63, F8, C6, and 20, with the last five bits padding." width="760" height="355" >}}
Follow border colors across row boundaries. Byte 0 holds all five bits of row 0 and the first three bits of row 1. There is no new byte at each row.
{{< /figure >}}

For pixel `(x, y)`, let `bit = y × advance + x`. Read byte `bitmap[bit / 8]` using integer division, then test `0x80 >> (bit % 8)`. For this A, pixel `(0, 1)` is bit 5: it lives in byte 0, mask `0x04`, and is on.

## Width, color, and pen position {#metrics}

{{< figure src="text-metrics.svg" alt="Original glyphs render A space B A with advances 5, 3, 5, and 5; the first bitmap row sits two pixels above the dashed penY line." width="760" height="350" >}}
The font determines the bit pattern and advance. The green color and dashed pen guide are presentation choices. With header offset +2, the first bitmap row sits two pixel rows above the supplied `penY`.
{{< /figure >}}

| Stored in FNT | Supplied by the caller / renderer |
| --- | --- |
| On/off glyph pixels | Color |
| Shared height and signed vertical offset | Pen position |
| Exact glyph advance | Any extra layout or line spacing |
| Byte-code mapping | String interpretation and code-page expectations |
| Blank space glyph, if authored | Caller-drawn text shadows |

Retail font data's high byte codes match Windows-1252, but the file is simply a mapping of byte values. The engine does not apply a code page. Do not turn that data convention into Unicode metadata that the file does not contain.

## Loading and confidence {#loading}

The retail loader reads the whole font and uses it in place without validation. Missing or empty startup fonts and side fonts are fatal with the path as the message; malformed offsets can send the rasterizer beyond the block [02 R-MALF-01 §9; 03 R-FONT-01 §1].

{{< callout kind="policy" title="Checked parsing is a host guarantee" >}}
Nanolathe preserves the four header bytes and each referenced packed bitmap. It rejects zero height, a short header/table, and out-of-file records or bitmap spans. These are host safety checks; they do not describe retail validation. Its tests cover cross-row packing, absent glyphs, nonzero `first_code`, and negative vertical offsets.
{{< /callout >}}

{{< callout kind="unknown" title="Byte 0x01 has no established authored meaning" >}}
Height accessors, the text-width walker, the string drawer, and the glyph rasterizer do not read it. It is zero in the surveyed copies. A period authoring tool could establish its producer-side meaning; the runtime contract is already known, and the parser retains the byte.
{{< /callout >}}

Corpus counts are observations, not format limits. An earlier layout survey covered 24 fonts; a later traced survey records 25 unique fonts. A per-archive census of `totala1.hpi`, `rev31.gp3`, `ccdata.ccx`, and `btdata.ccx` reports **39 copies, 25 distinct logical paths, and 21 distinct hashes**. Those populations are different and should not be collapsed into one “font count.”

The patched install's winning `fonts/SMLFONT.FNT` comes from `rev31.gp3`:
2,713 bytes with 223 glyphs, also shipped in `ccdata.ccx` and `btdata.ccx`.
The base `totala1.hpi` copy is 2,704 bytes with 222 glyphs; it lacks the patch's
`0xA0` glyph. Neither copy contains `0xFF`. Both have height 11 and vertical
offset 1. These are distinct archive copies of the same logical font path.

## Sources and example files {#sources}

Adapted from the [owning FNT research]({{< research >}}), pinned to the sidebar revision. The [complete source snapshot](research-source.txt) retains its bibliography, evidence IDs, and corpus observations. Runtime text rendering belongs to [03 §7.1, R-FONT-01], rather than to additional FNT fields.

The original [example.fnt](example.fnt) and its byte-derived SVG diagrams are reproducible with `scripts/fnt-example.py`; its `--check` mode checks the generated artifacts, including the hand-verified A bitstream.
