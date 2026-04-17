# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.0] - 2026-04-17
### Changed
- Introduce Presentation and rename the models to ...Model

## [0.1.8] - 2026-04-01

### Added
- `--serve` / `-s` flag to start a web server
- `EmptySlide` — a blank slide type with no content (just title)
- `--verbose` / `-v` CLI flag for controlling log level
- Examples are now shipped with the library (`src/clippt/examples/`)
- `Justfile` for common development tasks

## [0.1.7] - 2026-03-02

### Added
- Header showing presentation title and slide position (`N / total`)
- Basic test suite (`tests/test_app.py`, `tests/test_presentation.py`)
- New `examples/clippt/` presentation about clippt itself

### Changed
- All slide types now support titles
- A lot of internal refactoring
- Default theme changed from custom `"my"` theme to built-in `"atom-one-light"`

## [0.1.6] - 2026-02-21

### Fixed
- Shell output too narrow in the listing.

## [0.1.5] - 2026-02-20

### Added
- `execute_before` field on slides — run setup code before the main slide execution
- `Presentation.shell_cwd` — set a working directory for shell commands at the presentation level
- `--dev` flag in CLI for development/hot-reload mode

### Changed
- Slides are now Pydantic models
- Improved rendering of output and errors

## [0.1.4] - 2026-02-20

### Added
- The option to run a presentation from a Python script, from a string

## [0.1.3] - 2026-02-18

### Added
- Pydantic-based presentation model (`SlideDescription` / `Presentation`) with TOML and JSON support
- Non-executable `CodeSlide` for displaying syntax-highlighted code without running it
- Directory support in CLI — passing a directory loads `presentation.toml` inside it
- `load()` now maps file extensions to languages (`EXT_LANGUAGE_MAPPING`) and falls back to `CodeSlide` for unknown types
- Added fibonacci examples

## [0.1.2] - 2026-02-15

### Added
- Shell keyboard shortcut (`ctrl+o`)

## [0.1.1] - 2026-02-15

### Added
- Click-based CLI application (`clippt` command)
- Shell integration and support
- Example presentations
- `--continue` flag for resuming presentations
- Path support in slide definitions

### Changed
- Initial release with core slideshow functionality
