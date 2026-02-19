# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).


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
