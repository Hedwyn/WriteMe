"""
Main interface to run shell commands

@date:03.09.2025
@author: Baptiste Pestourie
"""

from __future__ import annotations

import subprocess


def get_command_output(cmd: str) -> str:
    """
    Captures the output of `cmd` on stdout
    """
    result = subprocess.run(cmd, shell=True, capture_output=True)
    return result.stdout.decode()
