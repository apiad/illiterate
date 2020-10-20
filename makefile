.PHONY: build
build:
	illiterate illiterate docs --copy Readme.md:index.md --inline

.PHONY: publish
publish:
	poetry publish --build

.PHONY: docs
docs:
	mkdocs gh-deploy
