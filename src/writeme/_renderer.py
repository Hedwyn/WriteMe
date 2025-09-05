"""
Implements the rendering pipeline from WriteMe markdown files to their
final auto-generated README
"""

from __future__ import annotations

from typing import Callable, Final, Iterator, TypeVar

from mistletoe import Document
from mistletoe.block_token import CodeFence
from mistletoe.span_token import RawText
from mistletoe.token import Token

from ._commands import get_command_output

type _RenderingFunction = Callable[..., str]

type RenderingNamespace = dict[str, _RenderingFunction]

T = TypeVar("T", bound=_RenderingFunction)


class RendererNamespace:
    """
    All the functions that can be called from the top-level,
    i.e., the code blocks embedded in the markdown
    """

    def __init__(self) -> None:
        """
        Creates an emtpy namespace
        """
        self._namespace: RenderingNamespace = {}

    def register(self, func: T, overwrite_name: str | None = None) -> T:
        """
        Adds the passed function `func` to this namespace.
        Function would be declared under the same name unless `overwrite_name`
        has been passed.

        Can be used as decorator:

        @MyNamespace.register
        def func:
            ...
        """
        func_name = overwrite_name or func.__name__
        if func_name in self._namespace:
            raise ValueError(f"{func_name} already declared in namespace")

        self._namespace[func_name] = func
        return func

    def export(self) -> RenderingNamespace:
        """
        Returns
        -------
        RenderingNamespace
            A dict version of this object that can be injected in eval() or exec()
        """
        return self._namespace.copy()


_MainNamespace: Final[RendererNamespace] = RendererNamespace()


@_MainNamespace.register
def show_command_output(cmd: str) -> str:
    """
    Runs the comamnd and returns stdout
    """
    return get_command_output(cmd)


@_MainNamespace.register
def show_help_menu(cmd: str) -> str:
    """
    Small wrapper around show_command_output; queries the help menu
    """
    return get_command_output(cmd + " --help")


def evaluate_block(eval_code: str) -> str:
    """
    Calls eval() on the passed code `eval_code`.
    Injects the MainNamespace before running the evaluation.

    Returns
    -------
    str
        The output of the called function
    """
    result = eval(eval_code, _MainNamespace.export())
    return str(result)


def unwrap_tokens(root: Token) -> Iterator[Token]:
    """
    Flattens the hierarchy of mardkwon tokens and iterates over them
    in their apparition order
    """
    yield root
    children = list(root.children) if root.children else []
    for child in children:
        yield from unwrap_tokens(child)


def render_template(content: str) -> Document:
    """Parse markdown and find writeme code blocks.

    Parameters
    ----------
    content : str
        The markdown content to parse.

    Returns
    -------
    list[str]
        A list of code blocks marked with "writeme".
    """
    doc = Document(content)
    if doc.children is None:
        return doc

    current_fence: CodeFence | None = None
    for child in unwrap_tokens(doc):
        match child:
            case CodeFence():
                current_fence = child
            case RawText():
                if current_fence is None:
                    continue

                rendered = evaluate_block(child.content)
                child.content = rendered
                current_fence.language = "console"
                current_fence = None
            case _:
                continue

    return doc
