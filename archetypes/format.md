+++
title = '{{ .Name | upper }} — Format title'
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

## Overview

Explain the file's role. Retain evidence labels and cite the owning research.

{{< callout kind="note" title="About the examples" >}}
State the provenance and scope of any examples.
{{< /callout >}}

## Format at a glance

Add an accessible diagram and a prose equivalent.

## Byte layouts

### File header

| Offset | Bytes | Type | Field | Meaning |
| --- | --- | --- | --- | --- |
| `0x00` | 4 | `u32` | `field` | Description. |

## Worked example

Add an original downloadable fixture and explain its bytes. Use the figure
shortcode for static media or format-demo with a dedicated formats/ partial.

## Unknowns and caveats

Keep host policy distinct from retail behavior.

## Sources

[Owning research]({{< research >}}).
