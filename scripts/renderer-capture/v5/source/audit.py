#!/usr/bin/env python3
"""Check the captured publication, camera, payload, native size, and Metal evidence."""
import hashlib
import json
import subprocess
import sys
from pathlib import Path

out = Path(sys.argv[1]).resolve()
repo = Path(__file__).resolve().parents[2]
pin = "279f7af159a7d33ffd16358d1133434d9d48c7b9"


def load(name):
    return json.loads((out/name).read_text())


def rows(name):
    return [json.loads(x) for x in (out/name).read_text().splitlines()]


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


result = {"engine_revision": pin, "checks": {}}
explosion = rows("raw/explosion/events.jsonl")
assert len(explosion) == 90
assert all(r["state_unchanged_after_recording"] and r["presentation_crt_bound_classic"]
           and r["presentation_crt_bound_modern"] for r in explosion)
assert all(r["camera"] == explosion[0]["camera"] and r["gpu_classic_planes"] == 0
           and r["cpu_indexed_bytes"] == 960*640 for r in explosion)
assert all(0 < r["gpu_ssaa_packets"] <= r["gpu_models"] for r in explosion)
inventory = load("raw-png-manifest.json")
for r in explosion:
    assert inventory[f"raw/explosion/cpu-{r['frame']:04d}.png"]["rgba_pixel_sha256"] == r["cpu_rgba_sha256"]
result["checks"]["explosion_matched_publication_camera_cpu_pixels_and_real_gpu_geometry"] = True
result["explosion_poster"] = {"frame": 42, "tick": explosion[42]["tick"],
                               "state_sha256": explosion[42]["state_sha256"],
                               "camera": explosion[42]["camera"],
                               "effects": explosion[42]["effects_selection"],
                               "gpu_stats": explosion[42]["gpu_stats"],
                               "synthesized_sprite_commands": explosion[42]["gpu_terrain"]["SynthesizedSpriteCommands"]}

land = rows("raw/landscape/events.jsonl")
control = land[0]
assert control["same_camera_and_feature_sprites"]
assert control["terrain_original_audit"]["Camera"] == control["terrain_synthesized_audit"]["Camera"]
assert control["terrain_original_audit"]["DetailTiles"] == 0
assert control["terrain_synthesized_audit"]["DetailTiles"] == 2347
assert control["terrain_original_audit"]["SynthesizedSpriteCommands"] == control["terrain_synthesized_audit"]["SynthesizedSpriteCommands"] == 26
result["checks"]["terrain_only_tiles_change_same_modern_camera_and_synthesized_banks"] = True
result["terrain_control"] = control
result["synthesis"] = {}
for scene in ["explosion", "landscape", "camera", "aa-1x", "aa-2x"]:
    s = load(f"raw/{scene}/synthesis.json")
    assert s["texture_synthesis_scale"] == 2 and s["source_tile_dimensions"] == [32, 32]
    assert s["output_tile_dimensions"] == [64, 64] and s["second_call_cached"]
    assert s["cold_and_warm_output_identical"] and s["pixels_different_from_nearest_doubling"] > 0
    for bank in s["feature_bank_proof"]:
        assert bank["dimensions_2x_verified"] and bank["anchor_offsets_2x_verified"]
        assert bank["second_cached"] and bank["payload_sha256"] == bank["warm_payload_sha256"]
    result["synthesis"][scene] = s
result["checks"]["terrain_payload_and_independent_sprite_variants_verified"] = True

cam = load("raw/camera/movies-metadata.json")
assert len(cam) == 180
assert all(r["publication_unchanged"] and r["crt_bound"] and r["units"] == 38 for r in cam)
assert cam[0]["shot"]["Zoom"] == 2 and cam[-1]["shot"]["Zoom"] == .25
assert cam[0]["shot"]["X"] == 4100 and cam[-1]["shot"]["X"] == 4500
assert cam[0]["models"] == 38 and cam[-1]["models"] == 0
assert cam[-1]["strategic_view"] and cam[-1]["strategic_icons"]
assert cam[-1]["terrain_record"]["MarkersCount"] == 38
assert cam[0]["terrain_record"]["SynthesizedSpriteCommands"] > 0
assert cam[-1]["terrain_record"]["SynthesizedSpriteCommands"] == 0
result["checks"]["actual_camera_pan_zoom_and_native_tactical_icons"] = True
result["camera_keyframes"] = {str(n): cam[n] for n in [0, 71, 120, 179]}

for scene in ["water", "reflection"]:
    r = load(f"raw/{scene}/census.json")
    assert len(r) == 180
    assert all(x["publication_unchanged"] and x["crt_bound"] for x in r)
    assert all(x["off_on_off_exact"] for x in r if x["frame"] % 30 == 0)
    assert all(x["model_commands"] == (1 if scene == "reflection" else 0) for x in r)
    assert all(x["stats_off"]["ReflectionVertices"] == 0 for x in r)
    if scene == "reflection":
        assert all(x["stats_on"]["ReflectionVertices"] > 0 for x in r)
        assert r[0]["units"] != r[-1]["units"]
    result["checks"][scene+"_same_list_publication_and_exact_control_restoration"] = True
    result[scene] = {"first": r[0], "poster": r[90], "last": r[-1]}

mat = load("raw/materials/metadata.json")
assert len(mat) == 180
assert all(x["publication_unchanged"] and x["same_recorded_drawlist"] and x["crt_bound"] for x in mat)
assert all(x["model"] == "armmanni" and x["width"] == 512 and x["height"] == 512 and x["zoom"] == 2 for x in mat)
assert all(x["heading"] == x["frame"]*65536//180 for x in mat)
assert "off/on/off exact restoration passed" in (out/"materials.log").read_text()
result["checks"]["native_square_material_turntable_same_list_and_unchanged_publication"] = True
result["materials_poster"] = mat[35]
for scale, zoom in [("1x", 1024), ("2x", 2048)]:
    r = rows(f"raw/aa-{scale}/events.jsonl")[0]
    assert r["camera"]["Zoom"] == zoom and r["cpu_anti_alias"] and r["gpu_anti_alias"]
    assert r["gpu_models"] == 5 and r["gpu_ssaa_packets"] == 5
    assert r["state_unchanged_after_recording"] and r["gpu_classic_planes"] == 0
    result["aa_"+scale] = r
result["checks"]["native_aa_whole_renderer_pairs_1x_and_2x"] = True

result["backend_probes"] = {}
for scene in ["core", "water", "materials", "camera"]:
    log = out/f"backend-{scene}.log"
    assert "BACKEND actual=Metal" in log.read_text()
    result["backend_probes"][scene] = {"log": log.name, "sha256": sha(log), "actual_backend": "Metal"}
matches = [
    ("raw/landscape/cpu-0000.png", "verification/backend-core/cpu-0000.png"),
    ("raw/landscape/gpu-0000.png", "verification/backend-core/gpu-0000.png"),
    ("raw/landscape/modern-original-0000.png", "verification/backend-core/modern-original-0000.png"),
    ("raw/reflection/off-0000.png", "verification/backend-water/off-0000.png"),
    ("raw/reflection/on-0000.png", "verification/backend-water/on-0000.png"),
    ("raw/materials/armmanni/off-0000.png", "verification/backend-materials/armmanni/off-0000.png"),
    ("raw/materials/armmanni/on-0000.png", "verification/backend-materials/armmanni/on-0000.png"),
    ("raw/camera/camera/0000.png", "verification/backend-camera/camera/0000.png")]
assert all(sha(out/a) == sha(out/b) for a, b in matches)
result["checks"]["all_four_actual_metal_backend_probes_and_identical_first_frame_replay"] = True
result["production_source_sha256"] = {p: sha(repo/p) for p in [
    "docs/DESIGN_GPU_RENDERER.md", "docs/FILM_CAPTURE.md", "cmd/nanolathe/detail_art.go",
    "internal/drawlist/effects.go", "internal/platform/gpurender/renderer.go",
    "internal/platform/gpurender/visual_controls.go", "internal/client/detail_art.go",
    "internal/upscale/cache.go", "internal/upscale/terrain.go", "internal/upscale/sprite.go", "internal/upscale/bank.go"]}
changed = subprocess.check_output(["git", "diff", pin, "--name-only"], cwd=repo, text=True).splitlines()
assert all(p.startswith("cmd/website-features-capture/") for p in changed)
result["checks"]["production_sources_unchanged"] = True
(out/"verification.json").write_text(json.dumps(result, indent=2)+"\n")
print("All", len(result["checks"]), "capture audit groups passed")
