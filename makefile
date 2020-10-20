build:
	illiterate illiterate docs --copy Readme.md:index.md --inline

publish:
	poetry publish --build