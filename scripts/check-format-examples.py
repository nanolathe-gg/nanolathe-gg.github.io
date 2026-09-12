"""Verify every authored format fixture using its generator's read-only mode."""
from pathlib import Path
import subprocess
import sys

root = Path(__file__).resolve().parents[1]
scripts = [p for p in sorted((root / 'scripts').glob('*-example.py'))
           if (root / 'content/docs' / p.name.removesuffix('-example.py') / 'index.md').exists()]
for script in scripts:
    subprocess.run([sys.executable, str(script), '--check'], cwd=root, check=True)
print(f'Checked {len(scripts)} format example generators.')
