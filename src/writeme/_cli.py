"""
Command-line interface for WriteMe
@date: 03.09.2025
@author: Baptiste Pestourie
"""

from __future__ import annotations

from pathlib import Path

import click
from mistletoe.markdown_renderer import MarkdownRenderer

from ._renderer import render_template


@click.group()
def writeme() -> None:
    click.echo("Welcome to WriteMe !")


@writeme.command()
@click.argument("markdown_path", type=str)
@click.option(
    "-o",
    "--output",
    type=str,
    default=None,
    help="Path to the file to render to. If omitted, uses stdout",
)
def render(markdown_path: str, output: str | None) -> None:
    """
    Shows all found `writeme` code blocks in the passed markdown file.
    """
    markdown_content = Path(markdown_path).read_text()
    doc = render_template(markdown_content)
    with MarkdownRenderer() as renderer:
        if output is None:
            click.echo(renderer.render(doc))
            return
        with open(output, "w+") as f:
            f.write(renderer.render(doc))
            click.echo(f"Rendered to {output}")
