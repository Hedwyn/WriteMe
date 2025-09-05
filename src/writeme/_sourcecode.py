"""
Extraction of source code.

@date: 05.09.2025
@author: Baptiste Pestourie
"""

from __future__ import annotations

import inspect
import importlib


def get_source_code(obj_import_path: str) -> str:
    """
    Parameters
    ----------
    obj_import_path: str
        Path to the object from which to display the source code,
        as {import_path}:func_name.
    """
    try:
        mod_path, func_name = obj_import_path.split(":")
    except ValueError as exc:
        raise ValueError(
            f"Import path should be passed as mod_a.mod_b:func_name, got {obj_import_path}"
        ) from exc

    try:
        mod = importlib.import_module(mod_path)
    except ImportError as exc:
        raise ImportError(
            f"Failed to import {mod_path}. Is the module installed in your environement ?"
        ) from exc

    try:
        obj = getattr(mod, func_name)
    except AttributeError as exc:
        raise ImportError(
            f"Failed to import {func_name} from {mod_path}.Is the module installed in your environement ?"
        ) from exc

    return inspect.getsource(obj)
