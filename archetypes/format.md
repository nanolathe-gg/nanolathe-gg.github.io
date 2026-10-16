+++
title = '{{ .Name | upper }} file format'
description = 'What this format stores and why you would read it.'
type = 'format'
url = '/docs/formats/{{ .Name }}/'
format = '{{ .Name | upper }}'
extension = '.{{ .Name }}'
sourcePath = 'research/formats/{{ .Name }}.md'
sourceRevision = 'REPLACE_WITH_FULL_ENGINE_COMMIT'
[[facts]]
label = 'Byte order'
value = 'Little-endian'
[[facts]]
label = 'Stores'
value = 'Describe the payload'
+++

## Overview {#overview}

Explain what the file stores and where TA uses it. Give this section a heading
that names its subject. Follow brand/GUIDE.md#writing-voice, retain evidence
labels and cite the research.

{{< callout kind="note" title="About the examples" >}}
State the provenance and scope of any examples.
{{< /callout >}}

## File organization {#structure}

Add an accessible diagram and a prose equivalent.

## Byte layouts {#byte-layouts}

### File header

| Offset | Bytes | Type | Field | Meaning |
| --- | --- | --- | --- | --- |
| `0x00` | 4 | `u32` | `field` | Description. |

## Worked example {#worked-example}

Add an original downloadable fixture and explain its bytes. Use the figure
shortcode for static media or format-demo with a dedicated formats/ partial.

## Unknowns and caveats {#unknowns-and-caveats}

Keep host policy distinct from retail behavior.

## Sources {#sources}

[Owning research]({{< research >}}).
