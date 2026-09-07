.PHONY: brand build check serve

brand:
	python3 scripts/package-brand.py

build: brand
	hugo --gc --minify --panicOnWarning

check: build
	python3 scripts/check-site.py

serve: brand
	hugo server
