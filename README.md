# datasette-render-markdown

[![PyPI](https://img.shields.io/pypi/v/datasette-render-markdown.svg)](https://pypi.org/project/datasette-render-markdown/)
[![Changelog](https://img.shields.io/github/v/release/simonw/datasette-render-markdown?include_prereleases&label=changelog)](https://github.com/simonw/datasette-render-markdown/releases)
[![Tests](https://github.com/simonw/datasette-render-markdown/workflows/Test/badge.svg)](https://github.com/simonw/datasette-render-markdown/actions?query=workflow%3ATest)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](https://github.com/simonw/datasette-render-markdown/blob/main/LICENSE)

Datasette plugin for rendering Markdown.

## Installation

Install this plugin in the same environment as Datasette to enable this new functionality:

    $ pip install datasette-render-markdown

## Usage

You can explicitly list the columns you would like to treat as Markdown using [plugin configuration](https://datasette.readthedocs.io/en/stable/plugins.html#plugin-configuration) in a `metadata.json` file.

Add a `"datasette-render-markdown"` configuration block and use a `"columns"` key to list the columns you would like to treat as Markdown values:

```json
{
    "plugins": {
        "datasette-render-markdown": {
            "columns": ["body"]
        }
    }
}
```

This will cause any `body` column in any table to be treated as markdown and safely rendered using [Python-Markdown](https://python-markdown.github.io/). The resulting HTML is then run through [Bleach](https://bleach.readthedocs.io/) to avoid the risk of XSS security problems.

Save this to `metadata.json` and run Datasette with the `--metadata` flag to load this configuration:

    $ datasette serve mydata.db --metadata metadata.json

The configuration block can be used at the top level, or it can be applied just to specific databases or tables. Here's how to apply it to just the `entries` table in the `news.db` database:

```json
{
    "databases": {
        "news": {
            "tables": {
                "entries": {
                    "plugins": {
                        "datasette-render-markdown": {
                            "columns": ["body"]
                        }
                    }
                }
            }
        }
    }
}
```

And here's how to apply it to every `body` column in every table in the `news.db` database:

```json
{
    "databases": {
        "news": {
            "plugins": {
                "datasette-render-markdown": {
                    "columns": ["body"]
                }
            }
        }
    }
}
```

## Columns that match a naming convention

This plugin can also render markdown in any columns that match a specific naming convention.

By default, columns that have a name ending in `_markdown` will be rendered.

You can try this out using the following query:

```sql
select '# Hello there

* This is a list
* of items

[And a link](https://github.com/simonw/datasette-render-markdown).'
as demo_markdown
```

You can configure a different list of wildcard patterns using the `"patterns"` configuration key. Here's how to render columns that end in either `_markdown` or `_md`:

```json
{
    "plugins": {
        "datasette-render-markdown": {
            "patterns": ["*_markdown", "*_md"]
        }
    }
}
```

To disable wildcard column matching entirely, set `"patterns": []` in your plugin metadata configuration.

## Markdown extensions

The [Python-Markdown library](https://python-markdown.github.io/) that powers this plugin supports extensions, both [bundled](https://python-markdown.github.io/extensions/) and [third-party](https://github.com/Python-Markdown/markdown/wiki/Third-Party-Extensions). These can be used to enable additional Markdown features such as [table support](https://python-markdown.github.io/extensions/tables/).

You can configure support for extensions using the `"extensions"` key in your plugin metadata configuration.

Since extensions may introduce new HTML tags, you will also need to add those tags to the list of tags that are allowed by the [Bleach](https://bleach.readthedocs.io/) sanitizer. You can do that using the `"extra_tags"` key, and you can whitelist additional HTML attributes using `"extra_attrs"`. See [the Bleach documentation](https://bleach.readthedocs.io/en/latest/clean.html#allowed-tags-tags) for more information on this.

Here's how to enable support for [Markdown tables](https://python-markdown.github.io/extensions/tables/):

```json
{
    "plugins": {
        "datasette-render-markdown": {
            "extensions": ["tables"],
            "extra_tags": ["table", "thead", "tr", "th", "td", "tbody"],
        }
    }
}
```

### GitHub-Flavored Markdown

Enabling [GitHub-Flavored Markdown](https://help.github.com/en/github/writing-on-github) (useful for if you are working with data imported from GitHub using [github-to-sqlite](https://github.com/dogsheep/github-to-sqlite)) is a little more complicated.

First, you will need to install the [py-gfm](https://py-gfm.readthedocs.io) package:

    $ pip install py-gfm

Note that `py-gfm` has [a bug](https://github.com/Zopieux/py-gfm/issues/13) that causes it to pin to `Markdown<3.0` - so if you are using it you should install it _before_ installing `datasette-render-markdown` to ensure you get a compatibly version of that dependency.

Now you can configure it like this. Note that the extension name is `mdx_gfm:GithubFlavoredMarkdownExtension` and you need to whitelist several extra HTML tags and attributes:

```json
{
    "plugins": {
        "datasette-render-markdown": {
            "extra_tags": [
                "hr",
                "br",
                "details",
                "summary",
                "input"
            ],
            "extra_attrs": {
                "input": [
                    "type",
                    "disabled",
                    "checked"
                ],
            },
            "extensions": [
                "mdx_gfm:GithubFlavoredMarkdownExtension"
            ]
        }
    }
}
```

The `<input type="" checked disabled>` attributes are needed to support rendering checkboxes in issue descriptions.

## Markdown in templates

The plugin also adds a new template function: `render_markdown(value)`. You can use this in your templates like so:

```html+jinja
{{ render_markdown("""
# This is markdown

* One
* Two
* Three
""") }}
```

You can load additional extensions and whitelist tags by passing extra arguments to the function like this:

```html+jinja
{{ render_markdown("""
## Markdown table

First Header  | Second Header
------------- | -------------
Content Cell  | Content Cell
Content Cell  | Content Cell
""", extensions=["tables"],
    extra_tags=["table", "thead", "tr", "th", "td", "tbody"])) }}
```
