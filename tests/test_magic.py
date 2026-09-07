import pytest

import notebook_slide as ns
from notebook_slide.magic import SlideMagics, parse_options

IPython = pytest.importorskip("IPython")


def test_parse_options_name_only():
    assert parse_options("summary") == ("summary", {})


def test_parse_options_key_values_and_quotes():
    name, options = parse_options("summary color=#123456 label='Where we are'")
    assert name == "summary"
    assert options == {"color": "#123456", "label": "Where we are"}


def test_parse_options_dashes_become_underscores_and_none_is_parsed():
    _, options = parse_options("font-url=none")
    assert options == {"font_url": None}


def test_parse_options_rejects_a_second_positional():
    with pytest.raises(ValueError, match="key=value"):
        parse_options("summary extra")


@pytest.fixture
def shell():
    from IPython.testing.globalipapp import get_ipython

    ip = get_ipython()
    ip.extension_manager.load_extension("notebook_slide")
    yield ip
    ip.extension_manager.unload_extension("notebook_slide")


def test_load_ext_registers_the_magics(shell):
    assert "slide" in shell.magics_manager.magics["cell"]
    assert "slide_theme" in shell.magics_manager.magics["line"]
    assert "slide_types" in shell.magics_manager.magics["line"]


def test_cell_magic_renders(shell, capsys):
    with pytest.MonkeyPatch.context() as mp:
        shown = []
        mp.setattr("IPython.display.display", lambda obj: shown.append(obj))
        shell.run_cell_magic("slide", "title color=#4a3f8f", "# Part two")
    assert shown and "Part two" in shown[0].data and "#4a3f8f" in shown[0].data


def test_line_magic_theme_and_reset(shell, capsys):
    shell.run_line_magic("slide_theme", "midnight")
    assert ns.current_theme().background == ns.get_theme("midnight").background
    assert "accent=" in capsys.readouterr().out
    shell.run_line_magic("slide_theme", "accent=#0f766e")
    assert ns.current_theme().accent == "#0f766e"
    shell.run_line_magic("slide_theme", "reset")
    assert ns.current_theme() == ns.Theme()


def test_line_magic_lists_types(shell, capsys):
    shell.run_line_magic("slide_types", "")
    out = capsys.readouterr().out
    assert "preview" in out and "title" in out and "midnight" in out


def test_register_alias(shell):
    ns.register_alias("diapositiva", shell)
    assert "diapositiva" in shell.magics_manager.magics["cell"]


def test_magics_class_has_the_three_magics():
    assert {"slide"} <= set(SlideMagics.magics["cell"])
    assert {"slide_theme", "slide_types"} <= set(SlideMagics.magics["line"])
