set export

_default:
    @just --list

example-zen:
    uv run clippt examples/zen_of_python

# Example with multiple languages rendering
example-fibonacci:
    uv run clippt examples/fibonacci

# Show the presentation about clippt itself
demo:
    uv run clippt examples/clippt

type-check:
    uv run ty check src

# Remove all build artifacts
clean:
    rm -rf dist

build: clean
    uv build

# Publish to PyPI
publish: build
    uv publish

test:
    uv run pytest

textual-console:
    uv run textual console -x EVENT -x SYSTEM -x DEBUG

debug arg:
    uv run textual run --dev -c clippt $arg
