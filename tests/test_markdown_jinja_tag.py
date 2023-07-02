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
            {% markdown extensions="tables"
                extra_tags="table thead tr th td tbody" %}
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
        # extra_attrs
        (
            textwrap.dedent(
                """
            {% markdown extra_attrs="p:id,class a:name,href" %}
            <a href="https://www.example.com/" name="namehere">Example</a>
            <p id="paragraph" class="klass">Paragraph</p>
            {% endmarkdown %}
            """
            ).strip(),
            (
                '<p><a href="https://www.example.com/" name="namehere" rel="nofollow">Example</a></p>\n'
                '<p id="paragraph" class="klass">Paragraph</p>'
            ),
        ),
        # Without that they should be stripped:
        (
            textwrap.dedent(
                """
            {% markdown %}
            <a href="https://www.example.com/" name="namehere">Example</a>
            <p id="paragraph" class="klass">Paragraph</p>
            {% endmarkdown %}
            """
            ).strip(),
            (
                '<p><a href="https://www.example.com/" rel="nofollow">Example</a></p>\n'
                "<p>Paragraph</p>"
            ),
        ),
    ),
)
async def test_render_template_tag(tmpdir, input, expected):
    (tmpdir / "template.html").write_text(input, "utf-8")
    datasette = Datasette(template_dir=str(tmpdir))
    await datasette.invoke_startup()
    rendered = await datasette.render_template(["template.html"])
    expected = '<div style="white-space: normal">' + expected + "</div>"
    assert rendered == expected


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "input,expected_error",
    (
        (
            "{% markdown %}",
            (
                "Unexpected end of template. Jinja was looking for the following tags: "
                "'endmarkdown'. The innermost block that needs to be closed is 'markdown'."
            ),
        ),
        ('{% markdown foo="bar" %}{% endmarkdown %}', "Unknown attribute 'foo'"),
    ),
)
async def test_render_template_tag_errors(tmpdir, input, expected_error):
    (tmpdir / "template.html").write_text(input, "utf-8")
    datasette = Datasette(template_dir=str(tmpdir))
    await datasette.invoke_startup()
    with pytest.raises(Exception) as excinfo:
        await datasette.render_template(["template.html"])

    error = str(excinfo.value)
    assert error == expected_error
