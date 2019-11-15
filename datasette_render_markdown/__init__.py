import re
import bleach
import markdown
from datasette import hookimpl
import jinja2


@hookimpl()
def render_cell(value, column):
    if not isinstance(value, str):
        return None
    # Only convert to markdown if table ends in _markdown
    if not column.endswith("_markdown"):
        return None
    # Render it!
    return render_markdown(value)


def render_markdown(value):
    html = bleach.linkify(
        bleach.clean(
            markdown.markdown(value, output_format="html5"),
            tags=[
                "a",
                "abbr",
                "acronym",
                "b",
                "blockquote",
                "code",
                "em",
                "i",
                "li",
                "ol",
                "strong",
                "ul",
                "pre",
                "p",
                "h1",
                "h2",
                "h3",
                "h4",
                "h5",
                "h6",
            ],
        )
    )
    return jinja2.Markup(html)


@hookimpl
def extra_template_vars():
    return {
        "render_markdown": render_markdown,
    }
