from datasette_render_markdown import render_cell
from datasette.app import Datasette
import pytest


@pytest.mark.parametrize("value", [1, 1.1, b"binary"])
def test_render_cell_not_str(value):
    assert None == render_cell(
        value,
        column="demo_markdown",
        table="mytable",
        database="mydatabase",
        datasette=Datasette([]),
    )


def test_render_cell_no_markdown_suffix():
    assert None == render_cell(
        "# hello",
        column="no_suffix",
        table="mytable",
        database="mydatabase",
        datasette=Datasette([]),
    )


@pytest.mark.parametrize(
    "metadata",
    [
        # Table level
        {
            "databases": {
                "mydatabase": {
                    "tables": {
                        "mytable": {
                            "plugins": {
                                "datasette-render-markdown": {"patterns": ["*_md"],}
                            }
                        }
                    }
                }
            }
        },
        # Database level
        {
            "databases": {
                "mydatabase": {
                    "plugins": {"datasette-render-markdown": {"patterns": ["*_md"],}}
                }
            }
        },
        # Global level
        {"plugins": {"datasette-render-markdown": {"patterns": ["*_md"],}}},
    ],
)
def test_render_markdown_metadata_patterns(metadata):
    expected = "<h1>Hello there</h1>\n<ul>\n<li>one\n<em>two\n</em>three</li>\n</ul>"
    input = "# Hello there\n* one\n*two\n*three"
    actual = render_cell(
        input,
        column="demo_md",
        table="mytable",
        database="mydatabase",
        datasette=Datasette([], metadata=metadata),
    )
    assert expected == actual
    # Without metadata should not render
    assert None == render_cell(
        input,
        column="demo_md",
        table="mytable",
        database="mydatabase",
        datasette=Datasette([]),
    )


def test_render_markdown_default_pattern():
    expected = "<h1>Hello there</h1>\n<ul>\n<li>one\n<em>two\n</em>three</li>\n</ul>"
    input = "# Hello there\n* one\n*two\n*three"
    actual = render_cell(
        input,
        column="demo_markdown",
        table="mytable",
        database="mydatabase",
        datasette=Datasette([]),
    )
    assert expected == actual


def test_render_markdown_default_pattern_disabled_if_empty_listt():
    input = "# Hello there\n* one\n*two\n*three"
    assert None == render_cell(
        input,
        column="demo_markdown",
        table="mytable",
        database="mydatabase",
        datasette=Datasette(
            [], metadata={"plugins": {"datasette-render-markdown": {"patterns": []}}}
        ),
    )


@pytest.mark.parametrize(
    "metadata",
    [
        # Table level
        {
            "databases": {
                "mydatabase": {
                    "tables": {
                        "mytable": {
                            "plugins": {
                                "datasette-render-markdown": {"columns": ["body"],}
                            }
                        }
                    }
                }
            }
        },
        # Database level
        {
            "databases": {
                "mydatabase": {
                    "plugins": {"datasette-render-markdown": {"columns": ["body"],}}
                }
            }
        },
        # Global level
        {"plugins": {"datasette-render-markdown": {"columns": ["body"],}}},
    ],
)
def test_explicit_column(metadata):
    assert "<p><em>hello</em></p>" == render_cell(
        "*hello*",
        column="body",
        table="mytable",
        database="mydatabase",
        datasette=Datasette([], metadata=metadata),
    )
