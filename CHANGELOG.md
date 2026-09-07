# Changelog

All notable changes to this project are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and the project uses
[Semantic Versioning](https://semver.org/).

## [Unreleased]

## [0.1.0] - 2026-09-07

First packaged release, extracted from the inline `%%diapositiva` magic used in
the BDGE course notebooks and translated to English.

### Added

- `%%slide` cell magic, loaded with `%load_ext notebook_slide`.
- Four slide types: `preview`, `summary`, `question` and the new `title`
  section divider, which renders centred and framed on both sides.
- Fully configurable `Theme`: palette, typography (including `font_family` and
  `font_url`, so any local or web font can be used) and geometry.
- Built-in themes `amber` (the original palette, default), `slate` and
  `midnight`.
- `%slide_theme` and `%slide_types` line magics.
- `register_slide_type()` for custom or translated slide types, with per-type
  theme overrides, and `register_alias()` for extra magic names such as
  `%%diapositiva`.
- Per-slide overrides on the magic line (`%%slide summary color=#287681`).
- Markdown dialect: headings, bullet and numbered lists, call-outs, bold,
  italic, inline code and links, with HTML escaping throughout.
- Python API (`slide`, `slide_html`, `markdown_to_html`, `format_inline`) for
  use outside notebooks.

[Unreleased]: https://github.com/dsevilla/jupyter-notebook-slide/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/dsevilla/jupyter-notebook-slide/releases/tag/v0.1.0
