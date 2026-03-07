set export

example-zen:
    uv run clippt examples/zen_of_python

example-fibonacci:
    uv run clippt examples/fibonacci

demo:
    uv run clippt examples/clippt

type-check:
    uv run ty check src

clean:
    rm -rf dist

build: clean
    uv build

publish: build
    uv publish

test:
    uv run pytest

textual-console:
    uv run textual console -x EVENT -x SYSTEM -x DEBUG

debug arg:
    uv run textual run --dev -c clippt $arg
