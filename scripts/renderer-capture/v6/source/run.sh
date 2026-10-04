#!/bin/bash
set -euo pipefail
# From an isolated checkout at 617540c587e1b75d6d8ba7bf5243d24bea3f3bc2,
# copy this source directory to cmd/website-features-capture first.
out=${1:?absolute capture artifact directory required}
cache=${2:?private synthesis cache directory required}
bin=$(mktemp -d /tmp/nanolathe-v6-bin.XXXXXX)
export GOCACHE=/tmp/nanolathe-capture-gocache GOMAXPROCS=2 EBITENGINE_GRAPHICS_LIBRARY=metal
mkdir -p "$out/raw"
for package in core camera water; do
 go build -p 2 -o "$bin/$package" "./cmd/website-features-capture/$package"
done
capture() { local name=$1; shift; caffeinate -u -t 60 "$@" > "$out/$name.log" 2>&1; }
capture terrain "$bin/core" -scene landscape -map Greenhaven -x 4440 -z 4130 -width 480 -height 320 -frames 1 -cache "$cache" -out "$out/raw/terrain"
capture explosion "$bin/core" -scene lighting -map Greenhaven -x 4280 -z 4230 -frames 90 -cache "$cache" -out "$out/raw/explosion"
capture zoom "$bin/camera" -mode slider -map Greenhaven -x 4100 -z 4340 -remaster -cache "$cache" -out "$out/raw/zoom"
capture water "$bin/water" -scene fleet -frames 180 -out "$out/raw/water"
capture heat "$bin/core" -scene heat -frames 150 -width 480 -height 320 -cache "$cache" -out "$out/raw/heat"
capture wrecks "$bin/core" -scene wrecks -frames 390 -width 480 -height 320 -cache "$cache" -out "$out/raw/wrecks"
capture aa "$bin/core" -scene aa -frames 1 -cache "$cache" -out "$out/raw/aa"
go test -p 2 ./cmd/website-features-capture/... > "$out/checks.log" 2>&1
go vet -p 2 ./cmd/website-features-capture/... > "$out/vet.log" 2>&1
# Preserve the exact producer binary hashes alongside the artifacts.
shasum -a 256 "$bin/core" "$bin/camera" "$bin/water" > "$out/binaries.sha256"
