"""Verify that the public scripts and pinned release metadata stay together."""
import hashlib
from pathlib import Path
import re
import subprocess

root = Path(__file__).resolve().parents[1]
text = (root / "static/install/release.txt").read_text()
fields = {}
for line in text.splitlines():
    key, separator, value = line.partition("=")
    if not separator or key in fields or not re.fullmatch(r"[a-z_0-9]+", key):
        raise SystemExit("Malformed or duplicate release field")
    fields[key] = value
assert re.fullmatch(r"[0-9a-f]{40}", fields["source_revision"])
assert re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]{0,63}", fields["version"])
assert re.fullmatch(r"[0-9]+\.[0-9]+\.[0-9]+", fields["go_version"])
for key in ("source_tar_sha256", "source_zip_sha256", "go_darwin_amd64_sha256", "go_darwin_arm64_sha256", "go_linux_amd64_sha256", "go_linux_arm64_sha256", "go_windows_amd64_sha256", "go_windows_arm64_sha256", "installer_sh_sha256", "installer_ps1_sha256"):
    assert re.fullmatch(r"[0-9a-f]{64}", fields[key]), key
for extension in ("sh", "ps1"):
    path = root / "static" / ("install." + extension)
    assert hashlib.sha256(path.read_bytes()).hexdigest() == fields["installer_" + extension + "_sha256"], path
    assert (root / "public" / path.name).read_bytes() == path.read_bytes(), "Published installer differs"
assert (root / "public/install/release.txt").read_text() == text
subprocess.run(["bash", "-n", str(root / "static/install.sh")], check=True)
print("Installer scripts, published copies, and release checksums agree.")
