# datasette-render-markdown

[![PyPI](https://img.shields.io/pypi/v/datasette-render-markdown.svg)](https://pypi.org/project/datasette-render-markdown/)
[![CircleCI](https://circleci.com/gh/simonw/datasette-render-markdown.svg?style=svg)](https://circleci.com/gh/simonw/datasette-render-markdown)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](https://github.com/simonw/datasette-render-markdown/blob/master/LICENSE)

Datasette plugin for rendering Markdown.

Install this plugin in the same environment as Datasette to enable this new functionality:

    pip install datasette-render-markdown

The plugin currently only works against columns with a name ending in `_markdown`.

Their contents will be rendered using [Python-Markdown](https://python-markdown.github.io/). The resulting HTML is then run through [Bleach](https://bleach.readthedocs.io/) to avoid the risk of XSS security problems.

You can try it out using the following query:

```sql
select '# Hello there

* This is a list
* of items

[And a link](https://github.com/simonw/datasette-render-markdown).'
as demo_markdown
```
