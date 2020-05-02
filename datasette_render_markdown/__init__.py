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
    extensions = config.get("extensions") or []
    extra_tags = config.get("extra_tags") or []
    extra_attrs = config.get("extra_attrs") or {}
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
        return render_markdown(value, extensions, extra_tags, extra_attrs)
    else:
        return None


def render_markdown(value, extensions=None, extra_tags=None, extra_attrs=None):
    attributes = {"a": ["href"]}
    if extra_attrs:
        attributes.update(extra_attrs)
    html = bleach.linkify(
        bleach.clean(
            markdown.markdown(
                value, output_format="html5", extensions=extensions or []
            ),
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
            ]
            + (extra_tags or []),
            attributes=attributes,
        )
    )
    return jinja2.Markup(html)


@hookimpl
def extra_template_vars():
    return {
        "render_markdown": render_markdown,
    }
