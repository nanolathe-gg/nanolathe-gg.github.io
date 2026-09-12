+++
title = 'From sample bytes to sound'
seoTitle = 'WAV file format — illustrated Total Annihilation audio reference'
description = 'Listen to an original sound, inspect its PCM bytes, and follow the three container paths that the engine recognizes.'
type = 'format'
url = '/docs/formats/wav/'
format = 'WAV'
extension = '.wav'
sourcePath = 'research/formats/wav.md'
sourceRevision = 'c1b934071e15fc3156d9aa92ba91db26368768ac'
demoCSS = 'css/wav.css'
[[facts]]
label = 'Main container'
value = 'Microsoft RIFF / WAVE'
[[facts]]
label = 'Stock audio'
value = 'PCM · 8 or 16 bits'
[[facts]]
label = 'Legacy forms'
value = 'Raw PCM and DIGI'
[[facts]]
label = 'Common effects'
value = 'Mono · 11,025 Hz · 8-bit'
+++

## A sound you can inspect {#overview}

Most Total Annihilation `.wav` files are standard **RIFF WAVE containing PCM samples**. There is no TA-specific metadata in that canonical container. Two legacy forms matter too: raw sample bytes with no header, and a fixed-layout `DIGI` container.

{{< format-demo name="wav-listen" id="sound-example" title="Same chirp, two sample widths" label="Listen on demand" >}}
An original 400-millisecond descending chirp, generated for this guide. Both versions use 11,025 Hz mono PCM and the same synthesized waveform before quantization. The waveform above shows the 8-bit payload. Playback begins only when you press Play; these are browser audio controls, not a recreation of the retail audio backend.
{{< /format-demo >}}

Eight-bit PCM represents a sample as an unsigned byte centered around 128; 16-bit PCM uses a signed little-endian value centered around zero. More bits provide finer amplitude steps. In this example the 16-bit payload is twice the size; sample count, rate, and duration remain the same.

Sound effects and voices live in `sounds/`, referenced without extension by weapon TDFs, sound categories, and GUI events. Mission narration lives in `camps/briefs/`, selected by OTA fields such as `narration=` and `glamoursound=`.

## First identify the container {#detection}

The extension is not enough. The traced reader chooses a path from fixed signatures, in this order [02 §7; R-MALF-01 §10].

| Match | Selected path | Payload and metadata |
| --- | --- | --- |
| `DIGI` at 0, `HSHD` at 8, `SDAT` at 32 | Legacy DIGI | Rate at byte 22; bytes 40 through EOF; 8-bit mono. |
| Otherwise `RIFF` at 0 and `WAVE` at 8 | RIFF WAVE | First `fmt ` and first `data` chunks. |
| Otherwise | Raw | Entire file as unsigned 8-bit mono at 11,025 Hz. |

An unrecognized header can therefore become **sample data**, including its supposed header bytes. Recognized but malformed containers are a different case from a failed signature match.

{{< callout kind="note" title="Three containers, identical 8-bit sample payload" >}}
Download the same original sample as [RIFF WAVE](example-8bit.wav), [raw PCM](example-raw.wav), or [DIGI](example-digi.wav). The latter two are parser fixtures; browser playback above uses RIFF. The DIGI fixture leaves unused size fields at zero to demonstrate the traced fixed-position reader, not a general-purpose DIGI writer contract.
{{< /callout >}}

## Byte layouts {#byte-layouts}

### RIFF container and chunks

All numeric fields here are little-endian. The top-level offsets are file-relative.

| Offset | Bytes | Type | Field | Meaning |
| --- | --- | --- | --- | --- |
| `0x00` | 4 | ASCII | Chunk ID | `RIFF`. |
| `0x04` | 4 | `u32` | RIFF size | Declared container span minus 8. |
| `0x08` | 4 | ASCII | Form type | `WAVE`. |
| `0x0C` | Variable | Chunks | Chunk list | Walk to the declared RIFF span. |

Every child chunk starts with an eight-byte prefix. The literal space in **`fmt `** is part of its four-byte ID.

| Chunk-relative offset | Bytes | Type | Field | Meaning |
| --- | --- | --- | --- | --- |
| `+0x00` | 4 | ASCII | ID | For example `fmt ` or `data`. |
| `+0x04` | 4 | `u32` | Size | Payload length, excluding the eight-byte prefix. |
| `+0x08` | `size` | Bytes | Payload | Metadata, sample bytes, or another chunk's contents. |

### PCM format payload

These offsets are relative to the **start of the `fmt ` payload**, after its eight-byte chunk prefix. The first format chunk must have at least 16 payload bytes.

| Offset | Bytes | Type | Field | Retail read? |
| --- | --- | --- | --- | --- |
| `+0x00` | 2 | `u16` | Format tag | No; stock PCM is tag 1. |
| `+0x02` | 2 | `u16` | Channels | Yes. |
| `+0x04` | 4 | `u32` | Sample rate | Yes. |
| `+0x08` | 4 | `u32` | Byte rate | No; wrapper derives it. |
| `+0x0C` | 2 | `u16` | Block alignment | No; wrapper derives it. |
| `+0x0E` | 2 | `u16` | Bits per sample | Yes. |

For ordinary PCM, `frame_bytes = channels × bits_per_sample / 8`, and `byte_rate = sample_rate × frame_bytes`. A frame contains one sample per channel. The parser preserves the authored metadata words; the playback adapter separately derives its alignment.

### DIGI fixed positions

Offsets are file-relative. This table describes the traced reader, not the full historical container specification.

| Offset | Bytes | Type | Field | Retail behavior |
| --- | --- | --- | --- | --- |
| `0x00` | 4 | ASCII | Signature | Require `DIGI` for this path. |
| `0x04` | 4 | Bytes | Container size field | Not used for locating the sample. |
| `0x08` | 4 | ASCII | Header signature | Require `HSHD`. |
| `0x0C` | 10 | Bytes | Other header bytes | Not used by the described sample extraction. |
| `0x16` (22) | 4 | `u32` | Sample rate | **Little-endian**; 11,000 is adjusted to 11,025. |
| `0x1A` | 6 | Bytes | Other header bytes | Not used by the described sample extraction. |
| `0x20` (32) | 4 | ASCII | Sample signature | Require `SDAT`. |
| `0x24` | 4 | Bytes | SDAT size field | Ignored; sample extends to EOF. |
| `0x28` (40) | `size − 40` | `u8[]` | Sample bytes | Unsigned 8-bit mono. |

The sample-rate word's little-endian interpretation is established independently of the unused container-size fields. Raw PCM has no layout table: byte 0 is already sample 0.

## Walking chunks: the padding trap {#chunk-walk}

Retail advances by **`chunk_size + 8`, with no odd-byte padding**. Standard RIFF padding can therefore shift the next chunk away from where this reader expects it.

| One-byte chunk beginning at offset 12 | Position |
| --- | ---: |
| Chunk prefix | 12–19 |
| One payload byte | 20 |
| Retail's next chunk start | **21** |
| Standard padding byte | 21 |
| Standard next chunk start | **22** |

This is a one-byte difference in the next header's address, not an audio sample conversion. The supplied RIFF fixtures have even-sized chunks, so this distinction does not affect them.

The first `fmt ` and first `data` are selected independently from the beginning of the list: **data can precede format**. The walk stops when the next offset reaches `RIFF size + 8`. The first data chunk must declare a positive size and read back in full; otherwise the sample is null and the alias plays silently [02 R-MALF-01 §10].

{{< callout kind="warning" title="Ignoring the format tag is not codec support" >}}
Retail does not read the format tag and has no codec decoder in this wrapper. Compressed bytes are handed to a PCM backend using the declared channel count, rate, and width. Device creation may fail; playback as noise is not guaranteed either. Do not describe this permissiveness as compressed-format decoding.
{{< /callout >}}

## The example's 44-byte prefix {#worked-example}

The 8-bit fixture uses a conventional 16-byte PCM format chunk followed immediately by data. Its header is 44 bytes because of this chosen chunk order and size; **44 bytes is not a universal WAVE header length**.

| File offset | Contents | Example value |
| --- | --- | --- |
| `0x00` | `RIFF` + size + `WAVE` | RIFF size 4,446; file size 4,454. |
| `0x0C` | `fmt ` + payload size | 16-byte format payload. |
| `0x14` | PCM format payload | Tag 1, mono, 11,025 Hz, 8-bit. |
| `0x24` | `data` + payload size | 4,410 bytes. |
| `0x2C` | Sample payload | 4,410 complete one-byte frames. |

`4,410 / 11,025 = 0.4 seconds`. The 16-bit version has 8,820 payload bytes and the same 4,410 frames, giving an 8,864-byte file. The two legacy downloads retain the **same exact payload bytes as the 8-bit RIFF**: raw totals 4,410 bytes, DIGI 4,450 bytes.

The original chirp's attack and fading tail are encoded directly into the sample amplitudes. In-game volume, attenuation, and 3D positioning are runtime behavior, not extra WAV fields.

## Profiles found in the research corpus {#profiles}

These counts describe the inspected corpus; they are neither format limits nor a promise that every installation contains the same files.

| PCM profile | Observed count | Typical use |
| --- | ---: | --- |
| Mono · 11,025 Hz · 8-bit | 482 | Effects and unit voices. |
| Mono · 22,050 Hz · 16-bit | 74 | Mission briefing narration. |
| Stereo · 44,100 Hz · 16-bit | 4 | Core Contingency victory music. |
| Mono · 22,254 Hz · 8-bit | 1 | `sounds/CDOGGY.WAV`; a classic Macintosh-rate authoring leftover. |

The inspected installation also contains one raw file, `sounds/HONK.WAV`, and one DIGI file, `sounds/SING.WAV`; both play as unsigned 8-bit mono at 11,025 Hz. The research's retail button-click example was omitted from publication; the sound on this page is independently synthesized.

## Parsing ends at a device boundary {#playback-policy}

Nanolathe's shared `formats.LoadAudio` preserves container identity, authored PCM fields, and the full payload span. It checks file bounds and rejects truncated recognized containers. RIFF enumeration uses the declared span and the researched unpadded chunk stepping.

{{< callout kind="policy" title="The playback adapter has its own acceptance rules" >}}
Nanolathe accepts PCM with 8- or 16-bit samples, a positive channel count and rate, and representable frame size/byte rate. It rejects unsupported codecs, unsafe metadata, empty input, and direct-decode allocations beyond 16 MiB. It copies complete frames and retains VFS provenance. These are host policies, not retail checks on ignored metadata fields. The parser still retains a partial final frame even when playback excludes it.
{{< /callout >}}

For retail static and transient samples, the wrapper derives PCM parameters and passes the selected sample length directly to DirectSound. There is no separate zero-length rejection or repair fallback. Creation failure gives a null sample; lock, short-read, or unlock failure releases the buffer and also returns null.

| Empty raw input path | Established wrapper action | What remains unproven |
| --- | --- | --- |
| Static / transient | Request a zero-byte device buffer. | Whether the target backend accepts that request. |
| Streaming | Request a normal two-second buffer, then fill the initial EOF remainder with unsigned-8-bit silence and record the endpoint. | Whether that backend successfully creates or plays it. |

Streaming capacity comes from two seconds of the selected PCM parameters, independently of payload size [03 R-AUD-02 §1]. It therefore differs from the zero-size static request.

{{< callout kind="unknown" title="Backend acceptance is an external result" >}}
The actual DirectSound implementation's behavior for zero-byte buffers or unusual channel/rate/width combinations was not observed in this audit. Another wrapper trace cannot settle it; inspecting or exercising the target backend would. The traced boundary is established, while its device result remains unknown [03 §8.2].
{{< /callout >}}

## Sources and example files {#sources}

Adapted from the [owning WAV research]({{< research >}}) at the pinned sidebar revision. The [complete source snapshot](research-source.txt) retains its upstream bibliography and evidence labels. Numeric PCM field offsets are also reflected in the same revision's [shared audio parser](https://github.com/nanolathe-gg/nanolathe/blob/c1b934071e15fc3156d9aa92ba91db26368768ac/formats/wav.go).

All four audio files and the waveform were authored for this guide. `scripts/wav-example.py --check` reproduces them and independently reads both RIFF files with Python's standard-library WAVE parser to verify rate, sample width, frame count, and payload. No retail sound recording is included.
