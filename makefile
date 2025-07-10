.PHONY: build test dev self

build:
	cargo build

self:
	./target/debug/illiterate illiterate.md --dir src
	make build

check:
	echo illiterate.md | entr ./target/debug/illiterate illiterate.md --dir src --test

test:
	cargo test

dev:
	find src -name "*.rs" | entr -c cargo test
