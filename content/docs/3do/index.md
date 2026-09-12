+++
title = 'Models & moving pieces'
seoTitle = '3DO file format — illustrated Total Annihilation model reference'
description = 'A model is more than a mesh. Follow its pieces, inspect its faces, and discover how a compact tree of geometry becomes a unit on screen.'
type = 'format'
url = '/docs/formats/3do/'
format = '3DO'
extension = '.3do'
sourcePath = 'research/formats/3do.md'
sourceRevision = '1ef7b9193452752fca3e8ea75da8c38dfa318268'
demoScript = 'js/formats/3do.js'
demoCSS = 'css/3do.css'
[[facts]]
label = 'Structure'
value = 'Tree of named pieces'
[[facts]]
label = 'Coordinates'
value = 'Signed 16.16 fixed point'
[[facts]]
label = 'Byte order'
value = 'Little-endian'
[[facts]]
label = 'Root record'
value = '52 bytes · offset 0'
+++

## A model you can take apart {#overview}

A `.3do` file stores a model as a hierarchy of named **pieces**. Each piece owns its vertices, faces, and a translation from its parent. Pieces can form a chassis, turret, barrel, articulated limb, or even an invisible point where an effect begins.

{{< format-demo name="3do-model" id="model-example" title="One model. Five connected pieces." label="Explore a 3DO" >}}
An original survey crawler, decoded from [example.3do](example.3do). Orbit the view, select a piece, or switch to wireframe. Rotate the turret to see its descendants follow; explode the hierarchy to separate the pieces. **Selection plate** overlays the face designated by the root’s selection index, rather than simulating retail selection rendering.
{{< /format-demo >}}

{{< callout kind="note" title="Original geometry, with the research kept in view" >}}
This model and its display palette were authored for the guide. They are not retail assets. The interactive geometry and static images come from the same decoded binary. Lighting, projection, depth ordering, the plate overlay, and exploded separation are explanatory display choices. The separate texture diagram illustrates the established corner assignment; it is not a retail rasterizer.
{{< /callout >}}

Models live under `objects3d/`. A unit’s `ObjectName` selects its model. Its corpse reference selects a feature definition, whose `object` names the wreck model. Names such as `<unitname>.3do` and `<unitname>_dead.3do` are conventions, not lookup rules. See the [FBI]({{< research "research/formats/fbi.md" >}}) and [TDF]({{< research "research/formats/tdf.md" >}}) references.

| Stored in the file | Supplied elsewhere |
| --- | --- |
| Named pieces and parent-relative translations | Script motion from COB; unit and projectile transforms from runtime state |
| Vertex positions and ordered face indexes | Runtime normals, lighting, culling and rasterization |
| Palette-index fields and optional texture names | Image data in texture GAF entries; palette and lookup tables |
| A per-piece selection-primitive index | Runtime normalization, drawing, picking and bounds contracts |

{{< callout kind="established" title="No animation tracks. No UV coordinates." >}}
3DO stores **no rotation, scale, animation, UV, normal, or light-value fields**. COB scripts animate pieces by name. The renderer assigns texture corners from the face’s vertex-index order. Keep those runtime operations separate from lossless file decoding.
{{< /callout >}}

## Follow the object tree {#hierarchy}

There is **no separate file header**. The root is an ordinary 52-byte object record at file offset 0. Each record points to its name, vertex array, primitive array, first child, and next sibling. All integers are little-endian; all stored offsets are absolute from the start of the file.

```text
Object @ 0x0000  (52 bytes)
  name pointer ───────► NUL-terminated piece name
  vertices pointer ──► Vertex[n]       (12 bytes each)
  primitives pointer ► Primitive[m]   (32 bytes each)
                         indexes ────► u16[k], local to this piece
                         texture ────► GAF entry name, or 0
  child pointer ─────► first child Object
  sibling pointer ───► next Object with the same parent
```

Children of one parent form a linked list through their **sibling** pointers. Zero terminates a child or sibling link. The decoder also accepts a root sibling chain; the layout does not prohibit one. Names, arrays and other objects can appear elsewhere in the file. Follow their pointers instead of assuming an exporter’s packing order.

{{< format-demo name="3do-hierarchy" id="hierarchy-example" title="Local translations add along the chain" label="Piece anatomy" >}}
The fixture’s `turret` and `mast` are siblings. The `barrel` belongs to the turret; `flare` belongs to the barrel. The drawing separates pieces for inspection. The arithmetic uses their original, unmodified bind-pose translations.
{{< /format-demo >}}

Without runtime rotations, summing parent translations places each piece’s origin in the file’s **bind-pose coordinate system**. The flare in this example is at `(0, 11, −20)`. That is not a world position: it has not yet gone through runtime import, piece animation, unit orientation, or world placement.

A piece with **one vertex and no primitives** is useful. It has a position but no surface to draw. Such pieces commonly locate muzzle flashes, smoke, nano spray, thrust, or factory build pads. Select `flare` in the inspector to see one.

## Byte layouts {#byte-layouts}

The following offsets are relative to each record. `i32` is signed; `u32` and `u16` are unsigned. Each pointer targets an absolute file offset. Vertex positions and piece translations use signed 16.16 fixed point.

### Object record · 52 bytes {#object-record}

| Offset | Bytes | Type | Field | Meaning |
| --- | --- | --- | --- | --- |
| `+0x00` | 4 | `i32` | `VersionSignature` | `1` in surveyed retail files. Retail never reads this word; Nanolathe’s decoder requires 1. |
| `+0x04` | 4 | `i32` | `NumberOfVertexes` | Vertices owned by this piece. May be zero. |
| `+0x08` | 4 | `i32` | `NumberOfPrimitives` | Primitives owned by this piece. May be zero. |
| `+0x0C` | 4 | `i32` | `OffsetToSelectionPrimitive` | Historical name: a **primitive index**, not a byte offset. `−1` means none; `0` selects primitive 0 when present. |
| `+0x10` | 4 | `i32` | `XFromParent` | Signed 16.16 translation from the parent’s origin. |
| `+0x14` | 4 | `i32` | `YFromParent` | Parent-relative translation; Y is up. |
| `+0x18` | 4 | `i32` | `ZFromParent` | Parent-relative translation; see [coordinate conventions](#coordinates). |
| `+0x1C` | 4 | `i32` | `OffsetToObjectName` | Pointer to a NUL-terminated piece name. |
| `+0x20` | 4 | `u32` | `OptionalAuxiliaryOffset` | Relocated when nonzero. Zero in the surveyed corpus; target meaning unknown. Historically `Always_0`. |
| `+0x24` | 4 | `i32` | `OffsetToVertexArray` | Pointer to `NumberOfVertexes × 12` bytes. |
| `+0x28` | 4 | `i32` | `OffsetToPrimitiveArray` | Pointer to `NumberOfPrimitives × 32` bytes. |
| `+0x2C` | 4 | `i32` | `OffsetToSiblingObject` | Next piece sharing this parent; zero ends the list. |
| `+0x30` | 4 | `i32` | `OffsetToChildObject` | First child; zero means no children. |

{{< callout kind="warning" title="A field named “offset” may actually be an index" >}}
`OffsetToSelectionPrimitive` selects a primitive in **this piece’s** primitive array. All-ones (`0xFFFFFFFF`, signed `−1`) is the sole no-selection sentinel. Treating `0` as absent loses legitimate primitive-zero selections. Historical support for a byte-offset form is an implementation compatibility choice, not recovered retail-format evidence.
{{< /callout >}}

### Vertex record · 12 bytes {#vertex-record}

| Offset | Bytes | Type | Field | Meaning |
| --- | --- | --- | --- | --- |
| `+0x00` | 4 | `i32` | `x` | Signed 16.16 local X position. |
| `+0x04` | 4 | `i32` | `y` | Signed 16.16 local Y position. |
| `+0x08` | 4 | `i32` | `z` | Signed 16.16 local Z position. |

Decode a coordinate as `signed_integer / 65536`. The sign belongs to the whole 32-bit word; do not interpret the fractional half independently. For example:

| Stored bytes, little-endian | Signed integer | Model units |
| --- | --- | --- |
| `00 00 01 00` | `65536` | `+1.0` |
| `00 80 06 00` | `425984` | `+6.5` |
| `00 80 FE FF` | `−98304` | `−1.5` |

Primitives share vertices **within their own piece** through index arrays. An index never names a vertex in another piece. A lossless decoder retains authored coordinates; the runtime import conversion is a later step.

### Primitive record · 32 bytes {#primitive-record}

| Offset | Bytes | Type | Field | Meaning |
| --- | --- | --- | --- | --- |
| `+0x00` | 4 | `u32` | `ColorIndex` | Authored palette-index field. Some textured retail faces contain values above 255; preserve the full word. |
| `+0x04` | 4 | `i32` | `NumberOfVertexIndexes` | Number of `u16` indexes in this face’s index array. Stored counts include lines, triangles, quads and larger polygons. |
| `+0x08` | 4 | `u32` | `OptionalAuxiliaryOffset` | Relocated when nonzero; meaning unknown. Historically `Always_0`. |
| `+0x0C` | 4 | `i32` | `OffsetToVertexIndexArray` | Pointer to this face’s local `u16` vertex indexes. |
| `+0x10` | 4 | `i32` | `OffsetToTextureName` | Pointer to a NUL-terminated GAF entry name, without an extension. Zero means no texture name. |
| `+0x14` | 4 | `i32` | `Unknown_1` | Often nonzero. Historically attributed to editors; do not validate as zero. |
| `+0x18` | 4 | `i32` | `Unknown_2` | Same caveat; preserve it. |
| `+0x1C` | 4 | `i32` | `IsColored` | Authored flag word. Bit 0 distinguishes flat from textured rendering on the established path; noncanonical full-word values occur. |

{{< callout kind="warning" title="Preserve the raw flags and unknown words" >}}
631 of 761 surveyed models have a primitive with nonzero editor fields. The same corpus contains 868 textured primitives whose `ColorIndex` exceeds 255. Requiring zeros, clamping every color field, or reducing `IsColored` to a Boolean destroys authored data or rejects valid reference assets.
{{< /callout >}}

### Strings and packing {#strings}

Object and texture names are NUL-terminated strings and can appear anywhere their pointers address. One observed exporter layout puts a texture-name pool immediately after the root, then indexes, vertices, primitives, and additional objects. That is an observation, not a format constraint. Records need not be aligned to four-byte boundaries; the authored fixture’s vertex array starts at `0x0109`.

## Faces and implied texture corners {#texturing}

A texture name refers to an entry in a GAF under `textures/`. The name identifies image data; the 3DO does not embed it. Read the [GAF guide]({{< format-link "gaf" >}}) for named entries and frames, or the [palette reference]({{< research "research/formats/pal.md" >}}) for indexed colors and lookup tables.

For a textured quad, the established default corner assignment is:

| Position in the face’s index array | Texture coordinate |
| --- | --- |
| First | `(0, 0)` |
| Second | `(width − 1, 0)` |
| Third | `(width − 1, height − 1)` |
| Fourth | `(0, height − 1)` |

{{< format-demo name="3do-texture" id="texture-example" title="The index order turns the texture" >}}
The geometric corners stay fixed while the index array cycles. Order `[1, 2, 3, 0]` gives geometric vertex 1 the texture’s A corner, rotating the image a quarter-turn. No UV fields were edited: none exist. This separate authored diagram uses the corner rule from [03 §2.4.1](#sources); the downloadable crawler uses flat-color primitives only.
{{< /format-demo >}}

### Runtime dispatch is a separate contract

The bounded rendering research establishes the following branch behavior. These are **runtime rules**, not additional records in the file:

| Condition | Established runtime behavior |
| --- | --- |
| `IsColored` bit 0 set | Flat polygon filler using an explicit vertex count. |
| Bit 0 clear and vertex count not 4 | No textured face is drawn on this path. |
| Bit 0 clear and vertex count 4 | Textured quad mapper; texture resolution may use loader-owned state. |
| Texture name cannot be resolved | Loader changes the primitive to flat color index 209. |
| Shaded span writer selected | Samples `PALETTE.SHD` using the computed/interpolated row and source index. |
| Unshaded span writer selected | Uses the source palette index directly. |

The loader owns resolve-at-draw-time and team flags. The owner’s color index can select a complete `LOGOS.GAF` frame; see [GAF team textures](/docs/formats/gaf/#team-colors-select-complete-frames). Do not infer runtime precedence from a texture name alone, or from the complete integer value of `IsColored`.

{{< callout kind="established" title="GAF sprite keying does not automatically apply to model textures" >}}
The four model span writers do not test the sampled texel against a transparent or color-key index. A texture is fully opaque within this model raster path. Final model-image transparency is carried by the composition image’s own background index. This is distinct from the ordinary raw keyed GAF blitter. [03 §2.4.1, primitive dispatch](#sources).
{{< /callout >}}

The model stores no normals. Normal construction, renderer selection, SHD rows, `dont-shade`, affine sampling and culling belong to the behavioral reference. The inspector above uses neutral face contrast for readability; it does not preview those retail shading operations. Stored polygon counts are also **not triangulation advice**: retail’s established path does not first fan-triangulate every face.

## The selection primitive {#selection-primitive}

The selection field designates a face in its own piece. Retail normalizes this field on **every piece**, not just the root. Its drawing and picking consumers live in the behavioral specification.

In the original crawler, root selection value **0** designates the first face: a flat X/Z quadrilateral at Y = 0. Toggle **Selection plate** in the inspector to overlay it. The overlay is a visualization of the reference; it does not claim that the engine renders that face with a translucent green material.

| Root selection value | Models in the 761-model survey | Meaning |
| --- | --- | --- |
| Positive index | 361 | The indexed primitive |
| `0` | 300 | Primitive 0 |
| `−1` | 100 | No designated selection primitive |

A separate census cross-referenced 278 winning unit definitions to 278 unique models, excluding wrecks, projectiles and map features. All had at least one flat root X/Z quad. Among them, 167 selected primitive 0, 109 selected a positive index, and two (`armmstor`, `cormine1`) stored `−1` despite still containing a flat primitive-zero plate.

{{< callout kind="note" title="Plate geometry does not define collision or fallback behavior" >}}
In that unit census, designated plates had four unique vertices, constant Y, and nonzero X/Z extent. Texture and color flags did not reliably identify them: some valid plates were textured. This geometry observation establishes neither collision bounds nor a fallback selection face when the index is `−1`.
{{< /callout >}}

## Coordinates: authored, imported, world {#coordinates}

A 3DO’s authored coordinates are Y-up. Retail then persistently **negates both X and Z**, for vertices and parent translations: a half-turn about Y. After composition, a model-space offset `(x, y, z)` maps to world offset `(x, y, −z)`. These are two separate operations.

{{< format-demo name="3do-coordinates" id="coordinate-example" title="Two conversions, two different jobs" label="Coordinate spaces" >}}
The source locator `(2, 1, −30)` becomes `(-2, 1, +30)` in imported model space, and `(-2, 1, −30)` as a world offset in this unrotated example. A source-Z-only reflection is not the recovered import operation. [03 §2.4 and R-RAST-01 §8](#sources).
{{< /format-demo >}}

**Supported inference:** a common authoring convention puts the nose toward **−Z**. A recorded locator census found negative local Z for `flare*` translations 135 times, versus positive Z 13 times. That supports an asset convention, not a mandatory forward axis. Historical documentation also described +Z-forward; preserve the distinction between convention and the established runtime transform.

The 16.16 interpretation matches the surveyed data, but the research identifies no vendor statement of that scale. BOS/COB linear script values use another scale: **1 BOS unit = 2.5 model units**. See the [COB reference]({{< research "research/formats/cob.md" >}}).

## A file you can inspect {#worked-example}

Download **[example.3do · 3,750 bytes](example.3do)** and its **[decoded model and offset manifest](model.json)**. The manifest includes all five records, the local geometry, raw primitive fields represented by the fixture, and the original display palette. Nothing in the download depends on retail data.

| Piece | Object offset | Parent | Vertices / primitives |
| --- | --- | --- | --- |
| `base` | `0x0000` | — | 36 / 25 |
| `turret` | `0x0034` | `base` | 16 / 12 |
| `barrel` | `0x0068` | `turret` | 16 / 12 |
| `flare` | `0x009C` | `barrel` | 1 / 0 |
| `mast` | `0x00D0` | `base` | 16 / 12 |

This fixture puts five object records first, followed by each piece’s names and arrays. The root’s first 52 bytes are the root object itself:

```text
01 00 00 00  24 00 00 00  19 00 00 00  00 00 00 00
00 00 00 00  00 00 00 00  00 00 00 00  04 01 00 00
00 00 00 00  09 01 00 00  B9 02 00 00  00 00 00 00
34 00 00 00
```

Read those words as version **1**, **36 vertices**, **25 primitives**, selection index **0**, zero translation, name at **0x0104**, zero auxiliary offset, vertices at **0x0109**, primitives at **0x02B9**, no root sibling, and first child at **0x0034**.

The first vertex at `0x0109` is:

```text
00 00 EF FF  00 00 00 00  00 00 EA FF
```

That is `(-1114112, 0, -1441792)` as signed integers, or **(−17, 0, −22)** model units. The selection face’s index array is `[0, 1, 2, 3]`, so this is one corner of its flat plate. The turret’s sibling pointer reaches the mast; its child pointer reaches the barrel. The barrel’s child reaches the one-vertex flare.

The website’s `scripts/3do-example.py` writes the fixture, independently follows its pointers and index arrays, and generates the images and manifest from the decoded result. `--check` validates the committed outputs, including fixed-point quantization. The page does not use the publication-omitted retail byte dumps.

## Loading, ordering and measured bounds {#loading}

Retail reads the file whole. A missing or zero-length model is **fatal**, with the path shown, whether a unit, weapon, or feature names it. The loader relocates names and auxiliary offsets when nonzero, array offsets unconditionally, and child and sibling links recursively. It also relocates the primitive offsets. These operations are unbounded, and the relocator has no visited set.

Primitive compilation is runtime behavior. The loader normalizes selection and creates an ordered view using its established ordering and arithmetic. A lossless parser should retain **authored primitive order and the original selection field**; a runtime compiler can create a separate ordered representation. Do not bake runtime sorting into the stored-format interpretation.

### The model-top walk is not an ordinary bounding box {#model-top}

**Established:** the definition’s upper Y bound is measured by a recursive sibling-chain walk. Each invocation starts `top = 0`. It considers every `vertex.y + piece.translation.y`. For children, it recursively computes a fresh child maximum, adds the parent piece’s own Y translation, and compares again. Additions wrap to signed 32 bits; comparisons are signed.

Zero is a floor at **each recursive level**. A small constructed example shows why that matters:

| Step | Example with a root translated to Y = +10 |
| --- | --- |
| Geometry | Root has no vertices. Its child has zero translation and one vertex at local Y = −5. |
| Highest accumulated vertex | `+10 + (−5) = +5` |
| Child walk | `max(0, −5) = 0` |
| Root walk | `max(0, +10 + 0) = +10` |

The measured top is **10**, although the only vertex reaches **5**. The walk reads no script orientation and has no minimum-vertex-count gate. This example illustrates the specified arithmetic; it is separate from the downloadable model.

{{< callout kind="established" title="There is no geometry-derived min-Y counterpart" >}}
The definition’s minimum-Y bound is zeroed by the loader and is not filled by an inverted geometry walk. Horizontal bounds come from the authored footprint, not the model. Even the behavioral test that sounds like it needs a model bottom—the band-3 “fully submerged” `setSFXoccupy` test—reads the maximum. See [02 R-CAT-01 §7, 07 R-REV-01 §7, and 04 R-MOV-01 §8b](#sources).
{{< /callout >}}

## Host policy and remaining unknowns {#unknowns-and-caveats}

### Checked decoding and encoding

| Area | Nanolathe’s policy or limitation |
| --- | --- |
| Version | `LoadThreeDO` requires version 1 even though retail ignores it. |
| Graph | Rejects cycles and shared nodes; walks sibling lists iteratively and bounds child depth. |
| Geometry | Applies aggregate object, geometry and polygon-index budgets. |
| Preservation | Keeps original bytes, authored primitive order and raw fields. |
| Auxiliary offsets | Stores both raw words under the legacy `AlwaysZero` name without resolving targets. |
| Encoding | Copies auxiliary words while rebuilding other offsets; cannot safely relocate nonzero auxiliary targets. |
| Textured face counts | Encoder restricts textured output to quads; decoder does not impose that restriction. |

Retail has no corresponding aggregate budgets and does not check selection or vertex indexes before the ordering pass. A zero-index face reaching comparison in that pass can cause signed division by zero. Checked decoders may reject those malformed inputs instead of reproducing unsafe access. These are implementation acceptance boundaries, not file-format maxima.

{{< callout kind="unknown" title="Nonzero auxiliary references remain unresolved" >}}
Relocation of both auxiliary fields is established; their target data’s meaning is not. A per-archive census found both words zero across 761 model copies, and the inspected 3DOBuilder writer also emits zeros. That does not establish that a nonzero target is inert in every runtime path. Nanolathe’s encoder preserves the word but does not relocate the referenced content.
{{< /callout >}}

### Winding, flags and stock distributions

The recorded signed-volume census of 608 base models found 2,029 pieces with outward right-handed winding and 90 with inward winding. Signed volume establishes orientation for closed pieces; it does not by itself label an open piece defective. Runtime culling must come from the behavioral contract.

| Survey population | Observation | What it does not establish |
| --- | --- | --- |
| 608 base models, 50,443 primitives | All 43,845 texture-named faces have four indexes; all 6,598 unnamed faces have `IsColored` bit 0 set. Bit 1 is never authored. | Universal validation rules or the meaning of every noncanonical flag word |
| 761 models including expansions | About 94% of primitives have four indexes, 4% have three; 315 have two, none have one, and about 950 have 5–16. | A triangulation requirement |
| Same 761-model corpus | Maximum hierarchy depth 10; 391 models have only one piece. | Format or decoder maxima |
| Same 761-model corpus | Auxiliary words zero; 868 textured faces carry out-of-range color fields. | Nonzero auxiliary targets being universally unused |

These censuses describe their specified reference populations. They are evidence about shipped assets, not constraints on all authored files.

### Piece names link the model to its script

Common names include `base`, `turret`, `barrel1`, `flare1`, `pelvis`, `torso`, `lfoot`, `rfoot`, `nano1`, `pad`, and `door1`. They connect authored model pieces with script queries, motion, and effects. Ship `wake*` and aircraft `thrust` locators often have a single vertex and no primitives; wrecks conventionally use names such as `ground`, `wreck`, or `gp`.

The format does not enforce those names. `SMOKEPIECE` is an authored helper convention. The engine’s `SweetSpot` query seeds piece index zero, which need not be named `base`. A parser should preserve names rather than infer fixed behavior from them.

## Sources and evidence {#sources}

This guide adapts the [3DO research]({{< research >}}) at commit **1ef7b91**, with a [complete plain-text snapshot](research-source.txt). It retains the source’s distinction between established byte layouts, bounded asset observations, supported inferences, unknowns, and Nanolathe policy. The texture-corner and span-writer explanations also use the owning behavioral reference at that same revision.

| Owning reference | Evidence used here |
| --- | --- |
| [02 · Content, VFS, formats and data loading]({{< research "research/retail-executable-spec/02-content-vfs-formats-and-data-loading.md" >}}) | “Model archive (3DO)” and `R-MALF-01 §8`: records, relocation, selection normalization, malformed input, ordering. `R-CAT-01 §7`: model-top arithmetic. |
| [03 · World, visibility, rendering, audio and video]({{< research "research/retail-executable-spec/03-world-visibility-rendering-audio-and-video.md" >}}) | §2.4 and §2.4.1: model import, selection consumers, face dispatch, corner mapping and shading. `R-RAST-01 §1–§5, §8`: rasterization and composed world offsets. `R-RND-02A`: renderer selection. |
| [04 · Units, orders, scripts and movement]({{< research "research/retail-executable-spec/04-units-orders-scripts-and-movement.md" >}}) | §5.3: piece queries; `R-MOV-01 §8b`: the submergence consumer of the upper bound. |
| [07 · Interface, input, camera and front end]({{< research "research/retail-executable-spec/07-interface-input-camera-and-front-end.md" >}}) | `R-REV-01 §7`: model-top walk from selection-hover consumers. |
| [Nanolathe decoder]({{< research "formats/three_do.go" >}}) and [encoder]({{< research "formats/three_do_write.go" >}}) | Host implementation; the owning research describes decoder and encoder policy separately from retail behavior. |
| [Unofficial .3do note v0.9.1](https://units.tauniverse.com/tutorials/tadesign/tadesign/ta-3do-fmtV2.txt) | Dan Melchione, revised by Dark Rain: historical structures and examples. Its selection-offset interpretation is corrected by the later evidence. |
| [3DO, DXF, and LWO](https://units.tauniverse.com/tutorials/tadesign/tadesign/3dodesc.htm) | Historical modeling conventions, hierarchy and ground-plate descriptions; forward-axis and flag lore need the qualifications above. |

The source research also cites the inspected 3DOBuilder writers for their zero auxiliary fields and a 761-model base/expansion survey. Those findings do not recover the meaning of arbitrary auxiliary targets.

Continue with [GAF images and animations]({{< format-link "gaf" >}}), [COB unit scripts]({{< research "research/formats/cob.md" >}}), or [FBI unit definitions]({{< research "research/formats/fbi.md" >}}).
