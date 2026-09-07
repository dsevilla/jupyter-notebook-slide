import pytest

from notebook_slide import Theme, format_inline, markdown_to_html, render_slide, slide_html
from notebook_slide.theme import default_slide_types


def test_inline_escapes_html():
    assert "<script>" not in format_inline("<script>alert(1)</script>")
    assert "&lt;script&gt;" in format_inline("<script>alert(1)</script>")


def test_inline_code_bold_italic():
    html = format_inline("**bold** *italic* `code`")
    assert "<strong>bold</strong>" in html
    assert "<em>italic</em>" in html
    assert "<code" in html and ">code</code>" in html


def test_inline_code_is_not_formatted_inside_backticks():
    html = format_inline("`**not bold**`")
    assert "<strong>" not in html
    assert "**not bold**" in html


def test_links_are_rendered_and_unsafe_schemes_kept_literal():
    assert "<a href='https://example.org'" in format_inline("[site](https://example.org)")
    assert "<a" not in format_inline("[x](javascript:alert(1))")


def test_headings_lists_and_quote():
    html = markdown_to_html(
        """
# Title
## Subtitle
- one
- two

1. first
2. second

> note
""".strip()
    )
    assert "<h1" in html and "<h2" in html
    assert html.count("<ul") == 1 and html.count("<ol") == 1
    assert html.count("<li") == 4
    assert "border-left:6px solid" in html


def test_blank_line_splits_consecutive_lists():
    html = markdown_to_html("- a\n\n- b")
    assert html.count("<ul") == 2


def test_theme_colours_reach_the_output():
    theme = Theme(accent="#123456", background="#abcdef", heading="#0f0f0f")
    html = render_slide("# Hi", default_slide_types()["preview"].replace(color=None), theme)
    assert "#abcdef" in html and "#123456" in html and "#0f0f0f" in html


def test_font_family_and_url_are_configurable():
    theme = Theme(font_family="'Fira Sans', sans-serif", font_url="https://example.org/f.css")
    html = slide_html("# Hi", theme=theme)
    assert "'Fira Sans', sans-serif" in html
    assert 'href="https://example.org/f.css"' in html


def test_font_url_none_emits_no_stylesheet_link():
    assert "<link" not in slide_html("# Hi", theme=Theme(font_url=None))


def test_default_font_is_atkinson_hyperlegible():
    html = slide_html("# Hi")
    assert "Atkinson Hyperlegible" in html
    assert "fonts.googleapis.com" in html


def test_title_layout_is_centred_and_framed():
    html = slide_html("# Part two", type="title")
    assert "text-align:center" in html
    assert "border-left:10px solid" in html
    assert "SECTION" not in html  # the label is uppercased by CSS, not by us
    assert "Section" in html


def test_default_layout_is_left_aligned():
    html = slide_html("# Hi", type="preview")
    assert "text-align:left" in html


def test_unknown_slide_type_lists_valid_ones():
    with pytest.raises(ValueError, match="valid types"):
        slide_html("# Hi", type="nope")


def test_title_layout_draws_the_heading_in_the_accent_colour():
    html = slide_html("# Part two", type="title", color="#123456")
    assert "color:#123456" in html
    assert Theme().heading not in html


def test_title_layout_respects_an_explicit_heading_override():
    import notebook_slide as ns

    ns.register_slide_type("part", "Part", "#123456", layout="title", heading="#abcdef")
    assert "#abcdef" in ns.slide_html("# Part two", type="part")
