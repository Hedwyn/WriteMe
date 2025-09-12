"""
Extraction of source code.

@date: 05.09.2025
@author: Baptiste Pestourie
"""

from __future__ import annotations

import ast
import importlib
import inspect
from ast import (
    AsyncFunctionDef,
    ClassDef,
    Constant,
    Expr,
    FunctionDef,
    fix_missing_locations,
)


def get_source_code(obj_import_path: str, *, decl_only: bool = False) -> str:
    """
    Parameters
    ----------
    obj_import_path: str
        Path to the object from which to display the source code,
        as {import_path}:func_name.

    decl_only: bool
        Only shows the function (or class declaration), removes the body
        (show ... (Ellipsis) instead)
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
    source_code = inspect.getsource(obj)
    if not decl_only:
        return source_code
    ast_nodes = ast.parse(source_code)
    if not ast_nodes.body:
        raise ValueError("Empty object body")
    head = ast_nodes.body[0]

    if not isinstance(head, (FunctionDef, AsyncFunctionDef, ClassDef)):
        raise TypeError(
            f"Cannot trim source code for {source_code}, "
            "only functions and classes are supported"
        )
    return ast.unparse(remove_cls_or_func_body(head))


def remove_cls_or_func_body(node: FunctionDef | AsyncFunctionDef | ClassDef) -> ast.AST:
    """
    Given an AST FunctionDef, AsyncFunctionDef, or ClassDef,
    return a new AST node with only declaration, docstring, and `...` as the body.
    """

    # Extract docstring as an AST Expr(Constant(...)) if it exists
    docstring = ast.get_docstring(node, clean=False)
    new_body = [Expr(Constant(Ellipsis))]
    if docstring is not None:
        new_body.insert(0, Expr(Constant(docstring)))

    # Reconstruct node with same header/decorators but new body
    match node:
        case FunctionDef() | AsyncFunctionDef() as func:
            new_node = type(func)(  # type: ignore
                name=func.name,
                args=func.args,
                body=new_body,
                decorator_list=func.decorator_list,
                returns=func.returns,
                type_comment=func.type_comment,
            )
        case ClassDef() as klass:
            new_node = ClassDef(
                name=klass.name,
                bases=klass.bases,
                keywords=klass.keywords,
                body=new_body,  # type: ignore
                decorator_list=klass.decorator_list,
            )

    return fix_missing_locations(new_node)
