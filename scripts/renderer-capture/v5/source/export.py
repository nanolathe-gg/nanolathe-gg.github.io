#!/usr/bin/env python3
"""Copy native posters, encode bounded frame sequences, and verify provenance.

No crop, resize, compositing, generated art, or pixel edit is performed here.
"""
import argparse
import hashlib
import json
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path

from PIL import Image, ImageChops, ImageStat

PIN = "279f7af159a7d33ffd16358d1133434d9d48c7b9"
POSTERS = {
    "explosion-classic": "explosion/cpu-0042.png",
    "explosion-modern": "explosion/gpu-0042.png",
    "terrain-original": "landscape/modern-original-0000.png",
    "terrain-synthesized": "landscape/gpu-0000.png",
    "camera-tactical": "camera/camera/0000.png",
    "water-off": "water/off-0090.png",
    "water-on": "water/on-0090.png",
    "reflection-off": "reflection/off-0090.png",
    "reflection-on": "reflection/on-0090.png",
    "materials-off": "materials/armmanni/off-0035.png",
    "materials-on": "materials/armmanni/on-0035.png",
    "aa-classic": "aa-2x/cpu-0000.png",
    "aa-modern": "aa-2x/gpu-0000.png",
    # Supplemental native evidence, not required by the six website chapters.
    "landscape-classic": "landscape/cpu-0000.png",
    "landscape-modern": "landscape/gpu-0000.png",
    "aa-1x-classic": "aa-1x/cpu-0000.png",
    "aa-1x-modern": "aa-1x/gpu-0000.png",
    "camera-tactical-end": "camera/camera/0179.png",
    "camera-normal": "camera/camera/0071.png",
}
MOVIES = {
    "explosion-classic": ("explosion/cpu-%04d.png", 90),
    "explosion-modern": ("explosion/gpu-%04d.png", 90),
    "camera-tactical": ("camera/camera/%04d.png", 180),
    "water-off": ("water/off-%04d.png", 180),
    "water-on": ("water/on-%04d.png", 180),
    "reflection-off": ("reflection/off-%04d.png", 180),
    "reflection-on": ("reflection/on-%04d.png", 180),
    "materials-off": ("materials/armmanni/off-%04d.png", 180),
    "materials-on": ("materials/armmanni/on-%04d.png", 180),
}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def stamp(path):
    return datetime.fromtimestamp(path.stat().st_mtime, timezone.utc).isoformat()


def png_info(path):
    with Image.open(path) as im:
        assert im.format == "PNG"
        rgba = im.convert("RGBA")
        return {"bytes": path.stat().st_size, "sha256": sha(path),
                "width": im.width, "height": im.height,
                "rgba_pixel_sha256": hashlib.sha256(rgba.tobytes()).hexdigest(),
                "capture_file_mtime_utc": stamp(path)}


def comparison(a, b):
    with Image.open(a) as ia, Image.open(b) as ib:
        assert ia.size == ib.size
        x, y = ia.convert("RGBA"), ib.convert("RGBA")
        xb, yb = x.tobytes(), y.tobytes()
        changed = sum(xb[i:i+4] != yb[i:i+4] for i in range(0, len(xb), 4))
        diff = ImageChops.difference(x.convert("RGB"), y.convert("RGB"))
        return {"changed_pixels": changed, "total_pixels": x.width*x.height,
                "rgb_absolute_difference_sum": int(sum(ImageStat.Stat(diff).sum))}


def read_jsonl(path):
    return [json.loads(line) for line in path.read_text().splitlines()]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("out", type=Path)
    ap.add_argument("--skip-existing", action="store_true")
    args = ap.parse_args()
    out = args.out.resolve()
    raw = out / "raw"
    source = Path(__file__).resolve().parent
    repo = source.parents[1]
    manifest = {"schema": 1, "engine_revision": PIN,
                "harness_revision": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=repo, text=True).strip(),
                "exported_utc": datetime.now(timezone.utc).isoformat(),
                "capture_backend": "Ebitengine v2.10.4, forced Metal; NewChecked and GPU Execute/ReadPixels completed",
                "pixel_policy": "native capture PNG copied byte-for-byte; video has only H.264/yuv420p encoding, no resize/crop/filter/composite",
                "cadence": "offline bounded captures, 30 encoded frames/s; no performance claim",
                "posters": {}, "movies": {}, "comparisons": {}, "sources": {}}
    for name, rel in POSTERS.items():
        original, target = raw / rel, out / (name + ".png")
        info = png_info(original)
        shutil.copyfile(original, target)
        assert sha(target) == info["sha256"]
        info["raw_source"] = str(original)
        info["raw_relative_source"] = str(Path("raw") / rel)
        info["native_byte_copy"] = True
        manifest["posters"][target.name] = info
    for name, (rel, frames) in MOVIES.items():
        target = out / (name + ".mp4")
        pattern = raw / rel
        first = Path(str(pattern) % 0)
        dimensions = png_info(first)
        for n in range(frames):
            assert Path(str(pattern) % n).is_file()
        assert not Path(str(pattern) % frames).exists()
        command = ["ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
                   "-framerate", "30", "-start_number", "0", "-i", str(pattern),
                   "-frames:v", str(frames), "-c:v", "libx264", "-threads", "2",
                   "-preset", "slow", "-crf", "12" if name.startswith("materials") else "18",
                   "-pix_fmt", "yuv420p", "-an", "-movflags", "+faststart", str(target)]
        if not (args.skip_existing and target.exists()):
            subprocess.run(command, check=True)
        probe = json.loads(subprocess.check_output([
            "ffprobe", "-v", "error", "-count_frames", "-select_streams", "v:0",
            "-show_entries", "stream=codec_name,width,height,nb_read_frames,r_frame_rate,duration,pix_fmt",
            "-of", "json", str(target)], text=True))["streams"][0]
        assert int(probe["nb_read_frames"]) == frames
        assert probe["width"] == dimensions["width"] and probe["height"] == dimensions["height"]
        assert probe["r_frame_rate"] == "30/1" and abs(float(probe["duration"])-frames/30) < 0.001
        # Decode the whole video independently, so a metadata-only frame count cannot pass.
        decode = subprocess.check_output(["ffmpeg", "-v", "error", "-threads", "2", "-i", str(target),
                                          "-f", "framemd5", "-"])
        decoded = [line for line in decode.decode().splitlines() if line and not line.startswith("#")]
        assert len(decoded) == frames
        (out / (name + "-decoded.framemd5")).write_bytes(decode)
        manifest["movies"][target.name] = {"sha256": sha(target), "bytes": target.stat().st_size,
                                           "raw_pattern": str(pattern), "frames": frames,
                                           "decoded_frames": len(decoded), "probe": probe,
                                           "encode_command": command}
        print("verified", target.name, frames, probe["width"], probe["height"], flush=True)
    for name, a, b in [
        ("terrain_only", "terrain-original", "terrain-synthesized"),
        ("water", "water-off", "water-on"), ("reflection", "reflection-off", "reflection-on"),
        ("materials", "materials-off", "materials-on"),
        ("whole_renderer_aa_2x", "aa-classic", "aa-modern"),
        ("whole_renderer_explosion", "explosion-classic", "explosion-modern")]:
        manifest["comparisons"][name] = comparison(out/(a+".png"), out/(b+".png"))
    manifest["comparisons"]["lighting_and_glow_control_frame42"] = comparison(
        raw/"explosion/gpu-no-light-glow-0042.png", raw/"explosion/gpu-0042.png")
    manifest["comparisons"]["glow_control_frame42"] = comparison(
        raw/"explosion/gpu-no-glow-0042.png", raw/"explosion/gpu-0042.png")
    raw_inventory = {}
    for p in sorted(raw.rglob("*.png")):
        raw_inventory[str(p.relative_to(out))] = png_info(p)
    (out/"raw-png-manifest.json").write_text(json.dumps(raw_inventory, indent=2)+"\n")
    manifest["raw_png_count"] = len(raw_inventory)
    manifest["raw_png_manifest_sha256"] = sha(out/"raw-png-manifest.json")
    for p in sorted(source.rglob("*")):
        if p.is_file() and "__pycache__" not in p.parts:
            rel = p.relative_to(source)
            target = out/"source"/rel
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(p, target)
            manifest["sources"][str(rel)] = sha(p)
    manifest["metadata_sources"] = {str(p.relative_to(out)): sha(p)
                                    for p in sorted(raw.rglob("*")) if p.is_file() and p.suffix in [".json", ".jsonl"]}
    (out/"manifest.json").write_text(json.dumps(manifest, indent=2)+"\n")


if __name__ == "__main__":
    main()
