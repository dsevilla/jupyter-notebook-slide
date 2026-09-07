"""IPython magics: ``%%slide``, ``%slide_theme`` and ``%slide_types``."""

from __future__ import annotations

import shlex
from typing import Any

from . import api
from .theme import THEMES

__all__ = ["SlideMagics", "parse_options", "register_alias"]

_TRUE = {"true", "yes", "on", "1"}
_FALSE = {"false", "no", "off", "0"}
_NONE = {"none", "null", "-"}


def _coerce(value: str) -> Any:
    lowered = value.strip().lower()
    if lowered in _NONE:
        return None
    if lowered in _TRUE:
        return True
    if lowered in _FALSE:
        return False
    return value


def parse_options(line: str) -> tuple[str | None, dict[str, Any]]:
    """Split a magic line into a positional name and ``key=value`` options.

    ``"summary color=#123456 label='Where we are'"`` becomes
    ``("summary", {"color": "#123456", "label": "Where we are"})``.
    """
    tokens: list[str] = shlex.split(line.strip(), posix=True)
    name: str | None = None
    options: dict[str, Any] = {}
    for token in tokens:
        if "=" in token:
            key, _, value = token.partition("=")
            options[key.strip().replace("-", "_")] = _coerce(value)
        elif name is None:
            name = token
        else:
            raise ValueError(
                f"Unexpected argument {token!r}; expected key=value after the name"
            )
    return name, options


try:  # pragma: no cover - exercised only when IPython is installed
    from IPython.core.magic import Magics, cell_magic, line_magic, magics_class
except ImportError:  # pragma: no cover
    Magics = object  # type: ignore[assignment]

    def magics_class(cls):  # type: ignore[misc]
        return cls

    def cell_magic(name=None):  # type: ignore[misc]
        def decorator(func):
            return func

        return decorator

    line_magic = cell_magic  # type: ignore[assignment]


@magics_class
class SlideMagics(Magics):
    """The magics registered by ``%load_ext notebook_slide``."""

    @cell_magic("slide")
    def slide(self, line: str, cell: str) -> None:
        """Render the cell body as a slide.

        Usage::

            %%slide summary color=#287681 label="Where we are"
            # Heading
            - point
        """
        from IPython.display import display

        name, options = parse_options(line)
        display(api.slide(cell, type=name or "preview", **options))

    @line_magic("slide_theme")
    def slide_theme(self, line: str) -> None:
        """Select a built-in theme and/or override theme fields.

        Usage::

            %slide_theme midnight
            %slide_theme accent=#0f766e font_family="'Fira Sans', sans-serif"
            %slide_theme reset

        Prints a short summary of the resulting theme.  Use
        :func:`notebook_slide.use_theme` or :func:`notebook_slide.configure`
        when you need the :class:`~notebook_slide.theme.Theme` object back.
        """
        name, options = parse_options(line)
        if name == "reset":
            api.reset()
        elif name:
            api.use_theme(name, **options)
        elif options:
            api.configure(**options)
        theme = api.current_theme()
        print(
            f"Theme: accent={theme.accent} background={theme.background} "
            f"foreground={theme.foreground} font={theme.font_family}"
        )

    @line_magic("slide_types")
    def slide_types(self, line: str) -> None:
        """List the registered slide types and the available themes."""
        print("Slide types:")
        for name, slide_type in sorted(api.slide_types().items()):
            color = slide_type.color or api.current_theme().accent
            print(f"  {name:<12} {slide_type.label!r} {color} layout={slide_type.layout}")
        print("Themes: " + ", ".join(sorted(THEMES)))


def register_alias(name: str, ipython: Any | None = None) -> None:
    """Register an extra cell-magic name for ``%%slide``.

    Handy for notebooks written in another language::

        notebook_slide.register_alias("diapositiva")
    """
    if ipython is None:
        from IPython import get_ipython

        ipython = get_ipython()
    if ipython is None:  # pragma: no cover - outside IPython there is nothing to do
        raise RuntimeError("register_alias() must be called from inside IPython")

    def alias(line: str, cell: str) -> None:
        from IPython.display import display

        magic_name, options = parse_options(line)
        display(api.slide(cell, type=magic_name or "preview", **options))

    alias.__name__ = name
    alias.__doc__ = SlideMagics.slide.__doc__
    ipython.register_magic_function(alias, magic_kind="cell", magic_name=name)
