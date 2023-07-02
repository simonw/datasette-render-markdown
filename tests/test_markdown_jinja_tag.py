from datasette.app import Datasette
import pytest
import textwrap


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "input,expected",
    (
        (
            textwrap.dedent(
                """
        {% markdown %}
        # Data analysis with SQLite and Python
        "example" and 'example'
        {% endmarkdown %}
        """
            ).strip(),
            (
                "<h1>Data analysis with SQLite and Python</h1>\n"
                "<p>\"example\" and 'example'</p>"
            ),
        ),
        # With attributes
        (
            textwrap.dedent(
                """
            {% markdown extensions='["tables"]' extra_tags='["table", "thead", "tr", "th", "td", "tbody"]' %}
            ## Markdown table

            First Header  | Second Header
            ------------- | -------------
            Content Cell  | Content Cell
            Content Cell  | Content Cell
            {% endmarkdown %}
            """
            ).strip(),
            textwrap.dedent(
                """
            <h2>Markdown table</h2>
            <table>
            <thead>
            <tr>
            <th>First Header</th>
            <th>Second Header</th>
            </tr>
            </thead>
            <tbody>
            <tr>
            <td>Content Cell</td>
            <td>Content Cell</td>
            </tr>
            <tr>
            <td>Content Cell</td>
            <td>Content Cell</td>
            </tr>
            </tbody>
            </table>
            """
            ).strip(),
        ),
    ),
)
async def test_render_template_function(tmpdir, input, expected):
    (tmpdir / "template.html").write_text(input, "utf-8")
    datasette = Datasette(template_dir=str(tmpdir))
    await datasette.invoke_startup()
    rendered = await datasette.render_template(["template.html"])
    expected = '<div style="white-space: normal">' + expected + "</div>"
    assert rendered == expected
