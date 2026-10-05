.PHONY: brand play build check check-mods-remote serve

brand:
	python3 scripts/package-brand.py

# The engine's latest immutable browser release and the pinned demo assets (README,
# "Browser build"). Network failures fall back to the live build or a
# placeholder unless PLAY_REQUIRED=1.
play:
	python3 scripts/fetch-play.py
	python3 scripts/style-play.py

# public/ is generated: clean it so retired hashed browser files do not linger.
build: brand play
	hugo --gc --minify --panicOnWarning --cleanDestinationDir

check: build
	python3 scripts/check-site.py
	@if command -v node >/dev/null 2>&1; then node scripts/test-platform.cjs; else echo "Node unavailable; browser platform unit checks skipped."; fi
	@if command -v node >/dev/null 2>&1; then node scripts/test-browser-play.cjs; else echo "Node unavailable; browser demo unit checks skipped."; fi
	python3 scripts/check-play.py
	python3 scripts/test-play.py
	python3 scripts/check-format-examples.py
	python3 scripts/check-installers.py
	python3 scripts/check-mods.py
	python3 scripts/check-maps.py
	python3 scripts/test-fetch-play.py
	python3 scripts/test-package-mod.py
	python3 scripts/test-package-multipart.py
	python3 scripts/test-installers.py
	@if command -v pwsh >/dev/null 2>&1; then pwsh -NoProfile -File scripts/test-installers.ps1; else echo "PowerShell unavailable; Windows offline tests skipped."; fi

check-mods-remote: build
	python3 scripts/check-mods.py --remote

serve: brand play
	hugo server
