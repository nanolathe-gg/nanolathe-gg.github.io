#!/usr/bin/env python3
"""Package native engine captures without altering their pixels or video streams."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess

STILLS = [
    "explosion-classic", "explosion-modern", "terrain-original", "terrain-synthesized",
    "camera-tactical", "water-off", "water-on", "reflection-off", "reflection-on",
    "materials-off", "materials-on", "aa-classic", "aa-modern",
]
MOVIES = [
    "explosion-classic", "explosion-modern", "camera-tactical", "water-off", "water-on",
    "reflection-off", "reflection-on", "materials-off", "materials-on",
]


def run(*args):
    return subprocess.run(args, check=True, capture_output=True).stdout


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rgba_sha(path):
    pixels = run("ffmpeg", "-v", "error", "-threads", "2", "-i", str(path),
                 "-frames:v", "1", "-f", "rawvideo", "-pix_fmt", "rgba", "-")
    return hashlib.sha256(pixels).hexdigest()


def probe(path):
    return json.loads(run("ffprobe", "-v", "error", "-count_frames", "-show_streams",
                          "-show_format", "-of", "json", str(path)))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path, help="Verified capture artifact directory")
    args = parser.parse_args()
    evidence = Path(__file__).resolve().parent
    root = evidence.parents[2]
    output = root / "static/images/renderer/v5"
    for name in STILLS:
        if not (args.source / f"{name}.png").is_file():
            raise FileNotFoundError(args.source / f"{name}.png")
    for name in MOVIES:
        if not (args.source / f"{name}.mp4").is_file():
            raise FileNotFoundError(args.source / f"{name}.mp4")
    output.mkdir(parents=True, exist_ok=True)
    inventory, verification = [], []
    for name in STILLS:
        source, dest = args.source / f"{name}.png", output / f"{name}.webp"
        run("cwebp", "-quiet", "-lossless", "-exact", "-z", "9", str(source), "-o", str(dest))
        original_rgba, exported_rgba = rgba_sha(source), rgba_sha(dest)
        if original_rgba != exported_rgba:
            raise ValueError(f"Pixel mismatch: {name}")
        stream = probe(dest)["streams"][0]
        verification.append({"source": source.name, "source_sha256": sha(source),
                             "export": dest.name, "export_sha256": sha(dest),
                             "decoded_rgba_sha256": exported_rgba, "pixels_identical": True})
        inventory.append({"path": str(dest.relative_to(root)), "sha256": sha(dest),
                          "bytes": dest.stat().st_size, "width": stream["width"],
                          "height": stream["height"], "lossless": True})
    for name in MOVIES:
        source, dest = args.source / f"{name}.mp4", output / f"{name}.mp4"
        shutil.copy2(source, dest)
        if sha(source) != sha(dest):
            raise ValueError(f"Video copy mismatch: {name}")
        info = probe(dest)
        streams = info["streams"]
        if len(streams) != 1 or streams[0]["codec_type"] != "video":
            raise ValueError(f"Expected one silent video stream: {name}")
        stream = streams[0]
        inventory.append({"path": str(dest.relative_to(root)), "sha256": sha(dest),
                          "bytes": dest.stat().st_size, "width": stream["width"],
                          "height": stream["height"], "codec": stream["codec_name"],
                          "frames": int(stream["nb_read_frames"]), "fps": stream["avg_frame_rate"],
                          "duration": info["format"]["duration"], "source_copy_identical": True})
    (evidence / "website-media.json").write_text(json.dumps(inventory, indent=2) + "\n")
    (evidence / "webp-export-verification.json").write_text(json.dumps(verification, indent=2) + "\n")
    print(f"Packaged {len(STILLS)} pixel-identical stills and {len(MOVIES)} unchanged movies.")


if __name__ == "__main__":
    main()
