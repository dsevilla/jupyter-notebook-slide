# Changelog

All notable changes to this project are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and the project uses
[Semantic Versioning](https://semver.org/).

## [Unreleased]

## [0.1.6] - 2026-09-27

### Changed

- Consecutive `>` lines now form a single call-out, each line on its own line
  inside the box, instead of one box per line. A bare `>` line starts a new
  paragraph within the same call-out; a blank line still ends it.

### Fixed

- Bold and italic runs that contain inline code (``**the `Id` column**``) now
  render. Inline formatting used to be applied separately to the text on each
  side of a code span, which left the asterisks unmatched and visible.

## [0.1.5] - 2026-09-11

### Fixed

- Title slides no longer draw solid accent-coloured side borders, avoiding
  visible seams and mismatched colours where gradient backgrounds meet the
  rounded corners.

## [0.1.4] - 2026-09-11

### Changed

- Removed the unused `nbformat` development dependency.

## [0.1.3] - 2026-09-11

### Added

- Bullet and numbered lists can now be nested using indentation, including
  lists that mix both marker styles at different levels.

### Fixed

- Leading spaces in list items are no longer discarded, so nested items render
  inside their parent item instead of appearing as flat siblings.

## [0.1.2] - 2026-09-08

### Changed

- Title slides no longer show a section badge; headings remain centred while
  their body content is left-aligned.
- The README now points at the current `v0.1.2` release.

### Added

- GitHub Actions now creates a `v<version>` tag and GitHub release when the
  project version changes on `main`.

## [0.1.1] - 2026-09-07

### Fixed

- `***bold italic***` now renders as `<strong><em>…</em></strong>`. It used to
  be split into a bold run plus a stray asterisk, which produced mis-nested
  tags (`<strong><em>x</strong></em>`).

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

[Unreleased]: https://github.com/dsevilla/jupyter-notebook-slide/compare/v0.1.5...HEAD
[0.1.5]: https://github.com/dsevilla/jupyter-notebook-slide/compare/v0.1.4...v0.1.5
[0.1.4]: https://github.com/dsevilla/jupyter-notebook-slide/compare/v0.1.3...v0.1.4
[0.1.3]: https://github.com/dsevilla/jupyter-notebook-slide/compare/v0.1.2...v0.1.3
[0.1.2]: https://github.com/dsevilla/jupyter-notebook-slide/compare/v0.1.1...v0.1.2
[0.1.1]: https://github.com/dsevilla/jupyter-notebook-slide/compare/v0.1.0...v0.1.1
[0.1.0]: https://github.com/dsevilla/jupyter-notebook-slide/releases/tag/v0.1.0
