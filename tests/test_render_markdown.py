from datasette_render_markdown import render_cell, render_markdown, Markup
from datasette.app import Datasette
import pytest
import textwrap


@pytest.mark.parametrize("value", [1, 1.1, b"binary"])
def test_render_cell_not_str(value):
    assert (
        render_cell(
            value,
            column="demo_markdown",
            table="mytable",
            database="mydatabase",
            datasette=Datasette([]),
        )
        is None
    )


def test_render_cell_no_markdown_suffix():
    assert (
        render_cell(
            "# hello",
            column="no_suffix",
            table="mytable",
            database="mydatabase",
            datasette=Datasette([]),
        )
        is None
    )


@pytest.mark.asyncio
async def test_render_template_function(tmpdir):
    (tmpdir / "template.html").write_text(
        """
    Demo:
    {{ render_markdown("* one") }}

    With a None:
    {{ render_markdown(None) }}
    Done.
    """.strip(),
        "utf-8",
    )
    datasette = Datasette(template_dir=str(tmpdir))
    await datasette.invoke_startup()
    rendered = await datasette.render_template(["template.html"])
    assert rendered == (
        "Demo:\n"
        '    <div style="white-space: normal"><ul>\n'
        "<li>one</li>\n"
        "</ul></div>\n\n"
        "    With a None:\n"
        "    \n"
        "    Done."
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
                                "datasette-render-markdown": {
                                    "patterns": ["*_md"],
                                }
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
                    "plugins": {
                        "datasette-render-markdown": {
                            "patterns": ["*_md"],
                        }
                    }
                }
            }
        },
        # Global level
        {
            "plugins": {
                "datasette-render-markdown": {
                    "patterns": ["*_md"],
                }
            }
        },
    ],
)
def test_render_markdown_metadata_patterns(metadata):
    expected = '<div style="white-space: normal"><h1>Hello there</h1>\n<ul>\n<li>one\n<em>two\n</em>three</li>\n</ul></div>'
    input = "# Hello there\n* one\n*two\n*three"
    actual = render_cell(
        input,
        column="demo_md",
        table="mytable",
        database="mydatabase",
        datasette=Datasette(metadata=metadata),
    )
    assert expected == actual
    # Without metadata should not render
    assert (
        render_cell(
            input,
            column="demo_md",
            table="mytable",
            database="mydatabase",
            datasette=Datasette([]),
        )
        is None
    )


def test_render_markdown_default_pattern():
    expected = '<div style="white-space: normal"><h1>Hello there</h1>\n<ul>\n<li><a href="https://www.example.com/" rel="nofollow">one</a>\n<em>two\n</em>three</li>\n</ul></div>'
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
    assert (
        render_cell(
            input,
            column="demo_markdown",
            table="mytable",
            database="mydatabase",
            datasette=Datasette(
                metadata={"plugins": {"datasette-render-markdown": {"patterns": []}}}
            ),
        )
        is None
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
                                "datasette-render-markdown": {
                                    "columns": ["body"],
                                }
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
                    "plugins": {
                        "datasette-render-markdown": {
                            "columns": ["body"],
                        }
                    }
                }
            }
        },
        # Global level
        {
            "plugins": {
                "datasette-render-markdown": {
                    "columns": ["body"],
                }
            }
        },
    ],
)
def test_explicit_column(metadata):
    assert (
        '<div style="white-space: normal"><p><em>hello</em></p></div>'
        == render_cell(
            "*hello*",
            column="body",
            table="mytable",
            database="mydatabase",
            datasette=Datasette(metadata=metadata),
        )
    )


@pytest.mark.parametrize(
    "input,expected",
    (
        ("", '<div style="white-space: normal"></div>'),
        ("# Heading", '<div style="white-space: normal"><h1>Heading</h1></div>'),
        (
            "![Alt text](https://www.example.com/blah.png)",
            '<div style="white-space: normal"><p><img alt="Alt text" src="https://www.example.com/blah.png" style="max-width: 100%"></p></div>',
        ),
        (
            "[This & That](https://www.example.com/)",
            (
                '<div style="white-space: normal">'
                '<p><a href="https://www.example.com/" rel="nofollow">'
                "This &amp; That</a></p></div>"
            ),
        ),
        (None, None),
    ),
)
def test_miscellaneous_markup(input, expected):
    actual = render_cell(
        input,
        column="demo_markdown",
        table="mytable",
        database="mydatabase",
        datasette=Datasette([]),
    )
    assert actual == expected


MARKDOWN_TABLE = """
First Header | Second Header
------------- | -------------
[Content Cell](https://www.example.com/) | Content Cell
Content Cell | Content Cell
""".strip()

RENDERED_TABLE = """
<div style="white-space: normal"><table>
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
</table></div>
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
<div style="white-space: normal"><p>First Header | Second Header
------------- | -------------
<a href="https://www.example.com/" rel="nofollow">Content Cell</a> | Content Cell
Content Cell | Content Cell</p></div>
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
async def test_render_template_function_with_extensions(tmpdir):
    (tmpdir / "template.html").write_text(
        '{{ render_markdown("""'
        + MARKDOWN_TABLE
        + '""", extensions=["tables"], extra_tags=["table", "thead", "tr", "th", "td", "tbody"]) }}',
        "utf-8",
    )
    datasette = Datasette(template_dir=str(tmpdir))
    await datasette.invoke_startup()
    rendered = await datasette.render_template(["template.html"])
    assert RENDERED_TABLE == rendered


def test_render_markdown_no_linkify_inside_code_blocks():
    input = textwrap.dedent(
        """
    # Heading

    Should be URLified: datasette.name

    Should not be URLified:

        select datasette.name from datasette
    """
    )
    output = render_markdown(input)
    assert output == Markup(
        '<div style="white-space: normal"><h1>Heading</h1>\n'
        '<p>Should be URLified: <a href="http://datasette.name" rel="nofollow">datasette.name</a></p>\n'
        "<p>Should not be URLified:</p>\n"
        "<pre><code>select datasette.name from datasette\n"
        "</code></pre></div>"
    )
