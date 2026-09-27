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


def test_nested_bullet_lists_preserve_indentation():
    html = markdown_to_html("- Point 1\n  - Subpoint 1.1\n- Point 2")
    assert html.count("<ul") == 2
    assert "Point 1<ul" in html
    assert "Subpoint 1.1</li></ul></li><li" in html


def test_nested_numbered_lists_preserve_indentation():
    html = markdown_to_html("1. Point 1\n   1. Subpoint 1.1\n2. Point 2")
    assert html.count("<ol") == 2
    assert "Point 1<ol" in html
    assert "Subpoint 1.1</li></ol></li><li" in html


def test_nested_lists_can_mix_markers_and_return_multiple_levels():
    html = markdown_to_html("- Point\n  1. First\n    - Detail\n  2. Second\n- Last")
    assert html.count("<ul") == 2
    assert html.count("<ol") == 1
    assert "Point<ol" in html
    assert "First<ul" in html
    assert "Detail</li></ul></li><li" in html
    assert "Second</li></ol></li><li" in html


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


def test_title_layout_centres_headings_but_left_aligns_body():
    html = slide_html("# Part two\n## Subtitle\n\n- first\n- second", type="title")
    assert html.count("text-align:center") == 2
    assert "max-width:44ch;text-align:left" in html
    assert "<ul style='margin:18px 0 8px;padding-left:30px'>" in html
    assert "border:1px solid" in html
    assert "border-radius:10px" in html
    assert "border-left:" not in html
    assert "border-right:" not in html
    assert "SECTION" not in html
    assert "Section" not in html


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


def test_bold_italic_nests_correctly():
    html = format_inline("el ***footer*** del fichero")
    assert "<strong><em>footer</em></strong>" in html
    assert "<em>" not in html.replace("<em>footer</em>", "")


def test_bold_italic_next_to_plain_bold_and_italic():
    html = format_inline("***a*** **b** *c*")
    assert "<strong><em>a</em></strong>" in html
    assert "<strong>b</strong>" in html
    assert "<em>c</em>" in html


def test_bold_italic_inside_code_is_left_alone():
    assert "***x***" in format_inline("`***x***`")


def test_consecutive_quote_lines_share_one_callout():
    html = markdown_to_html("> first line\n> second line")
    assert html.count("border-left:6px solid") == 1
    assert "first line<br>second line" in html


def test_blank_line_splits_callouts():
    html = markdown_to_html("> one\n\n> two")
    assert html.count("border-left:6px solid") == 2


def test_bare_quote_marker_starts_a_paragraph_inside_the_callout():
    html = markdown_to_html("> first\n>\n> second")
    assert html.count("border-left:6px solid") == 1
    assert "<div style='margin-top:0px'>first</div>" in html
    assert "<div style='margin-top:10px'>second</div>" in html


def test_callout_ends_at_a_list_or_paragraph():
    html = markdown_to_html("> note\n- item\n> other\nplain")
    assert html.count("border-left:6px solid") == 2
    assert html.index("note") < html.index("<ul") < html.index("other") < html.index("<p")


def test_lone_quote_marker_renders_nothing():
    assert markdown_to_html(">") == ""


def test_formatting_inside_callout():
    html = markdown_to_html("> a **bold** and *italic* `code`")
    assert "<strong>bold</strong>" in html
    assert "<em>italic</em>" in html
    assert ">code</code>" in html


def test_bold_may_contain_inline_code():
    html = format_inline("**the `Id` is not sorted**.")
    assert html.startswith("<strong>the <code")
    assert ">Id</code> is not sorted</strong>." in html
    assert "**" not in html


def test_italic_may_contain_inline_code():
    html = format_inline("*a `b` c*")
    assert html.startswith("<em>a <code") and html.endswith("c</em>")


def test_code_inside_link_text_but_not_url():
    assert "<a href='https://x.org'" in format_inline("[the `x` docs](https://x.org)")
    assert "<a" not in format_inline("[x](https://x.org/`y`)")


def test_nul_characters_cannot_forge_placeholders():
    html = format_inline("\x000\x00 `c`")
    assert html.count("<code") == 1
    assert "\x00" not in html
