"""Themes and slide-type definitions for :mod:`notebook_slide`.

Everything that controls the look of a slide lives here: a :class:`Theme`
holds the palette, typography and geometry shared by every slide, while a
:class:`SlideType` describes one kind of slide (its label, accent colour and
layout).  Both are plain dataclasses, so they can be copied and tweaked with
:meth:`Theme.replace` / :meth:`SlideType.replace` without mutating globals.
"""

from __future__ import annotations

import dataclasses
from collections.abc import Iterator, Mapping
from dataclasses import dataclass, field

__all__ = [
    "DEFAULT_FONT_FAMILY",
    "DEFAULT_FONT_URL",
    "SlideType",
    "Theme",
    "THEMES",
    "default_slide_types",
    "get_theme",
]

#: Font stack used unless the theme says otherwise.  Atkinson Hyperlegible is
#: a highly legible face designed for low-vision readers; the rest of the
#: stack keeps slides sane when the web font cannot be downloaded.
DEFAULT_FONT_FAMILY = (
    "'Atkinson Hyperlegible',Inter,Aptos,'Segoe UI',Helvetica,Arial,sans-serif"
)

#: Stylesheet pulled in before rendering so the default family is available.
#: Set ``font_url=None`` to render with locally installed fonts only.
DEFAULT_FONT_URL = (
    "https://fonts.googleapis.com/css2"
    "?family=Atkinson+Hyperlegible:ital,wght@0,400;0,700;1,400;1,700&display=swap"
)


@dataclass(frozen=True)
class Theme:
    """Colours, typography and geometry shared by every slide.

    All colour fields accept any CSS colour string.  Values are inlined into
    ``style`` attributes rather than emitted as a stylesheet, because Colab
    and several notebook viewers strip ``<style>`` blocks from cell output.
    """

    # Palette
    background: str = "#fff9db"
    foreground: str = "#29261d"
    border: str = "#dfcc78"
    accent: str = "#c69200"
    heading: str = "#7b2c19"
    subheading: str = "#5b5140"
    link: str = "#1b6a75"
    code_background: str = "#fff0ae"
    code_foreground: str = "#713019"
    quote_background: str = "#fff0ae"

    # Typography
    font_family: str = DEFAULT_FONT_FAMILY
    font_url: str | None = DEFAULT_FONT_URL
    font_size: str = "22px"
    line_height: str = "1.42"
    heading_font_family: str | None = None
    heading_font_size: str = "34px"
    subheading_font_size: str = "25px"
    label_font_size: str = "15px"

    # Geometry
    max_width: str = "960px"
    min_height: str = "420px"
    padding: str = "34px 46px"
    margin: str = "20px auto"
    border_radius: str = "10px"
    accent_bar_width: str = "10px"

    def replace(self, **changes: object) -> Theme:
        """Return a copy of this theme with ``changes`` applied."""
        return dataclasses.replace(self, **changes)

    @property
    def headings_font(self) -> str:
        """Font stack for headings, falling back to the body font."""
        return self.heading_font_family or self.font_family


@dataclass(frozen=True)
class SlideType:
    """One kind of slide: its name, its badge text and how it is drawn.

    ``color`` overrides :attr:`Theme.accent` for this slide type only.  A
    ``layout`` of ``"title"`` renders a centred section divider instead of the
    default left-aligned content slide.
    """

    name: str
    label: str
    color: str | None = None
    layout: str = "default"
    #: Per-slide-type theme overrides, e.g. ``{"background": "#101014"}``.
    overrides: Mapping[str, object] = field(default_factory=dict)

    def replace(self, **changes: object) -> SlideType:
        """Return a copy of this slide type with ``changes`` applied."""
        return dataclasses.replace(self, **changes)

    def resolve_theme(self, theme: Theme) -> Theme:
        """Apply this slide type's accent colour and overrides to ``theme``."""
        changes: dict[str, object] = dict(self.overrides)
        if self.color is not None:
            changes.setdefault("accent", self.color)
        return theme.replace(**changes) if changes else theme


def default_slide_types() -> dict[str, SlideType]:
    """Return a fresh mapping with the four built-in slide types."""
    types = (
        SlideType("preview", "Coming up", "#c69200"),
        SlideType("summary", "Recap", "#287681"),
        SlideType("question", "Guiding question", "#a33a2b"),
        SlideType("title", "Section", "#4a3f8f", layout="title"),
    )
    return {slide_type.name: slide_type for slide_type in types}


#: Built-in themes, selectable by name from :func:`notebook_slide.use_theme`.
THEMES: dict[str, Theme] = {
    # The original notebook palette: warm paper with an amber accent.
    "amber": Theme(),
    "slate": Theme(
        background="#f4f6f8",
        foreground="#1f2933",
        border="#cbd2d9",
        accent="#2f6f9f",
        heading="#102a43",
        subheading="#486581",
        link="#2f6f9f",
        code_background="#e4ebf1",
        code_foreground="#243b53",
        quote_background="#e4ebf1",
    ),
    "midnight": Theme(
        background="#14161c",
        foreground="#e6e8ee",
        border="#2b303b",
        accent="#8ab4f8",
        heading="#f2b8a2",
        subheading="#aab2c0",
        link="#8ab4f8",
        code_background="#232733",
        code_foreground="#f6c177",
        quote_background="#1c2029",
    ),
}


def get_theme(name: str) -> Theme:
    """Look up a built-in theme by name.

    :raises KeyError: if no theme is registered under ``name``.
    """
    try:
        return THEMES[name]
    except KeyError:
        known = ", ".join(sorted(THEMES))
        raise KeyError(f"Unknown theme {name!r}; available themes: {known}") from None


def theme_names() -> Iterator[str]:
    """Iterate over the names of the built-in themes."""
    return iter(sorted(THEMES))
