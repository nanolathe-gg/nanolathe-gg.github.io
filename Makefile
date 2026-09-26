.PHONY: brand build check check-mods-remote serve

brand:
	python3 scripts/package-brand.py

build: brand
	hugo --gc --minify --panicOnWarning

check: build
	python3 scripts/check-site.py
	python3 scripts/check-format-examples.py
	python3 scripts/check-installers.py
	python3 scripts/check-mods.py
	python3 scripts/test-package-multipart.py
	python3 scripts/test-installers.py
	@if command -v pwsh >/dev/null 2>&1; then pwsh -NoProfile -File scripts/test-installers.ps1; else echo "PowerShell unavailable; Windows offline tests skipped."; fi

check-mods-remote: build
	python3 scripts/check-mods.py --remote

serve: brand
	hugo server
