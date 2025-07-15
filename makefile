.PHONY: build test dev self

build:
	cargo build

self:
	./target/debug/illiterate docs/illiterate.md docs/tests.md --dir src
	make test

check:
	find docs -name "*.md" | entr ./target/debug/illiterate docs/*.md --dir src --test

test:
	cargo test

dev:
	find docs -name "*.md" | entr bash -c "./target/debug/illiterate docs/*.md --dir src && make test"
