import re
import bleach
from fnmatch import fnmatch
import markdown
from datasette import hookimpl
import jinja2


@hookimpl()
def render_cell(value, column, table, database, datasette):
    if not isinstance(value, str):
        return None
    should_convert = False
    config = (
        datasette.plugin_config(
            "datasette-render-markdown", database=database, table=table
        )
        or {}
    )
    if column in (config.get("columns") or []):
        should_convert = True

    # Also convert to markdown if table ends in _markdown
    patterns = config.get("patterns")
    if patterns is None:
        patterns = ["*_markdown"]
    for pattern in patterns:
        if fnmatch(column, pattern):
            should_convert = True

    if should_convert:
        return render_markdown(value)
    else:
        return None


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
