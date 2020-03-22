# datasette-render-markdown

[![PyPI](https://img.shields.io/pypi/v/datasette-render-markdown.svg)](https://pypi.org/project/datasette-render-markdown/)
[![CircleCI](https://circleci.com/gh/simonw/datasette-render-markdown.svg?style=svg)](https://circleci.com/gh/simonw/datasette-render-markdown)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](https://github.com/simonw/datasette-render-markdown/blob/master/LICENSE)

Datasette plugin for rendering Markdown.

## Installation

Install this plugin in the same environment as Datasette to enable this new functionality:

    pip install datasette-render-markdown

## Usage

You can explicitly list the columns you would like to treat as markdown using [plugin configuration](https://datasette.readthedocs.io/en/stable/plugins.html#plugin-configuration) in a `metadata.json` file.

Add a `"datasette-render-markdown"` configuration block and use a `"columns"` key to list the columns you would like to treat as markdown values:

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

Save this to `metadata.json` and run datasette with the `--metadata` flag to load this configuration:

    datasette serve mydata.db --metadata metadata.json

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

## Column patterns

The plugin also against any columns with a name ending in `_markdown`.

You can try it out using the following query:

```sql
select '# Hello there

* This is a list
* of items

[And a link](https://github.com/simonw/datasette-render-markdown).'
as demo_markdown
```

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
