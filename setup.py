from setuptools import setup
import os

VERSION = "1.3"


def get_long_description():
    with open(
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "README.md"),
        encoding="utf8",
    ) as fp:
        return fp.read()


setup(
    name="datasette-render-markdown",
    description="Datasette plugin for rendering Markdown",
    long_description=get_long_description(),
    long_description_content_type="text/markdown",
    author="Simon Willison",
    url="https://github.com/simonw/datasette-render-markdown",
    license="Apache License, Version 2.0",
    version=VERSION,
    packages=["datasette_render_markdown"],
    entry_points={"datasette": ["render_markdown = datasette_render_markdown"]},
    install_requires=["datasette", "markdown", "bleach"],
    extras_require={"test": ["pytest", "pytest-asyncio"]},
    tests_require=["datasette-render-markdown[test]"],
)
