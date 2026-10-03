#!/usr/bin/env python3
"""Package untouched real captures and produce machine-readable evidence."""
import argparse
import hashlib
import json
import shutil
import subprocess
from pathlib import Path

from PIL import Image, ImageChops

ENGINE_REVISION = "ac32756e0caffbc37e0fb80b21c03d3c641f1d21"


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path, value):
    path.write_text(json.dumps(value, indent=2) + "\n")


def changed(a, b):
    difference = ImageChops.difference(Image.open(a).convert("RGB"), Image.open(b).convert("RGB"))
    return {"pixels": sum(pixel != (0, 0, 0) for pixel in difference.get_flattened_data()), "bbox": difference.getbbox()}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--lighting", type=Path, required=True)
    parser.add_argument("--landscape", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    selected = {
        "explosion-classic.png": args.lighting / "cpu-0042.png",
        "explosion-modern.png": args.lighting / "gpu-0042.png",
        "explosion-bright-classic.png": args.lighting / "cpu-0038.png",
        "explosion-bright-modern.png": args.lighting / "gpu-0038.png",
        "landscape-classic.png": args.landscape / "cpu-0000.png",
        "landscape-modern.png": args.landscape / "gpu-0000.png",
        "control-modern-no-glow.png": args.lighting / "gpu-no-glow-0042.png",
        "control-modern-no-light-glow.png": args.lighting / "gpu-no-light-glow-0042.png",
    }
    for name, source in selected.items():
        assert Image.open(source).size == (960, 640)
        shutil.copyfile(source, args.out / name)
        assert digest(source) == digest(args.out / name)

    records = {}
    for scene, raw in (("lighting", args.lighting), ("landscape", args.landscape)):
        rows = [json.loads(line) for line in (raw / "events.jsonl").read_text().splitlines()]
        synthesis = json.loads((raw / "synthesis.json").read_text())
        assert synthesis["first_call_cached"] is False
        assert synthesis["second_call_cached"] is True
        assert synthesis["cold_and_warm_output_identical"] is True
        for row in rows:
            assert row["state_unchanged_after_recording"] is True
            assert row["presentation_crt_bound_classic"] is True
            assert row["presentation_crt_bound_modern"] is True
            assert row["cpu_indexed_bytes"] == 960 * 640
            assert row["gpu_classic_planes"] == 0
            assert row["cpu_terrain"]["DetailTiles"] == 0
            assert row["gpu_terrain"]["DetailTiles"] == synthesis["synthesized_tiles"]
            assert row["cpu_terrain"]["Camera"] == row["gpu_terrain"]["Camera"] == row["camera"]
            assert row["camera"]["Zoom"] == 2048 and row["camera"]["Scale"] == 4
        for original, target in (("events.jsonl", f"{scene}-events.jsonl"), ("synthesis.json", f"{scene}-synthesis.json")):
            shutil.copyfile(raw / original, args.out / target)
        records[scene] = {"frames": len(rows), "tick_range": [rows[0]["tick"], rows[-1]["tick"]], "synthesis": synthesis}

    for renderer, pattern in (("classic", "cpu"), ("modern", "gpu")):
        movie = args.out / f"explosion-{renderer}.mp4"
        subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-framerate", "30", "-i", str(args.lighting / f"{pattern}-%04d.png"), "-frames:v", "60", "-c:v", "libx264", "-threads", "2", "-preset", "slow", "-crf", "18", "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(movie)], check=True)
        probe = json.loads(subprocess.check_output(["ffprobe", "-v", "error", "-show_streams", "-show_format", "-of", "json", str(movie)]))
        stream = probe["streams"][0]
        assert stream["width"] == 960 and stream["height"] == 640
        assert stream["nb_frames"] == "60" and stream["r_frame_rate"] == "30/1"
        assert float(probe["format"]["duration"]) == 2.0
        records[f"video_{renderer}"] = probe

    row = [json.loads(line) for line in (args.lighting / "events.jsonl").read_text().splitlines()][42]
    no_glow = args.out / "control-modern-no-glow.png"
    no_light = args.out / "control-modern-no-light-glow.png"
    glow_delta = changed(args.out / "explosion-modern.png", no_glow)
    light_delta = changed(no_glow, no_light)
    assert glow_delta["pixels"] > 0 and light_delta["pixels"] > 0
    records["selected_explosion"] = row
    records["same_modern_drawlist_controls"] = {"glow_delta": glow_delta, "lighting_delta_with_glow_off": light_delta}
    records["classic_vs_modern_explosion"] = changed(args.out / "explosion-classic.png", args.out / "explosion-modern.png")
    records["classic_vs_modern_landscape"] = changed(args.out / "landscape-classic.png", args.out / "landscape-modern.png")
    records["checks"] = {"actual_software_indexed_classic": True, "actual_gpu_modern": True, "matching_committed_inputs_unchanged": True, "matching_camera": True, "production_presentation_crt_bound_both": True, "modern_synthesized_2x_terrain_recorded": True, "classic_original_art_recorded": True, "cold_cache_warm_cache_identical": True, "all_pngs_native_unmodified": True}
    write_json(args.out / "verification.json", records)

    source_out = args.out / "source"
    source_out.mkdir(exist_ok=True)
    for source in Path(__file__).parent.iterdir():
        if source.suffix in (".go", ".py", ".md"):
            shutil.copyfile(source, source_out / source.name)
    native = {}
    for scene, raw in (("lighting", args.lighting), ("landscape", args.landscape)):
        native[scene] = {p.name: {"bytes": p.stat().st_size, "sha256": digest(p)} for p in sorted(raw.glob("*.png"))}
    write_json(args.out / "raw-frame-hashes.json", native)
    manifest = {
        "engine_source_revision": ENGINE_REVISION,
        "capture_harness_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip(),
        "backend": "Metal; EBITENGINE_GRAPHICS_LIBRARY=metal",
        "native_dimensions": [960, 640],
        "renderer_controls": {
            "classic_anti_alias": row["cpu_anti_alias"],
            "modern_anti_alias": row["gpu_anti_alias"],
            "modern_effects": row["effects_selection"],
            "modern_glow": row["glow"],
            "modern_glow_strength": row["glow_strength"],
            "modern_ground_light_strength": 100,
            "modern_blast_ring_strength": 100,
            "shadow_controls": {"master": True, "features": True, "vehicles": True},
        },
        "terrain_scope": {
            "synthesized_terrain_tiles": True,
            "synthesized_foliage_sprite_banks": False,
            "foliage_path": "stock nearest-doubled feature sprites on both clients",
        },
        "selected_source_pngs": {name: {"raw_source": str(source), "sha256": digest(source)} for name, source in selected.items()},
        "files": {str(p.relative_to(args.out)): {"bytes": p.stat().st_size, "sha256": digest(p)} for p in sorted(args.out.rglob("*")) if p.is_file() and p.name != "manifest.json"},
        "archive_files_packaged": [],
        "derived_synthesis_cache_packaged": False,
    }
    write_json(args.out / "manifest.json", manifest)
    print("Verified native PNG pairs, software/GPU paths, matched inputs, production CRT binding, synthesized terrain, effects, cache and video metadata.")


if __name__ == "__main__":
    main()
