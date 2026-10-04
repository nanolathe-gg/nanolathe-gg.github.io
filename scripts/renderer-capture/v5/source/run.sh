#!/bin/bash
set -euo pipefail

# Run from the pinned isolated engine checkout. Retail content is read in place.
repo=$(git rev-parse --show-toplevel)
out=${1:-/Users/daniel/Documents/Codex/2026-10-03/task/capture-features-v5}
cache=$(mktemp -d /tmp/nanolathe-features-v5-cache.XXXXXX)
bin=$(mktemp -d /tmp/nanolathe-features-v5-bin.XXXXXX)
export GOCACHE=/tmp/nanolathe-capture-gocache
export GOMAXPROCS=2
export EBITENGINE_GRAPHICS_LIBRARY=metal
mkdir -p "$out/raw"

for package in core camera water materials; do
  go build -p 2 -o "$bin/$package" "$repo/cmd/website-features-capture/$package"
done

capture() {
  local name=$1
  shift
  caffeinate -u -t 60 "$@" > "$out/$name.log" 2>&1
}

capture explosion "$bin/core" -scene lighting -frames 90 -cache "$cache" -out "$out/raw/explosion"
capture landscape "$bin/core" -scene landscape -map Greenhaven -x 4250 -z 4040 -frames 1 -cache "$cache" -out "$out/raw/landscape"
capture camera "$bin/camera" -mode movies -map Greenhaven -x 4100 -z 4340 -remaster -cache "$cache" -out "$out/raw/camera"
capture water "$bin/water" -scene coast -frames 180 -out "$out/raw/water"
capture reflection "$bin/water" -scene reflection -frames 180 -out "$out/raw/reflection"
capture materials "$bin/materials" -map 'Comet Catcher' -units armmanni -frames 180 -width 512 -height 512 -out "$out/raw/materials"
capture aa-2x "$bin/core" -scene aa -frames 1 -zoom 2 -cache "$cache" -out "$out/raw/aa-2x"
capture aa-1x "$bin/core" -scene aa -frames 1 -zoom 1 -cache "$cache" -out "$out/raw/aa-1x"

# Independent positive backend probes; native first frames must replay exactly.
capture backend-core "$bin/core" -scene landscape -map Greenhaven -x 4250 -z 4040 -frames 1 -cache "$cache" -out "$out/verification/backend-core"
capture backend-water "$bin/water" -scene reflection -frames 1 -out "$out/verification/backend-water"
capture backend-materials "$bin/materials" -map 'Comet Catcher' -units armmanni -frames 1 -width 512 -height 512 -out "$out/verification/backend-materials"
capture backend-camera "$bin/camera" -mode movies -limit 1 -map Greenhaven -x 4100 -z 4340 -remaster -cache "$cache" -out "$out/verification/backend-camera"

go test -p 2 ./cmd/website-features-capture/... > "$out/checks.log" 2>&1
go vet -p 2 ./cmd/website-features-capture/... > "$out/vet.log" 2>&1
python3 "$repo/cmd/website-features-capture/export.py" "$out"
python3 "$repo/cmd/website-features-capture/audit.py" "$out"
printf 'Private derived-art cache retained at %s; do not package it.\n' "$cache"
