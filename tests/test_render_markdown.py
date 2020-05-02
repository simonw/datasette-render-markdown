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


@pytest.mark.asyncio
async def test_render_template_tag(tmpdir):
    (tmpdir / "template.html").write_text(
        """
    Demo:
    {{ render_markdown("* one") }}
    Done.
    """.strip(),
        "utf-8",
    )
    datasette = Datasette([], template_dir=str(tmpdir))
    datasette.app()  # Configures Jinja
    rendered = await datasette.render_template(["template.html"])
    assert "Demo:\n    <ul>\n<li>one</li>\n</ul>\n    Done." == rendered


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
    expected = '<h1>Hello there</h1>\n<ul>\n<li><a href="https://www.example.com/" rel="nofollow">one</a>\n<em>two\n</em>three</li>\n</ul>'
    input = "# Hello there\n* [one](https://www.example.com/)\n*two\n*three"
    actual = render_cell(
        input,
        column="demo_markdown",
        table="mytable",
        database="mydatabase",
        datasette=Datasette([]),
    )
    assert expected == actual


def test_render_markdown_default_pattern_disabled_if_empty_list():
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


MARKDOWN_TABLE = """
First Header | Second Header
------------- | -------------
[Content Cell](https://www.example.com/) | Content Cell
Content Cell | Content Cell
""".strip()

RENDERED_TABLE = """
<table>
<thead>
<tr>
<th>First Header</th>
<th>Second Header</th>
</tr>
</thead>
<tbody>
<tr>
<td><a href="https://www.example.com/" rel="nofollow">Content Cell</a></td>
<td>Content Cell</td>
</tr>
<tr>
<td>Content Cell</td>
<td>Content Cell</td>
</tr>
</tbody>
</table>
""".strip()


def test_extensions():
    no_extension = render_cell(
        MARKDOWN_TABLE,
        column="body_markdown",
        table="mytable",
        database="mydatabase",
        datasette=Datasette([]),
    )
    assert (
        """
<p>First Header | Second Header
------------- | -------------
<a href="https://www.example.com/" rel="nofollow">Content Cell</a> | Content Cell
Content Cell | Content Cell</p>
    """.strip()
        == no_extension
    )
    # Now try again with the tables extension
    with_extension = render_cell(
        MARKDOWN_TABLE,
        column="body_markdown",
        table="mytable",
        database="mydatabase",
        datasette=Datasette(
            [],
            metadata={
                "plugins": {
                    "datasette-render-markdown": {
                        "extensions": ["tables"],
                        "extra_tags": ["table", "thead", "tr", "th", "td", "tbody"],
                    }
                }
            },
        ),
    )
    assert RENDERED_TABLE == with_extension


@pytest.mark.asyncio
async def test_render_template_tag_with_extensions(tmpdir):
    (tmpdir / "template.html").write_text(
        '{{ render_markdown("""'
        + MARKDOWN_TABLE
        + '""", extensions=["tables"], extra_tags=["table", "thead", "tr", "th", "td", "tbody"]) }}',
        "utf-8",
    )
    datasette = Datasette([], template_dir=str(tmpdir))
    datasette.app()  # Configures Jinja
    rendered = await datasette.render_template(["template.html"])
    assert RENDERED_TABLE == rendered
