"""Rendering of the small Markdown dialect used by slides.

The dialect is deliberately tiny so a slide always fits on screen and always
renders the same way in Jupyter, Colab and VS Code:

``# title``
    Slide heading.
``## subtitle``
    Section heading inside the slide.
``- item`` / ``1. item``
    Bullet and numbered lists. Indent items to create nested lists.
``> note``
    Highlighted call-out, drawn with the slide's accent colour. Consecutive
    ``>`` lines form a single call-out, each on its own line; a bare ``>``
    line starts a new paragraph inside it.
``**bold**``, ``*italic*``, ```` `code` ````, ``[text](url)``
    Inline formatting.

Anything else becomes a paragraph.  All text is HTML-escaped first, and the
output uses inline ``style`` attributes only, since notebook viewers such as
Colab strip ``<style>`` blocks from cell output.

The same HTML may also be pasted into a Markdown cell.  Colab sanitises
Markdown more strictly than output: it drops every ``style`` attribute but
keeps legacy presentational ones (``color``, ``size``, ``noshade``,
``align``).  The slide therefore carries a fallback built from those: accent
bars drawn with ``<hr>`` elements that ``display:none`` hides wherever styles
survive, the badge in an accent ``<font>`` whose colour ``color:inherit``
cancels, the call-out as a ``<blockquote>`` and centred headings with
``align``.  The fallback never sets the text or background colour, so it stays
readable on Colab's light and dark themes.
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
# The URL may not contain a code placeholder: its HTML would break the href.
_LINK = re.compile(r"\[([^\]]+)\]\(([^)\s\x00]+)\)")
_PLACEHOLDER = re.compile(r"\x00(\d+)\x00")
_LIST_ITEM = re.compile(
    r"^(?P<indent>[ \t]*)(?:(?P<bullet>-)|(?P<number>\d+)[.)])\s+(?P<text>.*)$"
)
_SAFE_URL = re.compile(r"^(https?:|mailto:|#|/|\./|\.\./)", re.IGNORECASE)


def _attribute(value: str) -> str:
    """Escape ``value`` for a double-quoted attribute.

    Unlike ``escape(value, quote=True)`` it leaves single quotes alone, so a
    font stack such as ``'Segoe UI'`` is not lengthened to ``&#x27;Segoe UI&#x27;``.
    """
    return escape(value, quote=False).replace('"', "&quot;")


def _fold_continuation_lines(lines: list[str]) -> list[str]:
    """Join source wraps aligned with the preceding line's text."""
    folded: list[str] = []
    content_column: int | None = None

    for raw in lines:
        line = raw.strip()
        indent = len(raw[: len(raw) - len(raw.lstrip(" \t"))].expandtabs(4))
        list_match = _LIST_ITEM.match(raw)
        starts_block = (
            list_match is not None or line == ">" or line.startswith(("> ", "# ", "## "))
        )

        if folded and line and not starts_block and indent == content_column:
            folded[-1] = folded[-1].rstrip() + " " + line
            continue

        folded.append(raw)
        if not line or line == ">":
            content_column = None
        elif list_match:
            content_column = len(raw[: list_match.start("text")].expandtabs(4))
        elif line.startswith("## "):
            content_column = indent + 3
        elif line.startswith(("# ", "> ")):
            content_column = indent + 2
        else:
            content_column = indent

    return folded


def _fallback_bar(color: str, size: int) -> str:
    """Accent bar shown only where ``style`` attributes are stripped."""
    return f'<hr color="{_attribute(color)}" size="{size}" noshade style="display:none">'


def _link_replacement(match: re.Match[str], theme: Theme) -> str:
    text, url = match.group(1), match.group(2)
    if not _SAFE_URL.match(url):
        # Refuse javascript: and friends; keep the literal text instead.
        return match.group(0)
    return f"<a href='{url}' style='color:{theme.link};text-decoration:underline'>{text}</a>"


def format_inline(text: str, theme: Theme | None = None) -> str:
    """Escape ``text`` and apply inline code, bold, italic and links."""
    theme = theme or Theme()
    # Code spans are swapped for placeholders before any other formatting, so
    # their contents are never formatted while a bold or italic run may still
    # contain them (``**the `Id` column**``). Formatting each chunk between
    # code spans separately would split such a run and leave its asterisks
    # unmatched. NUL never survives in slide text and `escape` leaves it alone.
    codes: list[str] = []

    def stash(match: re.Match[str]) -> str:
        codes.append(
            f"<code style='background:{theme.code_background};"
            f"color:{theme.code_foreground};padding:2px 6px;"
            f"border-radius:4px;font-size:0.9em'>{escape(match.group(1)[1:-1])}</code>"
        )
        return f"\x00{len(codes) - 1}\x00"

    safe = escape(_CODE_SPLIT.sub(stash, text.replace("\x00", "")))
    # Bold-italic first: otherwise `***x***` would be split into a bold run
    # and a stray asterisk, producing mis-nested tags.
    safe = _BOLD_ITALIC.sub(lambda m: f"<strong><em>{m.group(1)}</em></strong>", safe)
    safe = _BOLD.sub(lambda m: f"<strong>{m.group(1)}</strong>", safe)
    safe = _ITALIC.sub(lambda m: f"<em>{m.group(1)}</em>", safe)
    safe = _LINK.sub(lambda m: _link_replacement(m, theme), safe)
    return _PLACEHOLDER.sub(lambda m: codes[int(m.group(1))], safe)


def _render_list(items: list[tuple[int, str, str]], theme: Theme) -> str:
    """Render one contiguous run of list items, preserving indentation levels."""
    html: list[str] = []
    stack: list[tuple[int, str]] = []

    def open_list(indent: int, tag: str) -> None:
        style = (
            "margin:18px 0 8px;padding-left:30px"
            if not stack
            else "margin:6px 0 2px;padding-left:28px"
        )
        html.append(f"<{tag} style='{style}'>")
        stack.append((indent, tag))

    def close_list() -> None:
        _indent, tag = stack.pop()
        html.append(f"</li></{tag}>")

    for indent, tag, item_text in items:
        while stack and indent < stack[-1][0]:
            close_list()

        if not stack or indent > stack[-1][0]:
            open_list(indent, tag)
        elif tag == stack[-1][1]:
            html.append("</li>")
        else:
            close_list()
            open_list(indent, tag)

        html.append(
            "<li style='margin:10px 0;list-style-position:outside'>"
            + format_inline(item_text, theme)
        )

    while stack:
        close_list()
    return "".join(html)


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
    list_items: list[tuple[int, str, str]] = []
    quote_lines: list[str] = []
    heading_alignment = f"text-align:{heading_align};" if heading_align else ""
    # `align` keeps the alignment where the `style` attribute is stripped.
    heading_attribute = f' align="{_attribute(heading_align)}"' if heading_align else ""

    def close_list() -> None:
        if list_items:
            blocks.append(_render_list(list_items, theme))
            list_items.clear()

    def close_quote() -> None:
        if quote_lines:
            blocks.append(_render_quote(quote_lines, theme))
            quote_lines.clear()

    for raw in _fold_continuation_lines(text.strip("\n").splitlines()):
        line = raw.strip()
        list_match = _LIST_ITEM.match(raw)
        if line == ">" or line.startswith("> "):
            # Consecutive `>` lines form a single call-out, one line each.
            close_list()
            quote_lines.append(line[2:])
            continue
        close_quote()
        if not line:
            close_list()
        elif list_match:
            indent = len(list_match.group("indent").expandtabs(4))
            tag = "ul" if list_match.group("bullet") else "ol"
            list_items.append((indent, tag, list_match.group("text")))
        else:
            close_list()
            if line.startswith("# "):
                blocks.append(
                    f'<h1{heading_attribute} style="color:{_attribute(theme.heading)};'
                    f"font-family:{_attribute(theme.headings_font)};"
                    f"font-size:{theme.heading_font_size};line-height:1.15;"
                    f'{heading_alignment}margin:0 0 22px">'
                    + format_inline(line[2:], theme)
                    + "</h1>"
                )
            elif line.startswith("## "):
                blocks.append(
                    f'<h2{heading_attribute} style="color:'
                    f"{_attribute(theme.subheading)};"
                    f"font-family:{_attribute(theme.headings_font)};"
                    f"font-size:{theme.subheading_font_size};"
                    f'{heading_alignment}margin:18px 0 8px">'
                    + format_inline(line[3:], theme)
                    + "</h2>"
                )
            else:
                blocks.append("<p style='margin:10px 0'>" + format_inline(line, theme) + "</p>")

    close_quote()
    close_list()
    return "".join(blocks)


def _render_quote(lines: list[str], theme: Theme) -> str:
    """Render one run of ``>`` lines as a single call-out.

    Each line keeps its own line in the box; a bare ``>`` line separates
    paragraphs inside it.
    """
    paragraphs: list[list[str]] = [[]]
    for line in lines:
        if line.strip():
            paragraphs[-1].append(format_inline(line, theme))
        elif paragraphs[-1]:
            paragraphs.append([])
    paragraphs = [p for p in paragraphs if p]
    if not paragraphs:
        return ""
    body = "".join(
        f"<div style='margin-top:{0 if i == 0 else 10}px'>" + "<br>".join(p) + "</div>"
        for i, p in enumerate(paragraphs)
    )
    # A blockquote, not a div, so the call-out stays set apart where styles
    # are stripped. Its margin is spelled out to override the viewer's own.
    return (
        f"<blockquote style='background:{theme.quote_background};color:inherit;"
        f"border:none;border-left:6px solid {theme.accent};"
        f"margin:22px 0 0;padding:12px 16px'>{body}</blockquote>"
    )


def _font_link(theme: Theme) -> str:
    if not theme.font_url:
        return ""
    return f'<link rel="stylesheet" href="{_attribute(theme.font_url)}">'


def _frame(content: str, theme: Theme, *declarations: str) -> str:
    """Wrap ``content`` in the slide box.

    The HTML is a single line without whitespace between tags or style
    declarations: it is usually stored in the notebook, sometimes inside a
    string literal, and indentation would only make it longer. ``declarations``
    are the layout's own additions to the shared box style.
    """
    style = ";".join(
        (
            "box-sizing:border-box",
            "width:100%",
            f"max-width:{theme.max_width}",
            f"min-height:{theme.min_height}",
            f"margin:{theme.margin}",
            f"padding:{theme.padding}",
            f"background:{theme.background}",
            f"color:{theme.foreground}",
            f"border:1px solid {theme.border}",
            *declarations,
            f"border-radius:{theme.border_radius}",
            f"font-family:{theme.font_family}",
            f"font-size:{theme.font_size}",
            f"line-height:{theme.line_height}",
            "text-align:left",
            "overflow:hidden",
        )
    )
    return f'{_font_link(theme)}<div style="{style}">{content}</div>'


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
        f'text-transform:uppercase"><font color="{_attribute(theme.accent)}" '
        f'style="color:inherit"><b>{escape(badge)}</b></font></div>'
        if badge
        else ""
    )
    return _frame(
        _fallback_bar(theme.accent, 8) + badge_html + content + _fallback_bar(theme.accent, 2),
        theme,
        f"border-top:{theme.accent_bar_width} solid {theme.accent}",
    )


def _render_title(content: str, theme: Theme) -> str:
    """Section divider with centred headings and a left-aligned body."""
    return _frame(
        _fallback_bar(theme.accent, 8)
        + f'<div style="margin:0 auto;max-width:44ch;text-align:left">{content}</div>'
        + _fallback_bar(theme.accent, 8),
        theme,
        "display:flex",
        "flex-direction:column",
        "justify-content:center",
    )
