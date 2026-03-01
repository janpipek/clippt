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

A presentation is defined in a source file in TOML / JSON / YAML format, to be described.

## Examples

Syntax highlighting in many languages:

```shell
uv run clippt examples/fibonacci/
```

For more, see [examples/README.md](examples/README.md).
