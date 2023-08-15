from bleach.sanitizer import Cleaner
from bleach.linkifier import LinkifyFilter
from bleach.html5lib_shim import Filter
from fnmatch import fnmatch
from functools import partial
from jinja2 import nodes
from jinja2.exceptions import TemplateSyntaxError
from jinja2.ext import Extension
import json
import markdown
from datasette import hookimpl
from markupsafe import Markup


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
    if value is None:
        return Markup("")
    attributes = {"a": ["href"], "img": ["src", "alt"]}
    if extra_attrs:
        attributes.update(extra_attrs)
    cleaner = Cleaner(
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
            "img",
        ]
        + (extra_tags or []),
        attributes=attributes,
        filters=[ImageMaxWidthFilter, partial(LinkifyFilter, skip_tags={"pre"})],
    )
    html = cleaner.clean(
        markdown.markdown(value, output_format="html5", extensions=extensions or [])
    )
    return Markup('<div style="white-space: normal">{}</div>'.format(html))


class ImageMaxWidthFilter(Filter):
    """Adds style="max-width: 100%" to any image tags"""

    def __iter__(self):
        for token in Filter.__iter__(self):
            if token["type"] == "EmptyTag" and token["name"] == "img":
                token["data"][(None, "style")] = "max-width: 100%"
            yield token


@hookimpl
def extra_template_vars():
    return {
        "render_markdown": render_markdown,
    }


class MarkdownExtension(Extension):
    tags = set(["markdown"])

    def __init__(self, environment):
        super(MarkdownExtension, self).__init__(environment)

    def parse(self, parser):
        # We need this for reporting errors
        lineno = next(parser.stream).lineno

        # Gather tokens up to the next block_end ('%}')
        gathered = []
        while parser.stream.current.type != "block_end":
            gathered.append(next(parser.stream))

        # If all has gone well, we will have a sequence of triples of tokens:
        #   (type='name, value='attribute name'),
        #   (type='assign', value='='),
        #   (type='string', value='attribute value')
        # Anything else is a parse error

        if len(gathered) % 3 != 0:
            raise TemplateSyntaxError("Invalid syntax for markdown tag", lineno)
        attrs = {}
        for i in range(0, len(gathered), 3):
            if (
                gathered[i].type != "name"
                or gathered[i + 1].type != "assign"
                or gathered[i + 2].type != "string"
            ):
                raise TemplateSyntaxError(
                    (
                        "Invalid syntax for markdown attribute - got "
                        "'{}', should be name=\"value\"".format(
                            "".join([str(t.value) for t in gathered[i : i + 3]]),
                        )
                    ),
                    lineno,
                )
            attrs[gathered[i].value] = gathered[i + 2].value

        # Validate the attributes
        kwargs = {}
        for attr, value in attrs.items():
            if attr in ("extensions", "extra_tags"):
                kwargs[attr] = value.split()
            elif attr == "extra_attrs":
                # Custom syntax: tag:attr1,attr2 tag2:attr3,attr4
                extra_attrs = {}
                for tag_attrs in value.split():
                    tag, attrs = tag_attrs.split(":")
                    extra_attrs[tag] = attrs.split(",")
                kwargs["extra_attrs"] = extra_attrs
            else:
                raise TemplateSyntaxError("Unknown attribute '{}'".format(attr), lineno)

        body = parser.parse_statements(["name:endmarkdown"], drop_needle=True)

        return nodes.CallBlock(
            # I couldn't figure out how to send attrs to the _render_markdown
            # method other than json.dumps and then passing as a nodes.Const
            self.call_method("_render_markdown", [nodes.Const(json.dumps(kwargs))]),
            [],
            [],
            body,
        ).set_lineno(lineno)

    async def _render_markdown(self, kwargs_json, caller):
        kwargs = json.loads(kwargs_json)
        return render_markdown(await caller(), **kwargs)


@hookimpl
def prepare_jinja2_environment(env):
    env.add_extension(MarkdownExtension)
