from datasette_render_markdown import render_cell
import pytest


@pytest.mark.parametrize("value", [1, 1.1, b"binary"])
def test_render_cell_not_str(value):
    assert None == render_cell(value, "demo_markdown")


def test_render_cell_no_markdown_suffix():
    assert None == render_cell("# hello", "no_suffix")


def test_render_markdown():
    expected = "<h1>Hello there</h1>\n<ul>\n<li>one\n<em>two\n</em>three</li>\n</ul>"
    input = "# Hello there\n* one\n*two\n*three"
    actual = render_cell(input, "demo_markdown")
    assert expected == actual
