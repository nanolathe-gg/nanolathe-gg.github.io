+++
title = 'Pictures, runs & scanlines'
seoTitle = 'PCX file format — illustrated Total Annihilation image reference'
description = 'Unpack an indexed image and see why a perfectly ordinary PCX scanline can decode differently in Total Annihilation.'
type = 'format'
url = '/docs/formats/pcx/'
format = 'PCX'
extension = '.pcx'
sourcePath = 'research/formats/pcx.md'
sourceRevision = 'c1b934071e15fc3156d9aa92ba91db26368768ac'
[[facts]]
label = 'Stock profile'
value = 'Version 5 · 8-bit · one plane'
[[facts]]
label = 'Header'
value = '128 bytes'
[[facts]]
label = 'Encoding'
value = 'Literal bytes + RLE runs'
[[facts]]
label = 'Palette trailer'
value = '256 RGB entries · 768 bytes'
+++

## An old image format, a specific reader {#overview}

Total Annihilation uses ZSoft PCX for unit portraits, menu backgrounds, logos, mission victory images, and even a palette source. Stock assets use **8-bit, single-plane, RLE-encoded version 5 PCX**, with a 256-color RGB palette at the end.

That authored profile and the executable's reader are different contracts. The most visible distinction is scanline padding: standard PCX consumes the stored stride; retail consumes exactly the visible width.

{{< format-demo name="pcx-padding" id="scanline-comparison" title="One extra byte per row changes the picture" label="Decoder comparison" >}}
Both panels decode the original [padded.pcx](padded.pcx): width 15, stored stride 16. A coral padding byte ends every stored row. The standard decoder skips it; retail begins the next row with it, shearing the image. These diagrams are decoded from authored fixtures, not captured retail art.
{{< /format-demo >}}

| Logical location | Role | Observed convention |
| --- | --- | --- |
| `unitpics/<UNITNAME>.PCX` | F1 unit portrait | 96 × 96 pixels; basename matches the unit short name. |
| `bitmaps/` | Backgrounds, logos, glamour images | Background/glamour art commonly 640 × 480; logos vary. |
| `palettes/GUIPAL.PCX` | Palette source | Palette data carried in an image container. |

Lookup is case-insensitive. The dimensions above describe asset conventions, not fixed PCX dimensions.

## From header to trailer {#structure}

```text
0x0000        128-byte header
0x0080        RLE image stream
              …
file size−769 0x0C palette marker (standard profile)
file size−768 256 × { red, green, blue }
EOF
```

The palette channels are full 8-bit values. The image stream produces **indexes** into a color table, not RGB triples. Width and height come from inclusive extents: `xmax − xmin + 1` and `ymax − ymin + 1`.

{{< callout kind="established" title="An embedded palette need not become the display palette" >}}
Frontend backgrounds retain their indexed pixels and display through active `PALETTE.PAL`. The F1 portrait loader discards the decoded trailer and its painter copies indexes unchanged. GUI semantic-color mapping is handled separately. See [07 §5, Retail palette contract; R-HUD-03 §8] and the [PAL research]({{< research "research/formats/pal.md" >}}).
{{< /callout >}}

## Byte layouts {#byte-layouts}

### Image header

All offsets are file-relative; multibyte values are little-endian. The table records the researched fields and groups the remaining bytes without assigning unverified runtime meanings.

| Offset | Bytes | Type | Field | Stock profile / retail use |
| --- | --- | --- | --- | --- |
| `0x00` | 1 | `u8` | Manufacturer | Must be `0x0A`; retail validates it. |
| `0x01` | 1 | `u8` | Version | Must be `5`; retail validates it. |
| `0x02` | 1 | `u8` | Encoding | Stock `1` (RLE); not a retail validation gate. |
| `0x03` | 1 | `u8` | Bits per pixel per plane | Stock `8`; not a retail validation gate. |
| `0x04` | 8 | `u16 × 4` | `xmin, ymin, xmax, ymax` | Inclusive bounds used to derive dimensions. |
| `0x0C` | 4 | `u16 × 2` | DPI | Ignored by retail. |
| `0x10` | 48 | Bytes | 16-color EGA palette | Ignored by retail. |
| `0x40` | 1 | Byte | Remaining header byte | Not part of the traced checks. |
| `0x41` | 1 | `u8` | Planes | Stock `1`; not a retail validation gate. |
| `0x42` | 2 | `u16` | Bytes per scanline | Authored stride; **never read by the executable**. |
| `0x44` | 2 | `u16` | Palette information | Ignored by retail. |
| `0x46` | 58 | Bytes | Remaining header | Not used by the traced reader. |

The header must read completely. Only manufacturer and version are validation gates; encoding, depth, planes, stride, and palette marker are not checked [02 R-MALF-01 §9].

### Palette trailer

| Offset | Bytes | Type | Field | Meaning |
| --- | --- | --- | --- | --- |
| `size − 769` | 1 | `u8` | Marker | Standard value `0x0C`; retail does not check it. |
| `size − 768` | 768 | `u8 RGB[256]` | Palette | 256 RGB triplets, index order, channel range 0–255. |

Retail simply reads the **last 768 bytes** as RGB. A marker-free file is not rejected for lacking the marker. Whether those colors are installed is the consumer's decision.

## RLE, byte by byte {#rle}

A byte below `0xC0` is a literal pixel index. A byte with both high bits set introduces a run: its low six bits are the count, and the following byte is the repeated index. This makes the largest positive run **63 pixels**.

| Encoded bytes | Interpretation | Decoded indexes |
| --- | --- | --- |
| `03` | Literal index 3 | `03` |
| `C3 03` | Repeat index 3 three times | `03 03 03` |
| `C2 C5` | Repeat index 197 twice | `C5 C5` |
| `C1 C5` | Escape one high-valued literal | `C5` |
| `07` | Literal index 7 | `07` |

The authored six-pixel sequence `03 03 03 C5 C5 07` becomes **`C3 03 C2 C5 07`**. A value of `0xC5` cannot appear as a lone literal command: it would be interpreted as a run count. `0xC0` has a zero count and needs separate malformed-input handling.

Retail decodes one visible-width row at a time. A run that reaches beyond the right edge is **clamped to the remaining row**, with no overflow pixels carried to the next row. The standard scanline path instead targets `bytes_per_line` for the authored single-plane profile.

{{< callout kind="warning" title="Stride padding is not skipped" >}}
In the comparison above, every row stores 16 literal bytes but only 15 are visible. After the first 15 bytes, retail moves to the next display row while the stream still points at the previous row's padding. The header's stride field cannot correct this because the reader never consults it.
{{< /callout >}}

## A compact picture to inspect {#worked-example}

{{< figure src="example.svg" alt="An original blue-green calibration frame with an amber center, decoded from a 16-by-12 PCX fixture." width="512" height="384" >}}
The original [example.pcx](example.pcx) has a 16 × 12 visible image and stride 16, so both decoding approaches agree. Its amber center uses index 197 (`0xC5`), exercising the escaped/RLE high-index path. The SVG uses the file's embedded palette for this explanatory preview.
{{< /figure >}}

| Fixture field | Value | Bytes |
| --- | --- | --- |
| Manufacturer/version/encoding/depth | `0x0A, 5, 1, 8` | `0A 05 01 08` |
| Extents | `(0, 0) … (15, 11)` | `00 00 00 00 0F 00 0B 00` |
| DPI | 72 × 72 | `48 00 48 00` |
| Planes | 1 | `01` |
| Bytes per line | 16 | `10 00` |
| Trailer | Marker + 256 colors | `0C` followed by 768 bytes |

The separate [padded.pcx](padded.pcx) reduces visible width to 15 and retains stride 16. Its image is deliberately encoded as literal low-valued pixels, making each padding byte's movement easy to follow. These are small teaching fixtures; they do not follow the 96 × 96 unit-portrait convention.

## Failure behavior and host policy {#loading}

Retail returns 0 with no message if the header is short or the manufacturer/version check fails. It allocates dimensions derived from the extents as read. Truncation in the image stream is not detected: failed one-byte reads leave the previous byte in use. A stale `0xC0` makes no progress and can hang the loader. For a file shorter than 768 bytes, the negative palette seek fails and reading continues from the current position [02 §7; R-MALF-01 §9].

{{< callout kind="policy" title="Safe decoding preserves the retail row rule" >}}
Nanolathe retains the authored extents and stride, decodes visible-width rows with run clamping, and reads the final RGB bytes without requiring a marker. Minimum length checks, dimension/allocation bounds, zero-run rejection, and refusing image reads into the palette trailer are host safety policies. They are not guarantees supplied by retail.
{{< /callout >}}

The parser tests lock the visible-width rule, marker-free palette read, run clamping, and checked truncated-value failure. The F1 client's indexed PCX blit also follows the established active-display-palette behavior.

Retail's screenshot writer uses 63-byte RLE runs and literal bytes below `0xC0` [01 R-PLAT-02 §6]. Reader permissiveness does not imply that the writer authors all accepted variants.

## Sources and example files {#sources}

Adapted from the [owning PCX research]({{< research >}}) at the pinned sidebar revision. The [complete source snapshot](research-source.txt) includes the standard/TA bibliography and the publication omission of the retail portrait example. No retail picture is included in this page.

Both downloadable PCX files and all three byte-derived SVGs are original, reproducible assets from `scripts/pcx-example.py`. Its `--check` mode verifies the artifacts, confirms matching decodes for the unpadded fixture, and confirms the intentional standard/retail divergence for the padded fixture.
