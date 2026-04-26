# clippt

A command-line based presentation application (usable as a library too).

## Installation

```shell
uv tool install clippt
```

Optíonal dependencies:

```shell
uv tool install clippt[data]    # For data slides
uv tool install clippt[serve]   # Enable web server
```

## Running

```
Usage: clippt [OPTIONS] SOURCE

  Run a presentation in the command-line.

Options:
  -v, --verbose
  -s, --serve     Start a web server
  -c, --continue  Continue from last slide.
  --no-header     Disable header.
  --no-footer     Disable footer.
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
