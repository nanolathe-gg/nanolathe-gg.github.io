"""Prepare public installers from an exact, already-pushed engine commit.

Run the engine gates and native installer checks first. This only stages website
files; committing/pushing the website publishes the chosen source release.
"""
import argparse
import hashlib
import io
import json
from pathlib import Path
import re
import subprocess
import tarfile
from urllib.request import urlopen
import zipfile

ROOT = Path(__file__).resolve().parents[1]
PLATFORMS = ("darwin-amd64", "darwin-arm64", "linux-amd64", "linux-arm64", "windows-amd64")


def download(url):
    with urlopen(url, timeout=180) as response:
        return response.read()


def sha(data):
    return hashlib.sha256(data).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--engine", type=Path, required=True)
    parser.add_argument("--revision", required=True, help="Full engine commit, already public on GitHub")
    parser.add_argument("--version", required=True, help="Release label, for example 0.1.0-alpha.1")
    parser.add_argument("--go-version", default="1.26.8")
    args = parser.parse_args()
    if not re.fullmatch(r"[0-9a-f]{40}", args.revision):
        parser.error("--revision must be a full lowercase commit hash")
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]{0,63}", args.version):
        parser.error("--version must be a short filename-safe label")
    if not re.fullmatch(r"[0-9]+\.[0-9]+\.[0-9]+", args.go_version):
        parser.error("--go-version must be an exact Go patch version")
    releases = json.loads(download("https://go.dev/dl/?mode=json&include=all"))
    release = next((r for r in releases if r["version"] == "go" + args.go_version), None)
    if not release or not release["stable"]:
        parser.error("Go version must identify a stable official release")
    fields = {"version": args.version, "source_revision": args.revision}
    archives = {}
    for kind in ("tar.gz", "zip"):
        archives[kind] = download(f"https://codeload.github.com/nanolathe-gg/nanolathe/{kind}/{args.revision}")
        fields["source_" + ("tar" if kind == "tar.gz" else "zip") + "_sha256"] = sha(archives[kind])
    fields["go_version"] = args.go_version
    for platform in PLATFORMS:
        os_name, arch = platform.split("-")
        file = next(f for f in release["files"] if (f["os"], f["arch"], f["kind"]) == (os_name, arch, "archive"))
        fields[f"go_{os_name}_{arch}_sha256"] = file["sha256"]
    scripts = {}
    with tarfile.open(fileobj=io.BytesIO(archives["tar.gz"])) as tar, zipfile.ZipFile(io.BytesIO(archives["zip"])) as zipped:
        for name in ("install.sh", "install.ps1"):
            repo_path = "tools/installer/" + name
            archived_path = f"nanolathe-{args.revision}/{repo_path}"
            data = tar.extractfile(archived_path).read()
            local = subprocess.check_output(["git", "-C", str(args.engine), "show", f"{args.revision}:{repo_path}"])
            if data != local or zipped.read(archived_path) != local:
                raise SystemExit(f"Archive/local source mismatch for {repo_path}")
            scripts[name] = data
            fields["installer_" + name.rsplit(".", 1)[1] + "_sha256"] = sha(data)
    # All downloads and comparisons finish before replacing any public file.
    for name, data in scripts.items():
        (ROOT / "static" / name).write_bytes(data)
    destination = ROOT / "static/install/release.txt"
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text("".join(f"{key}={value}\n" for key, value in fields.items()))
    print(f"Prepared {args.version} from {args.revision}; review, run make check, and commit to publish.")


if __name__ == "__main__":
    main()
