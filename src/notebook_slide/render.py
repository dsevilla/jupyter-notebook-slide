"""Rendering of the small Markdown dialect used by slides.

The dialect is deliberately tiny so a slide always fits on screen and always
renders the same way in Jupyter, Colab and VS Code:

``# title``
    Slide heading.
``## subtitle``
    Section heading inside the slide.
``- item`` / ``1. item``
    Bullet and numbered lists.
``> note``
    Highlighted call-out, drawn with the slide's accent colour.
``**bold**``, ``*italic*``, ```` `code` ````, ``[text](url)``
    Inline formatting.

Anything else becomes a paragraph.  All text is HTML-escaped first, and the
output uses inline ``style`` attributes only, since notebook viewers such as
Colab strip ``<style>`` blocks from cell output.
"""

from __future__ import annotations

import re
from html import escape

from .theme import SlideType, Theme

__all__ = ["format_inline", "markdown_to_html", "render_slide"]

_CODE_SPLIT = re.compile(r"(`[^`]*`)")
_BOLD_ITALIC = re.compile(r"\*\*\*(.+?)\*\*\*")
_BOLD = re.compile(r"\*\*(.+?)\*\*")
_ITALIC = re.compile(r"\*(.+?)\*")
_LINK = re.compile(r"\[([^\]]+)\]\(([^)\s]+)\)")
_ORDERED_ITEM = re.compile(r"^(\d+)[.)]\s+(.*)$")
_SAFE_URL = re.compile(r"^(https?:|mailto:|#|/|\./|\.\./)", re.IGNORECASE)


def _link_replacement(match: re.Match[str], theme: Theme) -> str:
    text, url = match.group(1), match.group(2)
    if not _SAFE_URL.match(url):
        # Refuse javascript: and friends; keep the literal text instead.
        return match.group(0)
    return f"<a href='{url}' style='color:{theme.link};text-decoration:underline'>{text}</a>"


def format_inline(text: str, theme: Theme | None = None) -> str:
    """Escape ``text`` and apply inline code, bold, italic and links."""
    theme = theme or Theme()
    parts: list[str] = []
    for chunk in _CODE_SPLIT.split(text):
        if chunk.startswith("`") and chunk.endswith("`") and len(chunk) >= 2:
            code = escape(chunk[1:-1])
            parts.append(
                f"<code style='background:{theme.code_background};"
                f"color:{theme.code_foreground};padding:2px 6px;"
                f"border-radius:4px;font-size:0.9em'>{code}</code>"
            )
            continue

        safe = escape(chunk)
        # Bold-italic first: otherwise `***x***` would be split into a bold run
        # and a stray asterisk, producing mis-nested tags.
        safe = _BOLD_ITALIC.sub(lambda m: f"<strong><em>{m.group(1)}</em></strong>", safe)
        safe = _BOLD.sub(lambda m: f"<strong>{m.group(1)}</strong>", safe)
        safe = _ITALIC.sub(lambda m: f"<em>{m.group(1)}</em>", safe)
        safe = _LINK.sub(lambda m: _link_replacement(m, theme), safe)
        parts.append(safe)
    return "".join(parts)


def markdown_to_html(
    text: str,
    theme: Theme | None = None,
    *,
    heading_align: str | None = None,
) -> str:
    """Convert the slide Markdown dialect in ``text`` to an HTML fragment.

    ``heading_align`` is used by the title layout to centre headings without
    changing the alignment inherited by the rest of the slide body.
    """
    theme = theme or Theme()
    blocks: list[str] = []
    items: list[str] = []
    ordered = False
    heading_alignment = f"text-align:{heading_align};" if heading_align else ""

    def close_list() -> None:
        nonlocal ordered
        if items:
            tag = "ol" if ordered else "ul"
            blocks.append(
                f"<{tag} style='margin:18px 0 8px;padding-left:30px'>"
                + "".join(items)
                + f"</{tag}>"
            )
            items.clear()
        ordered = False

    for raw in text.strip().splitlines():
        line = raw.strip()
        ordered_match = _ORDERED_ITEM.match(line)
        if not line:
            close_list()
        elif line.startswith("- "):
            if ordered:
                close_list()
            items.append(
                "<li style='margin:10px 0'>" + format_inline(line[2:], theme) + "</li>"
            )
        elif ordered_match:
            if items and not ordered:
                close_list()
            ordered = True
            items.append(
                "<li style='margin:10px 0'>"
                + format_inline(ordered_match.group(2), theme)
                + "</li>"
            )
        else:
            close_list()
            if line.startswith("# "):
                blocks.append(
                    f'<h1 style="color:{escape(theme.heading, quote=True)};'
                    f"font-family:{escape(theme.headings_font, quote=True)};"
                    f"font-size:{theme.heading_font_size};line-height:1.15;"
                    f'{heading_alignment}margin:0 0 22px">'
                    + format_inline(line[2:], theme)
                    + "</h1>"
                )
            elif line.startswith("## "):
                blocks.append(
                    f'<h2 style="color:{escape(theme.subheading, quote=True)};'
                    f"font-family:{escape(theme.headings_font, quote=True)};"
                    f"font-size:{theme.subheading_font_size};"
                    f'{heading_alignment}margin:18px 0 8px">'
                    + format_inline(line[3:], theme)
                    + "</h2>"
                )
            elif line.startswith("> "):
                blocks.append(
                    f"<div style='background:{theme.quote_background};"
                    f"border-left:6px solid {theme.accent};"
                    "margin-top:22px;padding:12px 16px'>"
                    + format_inline(line[2:], theme)
                    + "</div>"
                )
            else:
                blocks.append("<p style='margin:10px 0'>" + format_inline(line, theme) + "</p>")

    close_list()
    return "".join(blocks)


def _font_link(theme: Theme) -> str:
    if not theme.font_url:
        return ""
    return f'<link rel="stylesheet" href="{escape(theme.font_url, quote=True)}">\n'


def render_slide(
    body: str,
    slide_type: SlideType,
    theme: Theme | None = None,
    label: str | None = None,
) -> str:
    """Render ``body`` as a self-contained slide and return its HTML.

    ``slide_type`` supplies the badge label, the accent colour and the layout;
    ``theme`` supplies everything else.  Default-layout slides render the
    badge; title-layout slides omit it.  Pass ``label`` to override the badge
    text for a default-layout slide only.
    """
    theme = slide_type.resolve_theme(theme or Theme())
    badge = label if label is not None else slide_type.label
    layout = slide_type.layout
    content = markdown_to_html(body, theme)

    if layout == "title":
        # A divider reads as one block of colour: unless the slide type says
        # otherwise, its heading takes the accent colour too.
        if "heading" not in slide_type.overrides:
            theme = theme.replace(heading=theme.accent)
        return _render_title(markdown_to_html(body, theme, heading_align="center"), theme)
    return _render_default(content, badge, theme)


def _render_default(content: str, badge: str, theme: Theme) -> str:
    badge_html = (
        f'<div style="color:{theme.accent};font-size:{theme.label_font_size};'
        "font-weight:bold;letter-spacing:1px;margin-bottom:18px;"
        f'text-transform:uppercase">{escape(badge)}</div>'
        if badge
        else ""
    )
    return f"""
{_font_link(theme)}<div style="box-sizing:border-box;width:100%;max-width:{theme.max_width};
     min-height:{theme.min_height};margin:{theme.margin};padding:{theme.padding};
     background:{theme.background};color:{theme.foreground};
     border:1px solid {theme.border};
     border-top:{theme.accent_bar_width} solid {theme.accent};
     border-radius:{theme.border_radius};font-family:{theme.font_family};
     font-size:{theme.font_size};line-height:{theme.line_height};
     text-align:left;overflow:hidden">
  {badge_html}
  {content}
</div>
"""


def _render_title(content: str, theme: Theme) -> str:
    """Section divider with centred headings and a left-aligned body."""
    return f"""
{_font_link(theme)}<div style="box-sizing:border-box;width:100%;max-width:{theme.max_width};
     min-height:{theme.min_height};margin:{theme.margin};padding:{theme.padding};
     background:{theme.background};color:{theme.foreground};
     border:1px solid {theme.border};
     border-left:{theme.accent_bar_width} solid {theme.accent};
     border-right:{theme.accent_bar_width} solid {theme.accent};
     border-radius:{theme.border_radius};font-family:{theme.font_family};
     font-size:{theme.font_size};line-height:{theme.line_height};
     display:flex;flex-direction:column;justify-content:center;
     text-align:left;overflow:hidden">
  <div style="margin:0 auto;max-width:44ch;text-align:left">{content}</div>
</div>
"""
