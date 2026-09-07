"""Public, notebook-facing API: the slide registry and its configuration."""

from __future__ import annotations

from collections.abc import Mapping

from .render import render_slide
from .theme import SlideType, Theme, default_slide_types, get_theme

__all__ = [
    "configure",
    "current_theme",
    "get_slide_type",
    "register_slide_type",
    "reset",
    "set_theme",
    "slide",
    "slide_html",
    "slide_types",
    "unregister_slide_type",
    "use_theme",
]

_theme: Theme = Theme()
_slide_types: dict[str, SlideType] = default_slide_types()


def reset() -> None:
    """Restore the default theme and the built-in slide types."""
    global _theme, _slide_types
    _theme = Theme()
    _slide_types = default_slide_types()


def current_theme() -> Theme:
    """Return the theme currently used to render slides."""
    return _theme


def set_theme(theme: Theme) -> Theme:
    """Replace the current theme wholesale and return it."""
    global _theme
    if not isinstance(theme, Theme):
        raise TypeError(f"Expected a Theme instance, got {type(theme).__name__}")
    _theme = theme
    return _theme


def use_theme(name: str, **overrides: object) -> Theme:
    """Select a built-in theme by name, optionally overriding some fields.

    >>> use_theme("midnight", font_family="'Fira Sans', sans-serif")  # doctest: +SKIP
    """
    theme = get_theme(name)
    return set_theme(theme.replace(**overrides) if overrides else theme)


def _check_theme_fields(overrides: dict) -> None:
    unknown = set(overrides) - set(Theme.__dataclass_fields__)
    if unknown:
        known = ", ".join(sorted(Theme.__dataclass_fields__))
        raise TypeError(
            f"Unknown theme option(s): {', '.join(sorted(unknown))}. Valid options: {known}"
        )


def configure(**overrides: object) -> Theme:
    """Override individual fields of the current theme.

    Every :class:`~notebook_slide.theme.Theme` field is accepted, so this is
    how you set your own palette or typography::

        configure(accent="#0f766e", font_family="'IBM Plex Sans', sans-serif",
                  font_url="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans")
    """
    if not overrides:
        return _theme
    _check_theme_fields(overrides)
    return set_theme(_theme.replace(**overrides))


def slide_types() -> Mapping[str, SlideType]:
    """Return a read-only view of the registered slide types."""
    return dict(_slide_types)


def get_slide_type(name: str) -> SlideType:
    """Look up a slide type by name.

    :raises ValueError: if the name is not registered.
    """
    key = name.strip().lower()
    try:
        return _slide_types[key]
    except KeyError:
        known = ", ".join(sorted(_slide_types))
        raise ValueError(f"Unknown slide type {name!r}; valid types: {known}") from None


def register_slide_type(
    name: str,
    label: str,
    color: str | None = None,
    layout: str = "default",
    **overrides: object,
) -> SlideType:
    """Register (or replace) a slide type and return it.

    Use it to add your own kinds of slide, or to relabel the built-in ones —
    for instance to translate them::

        register_slide_type("resumen", "Recapitulación", "#287681")
        register_slide_type("title", "Sección", "#4a3f8f", layout="title")
    """
    if layout not in {"default", "title"}:
        raise ValueError(f"Unknown layout {layout!r}; valid layouts: default, title")
    slide_type = SlideType(
        name=name.strip().lower(),
        label=label,
        color=color,
        layout=layout,
        overrides=dict(overrides),
    )
    _slide_types[slide_type.name] = slide_type
    return slide_type


def unregister_slide_type(name: str) -> None:
    """Remove a slide type. Unknown names are ignored."""
    _slide_types.pop(name.strip().lower(), None)


def slide_html(
    body: str,
    type: str = "preview",  # noqa: A002 - reads naturally at the call site
    label: str | None = None,
    color: str | None = None,
    theme: Theme | None = None,
    **overrides: object,
) -> str:
    """Render a slide and return its HTML as a string.

    ``color`` and any :class:`~notebook_slide.theme.Theme` field passed as a
    keyword apply to this slide only; the global configuration is untouched.
    """
    slide_type = get_slide_type(type)
    if color is not None:
        slide_type = slide_type.replace(color=color)
    base = theme if theme is not None else _theme
    if overrides:
        _check_theme_fields(overrides)
        base = base.replace(**overrides)
    return render_slide(body, slide_type, base, label=label)


def slide(
    body: str,
    type: str = "preview",  # noqa: A002
    label: str | None = None,
    color: str | None = None,
    theme: Theme | None = None,
    **overrides: object,
):
    """Render a slide as an :class:`IPython.display.HTML` object.

    Returning it from a cell (or passing it to ``display``) shows the slide.
    """
    from IPython.display import HTML

    return HTML(slide_html(body, type=type, label=label, color=color, theme=theme, **overrides))
