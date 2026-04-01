# clippt

A command-line based presentation application.

## Installation

```shell
uv tool install clippt
```

## Running

```
Usage: clippt [OPTIONS] SOURCE

Options:
  --disable-footer  Disable footer
  -c, --continue    Continue from last slide.
```

## Configuration

A presentation is defined in a source file in TOML / JSON  format. 

## Examples

```shell
uv run --with clippt python -m clippt
```

Syntax highlighting in many languages:

```shell
uv run clippt src/clippt/examples/fibonacci
```

For more, see [src/clippt/examples/README.md](src/clippt/examples/README.md).
