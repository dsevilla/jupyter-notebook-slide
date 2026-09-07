import pytest

import notebook_slide as ns
from notebook_slide import Theme


def test_configure_updates_only_named_fields():
    ns.configure(accent="#0f766e")
    assert ns.current_theme().accent == "#0f766e"
    assert ns.current_theme().background == Theme().background


def test_configure_rejects_unknown_options():
    with pytest.raises(TypeError, match="Unknown theme option"):
        ns.configure(colour="#fff")


def test_use_theme_with_overrides():
    theme = ns.use_theme("midnight", font_family="'Fira Sans', sans-serif")
    assert theme.background == ns.get_theme("midnight").background
    assert theme.font_family == "'Fira Sans', sans-serif"
    assert ns.get_theme("midnight").font_family == Theme().font_family  # unchanged


def test_unknown_theme_lists_available_ones():
    with pytest.raises(KeyError, match="available themes"):
        ns.get_theme("nope")


def test_register_slide_type_and_render():
    ns.register_slide_type("demo", "Live demo", "#aa00aa")
    html = ns.slide_html("# Watch", type="demo")
    assert "Live demo" in html and "#aa00aa" in html


def test_register_slide_type_can_relabel_builtins_for_other_languages():
    ns.register_slide_type("resumen", "Recapitulación", "#287681")
    assert "Recapitulación" in ns.slide_html("# Hola", type="resumen")


def test_register_slide_type_supports_per_type_overrides():
    ns.register_slide_type("dark", "Dark", "#8ab4f8", background="#101014")
    assert "#101014" in ns.slide_html("# Hi", type="dark")
    assert ns.current_theme().background == Theme().background


def test_register_slide_type_rejects_unknown_layout():
    with pytest.raises(ValueError, match="valid layouts"):
        ns.register_slide_type("x", "X", layout="carousel")


def test_per_slide_overrides_do_not_leak():
    ns.slide_html("# Hi", color="#ff0000", background="#000000")
    assert ns.current_theme().accent == Theme().accent
    assert ns.current_theme().background == Theme().background


def test_label_override():
    assert "Where we are" in ns.slide_html("# Hi", type="summary", label="Where we are")


def test_unregister_and_reset():
    ns.unregister_slide_type("summary")
    assert "summary" not in ns.slide_types()
    ns.unregister_slide_type("summary")  # idempotent
    ns.reset()
    assert set(ns.slide_types()) == {"preview", "summary", "question", "title"}


def test_set_theme_type_check():
    with pytest.raises(TypeError):
        ns.set_theme("midnight")


def test_slide_returns_display_object():
    obj = ns.slide("# Hi")
    assert "Hi" in obj.data


def test_version_is_exposed():
    assert isinstance(ns.__version__, str) and ns.__version__


def test_per_slide_overrides_are_validated():
    with pytest.raises(TypeError, match="Unknown theme option"):
        ns.slide_html("# Hi", backgroud="#000")
