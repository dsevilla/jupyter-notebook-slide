"""Self-contained HTML slides inside notebook cells.

Load the extension and write a slide::

    %load_ext notebook_slide

    %%slide preview
    # What this session covers
    - Read the data
    - Convert it
    > Moving less data is usually the first big optimisation.

Everything renders as inline-styled HTML, with no JavaScript and no frontend
extension, so the same notebook works in Jupyter, Colab and VS Code.
"""

from __future__ import annotations

from .api import (
    configure,
    current_theme,
    get_slide_type,
    register_slide_type,
    reset,
    set_theme,
    slide,
    slide_html,
    slide_types,
    unregister_slide_type,
    use_theme,
)
from .magic import SlideMagics, register_alias
from .render import format_inline, markdown_to_html, render_slide
from .theme import (
    DEFAULT_FONT_FAMILY,
    DEFAULT_FONT_URL,
    THEMES,
    SlideType,
    Theme,
    get_theme,
)

try:  # pragma: no cover - trivial
    from importlib.metadata import PackageNotFoundError, version

    __version__ = version("jupyter-notebook-slide")
except PackageNotFoundError:  # pragma: no cover - running from a source tree
    __version__ = "0.0.0.dev0"

__all__ = [
    "DEFAULT_FONT_FAMILY",
    "DEFAULT_FONT_URL",
    "SlideMagics",
    "SlideType",
    "THEMES",
    "Theme",
    "__version__",
    "configure",
    "current_theme",
    "format_inline",
    "get_slide_type",
    "get_theme",
    "load_ipython_extension",
    "markdown_to_html",
    "register_alias",
    "register_slide_type",
    "render_slide",
    "reset",
    "set_theme",
    "slide",
    "slide_html",
    "slide_types",
    "unregister_slide_type",
    "use_theme",
]


def load_ipython_extension(ipython) -> None:
    """Entry point for ``%load_ext notebook_slide``."""
    ipython.register_magics(SlideMagics)


def unload_ipython_extension(ipython) -> None:  # pragma: no cover - rarely used
    """Entry point for ``%unload_ext notebook_slide``."""
    for kind, names in (("cell", ("slide",)), ("line", ("slide_theme", "slide_types"))):
        for name in names:
            ipython.magics_manager.magics[kind].pop(name, None)
