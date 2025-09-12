"""
Command-line interface for WriteMe
@date: 03.09.2025
@author: Baptiste Pestourie
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import click
from mistletoe.markdown_renderer import MarkdownRenderer

from ._renderer import render_template


@dataclass
class RenderingConfig:
    """
    Parameters that can be passed to the Markdown Renderer
    """

    max_line_length: int | None = None
    normalize_whitespaces: bool = False


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
@click.option(
    "-mxl",
    "--max-line-length",
    type=int,
    default=None,
    help="Maximum line length to apply when formatting Markdown",
)
@click.option(
    "-norm", "--normalize-whitespaces", is_flag=True, help="Normalizes whitespaces"
)
def render(
    *,
    markdown_path: str,
    output: str | None,
    max_line_length: int | None,
    normalize_whitespaces: bool,
) -> None:
    """
    Renders a WriteMe template.
    Formats all found `writeme` code blocks in the passed markdown file.
    Output is written the the file given by -o if passed,
    and to stdout otherwise.
    """
    markdown_content = Path(markdown_path).read_text()
    doc = render_template(markdown_content)
    with MarkdownRenderer(
        normalize_whitespace=normalize_whitespaces,
        max_line_length=max_line_length,  # type: ignore
    ) as renderer:
        if output is None:
            click.echo(renderer.render(doc))
            return
        with open(output, "w+") as f:
            f.write(renderer.render(doc))
            click.echo(f"Rendered to {output}")
