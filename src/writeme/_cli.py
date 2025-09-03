"""
Command-line interface for WriteMe
@date: 03.09.2025
@author: Baptiste Pestourie
"""

from __future__ import annotations

import click


@click.command()
def writeme() -> None:
    click.echo("Welcome to WriteMe !")
