"""
Implements the rendering pipeline from WriteMe markdown files to their
final auto-generated README
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Final, Iterator, TypeVar

from mistletoe.block_token import CodeFence, Document
from mistletoe.span_token import RawText
from mistletoe.token import Token

from ._commands import get_command_output
from ._sourcecode import get_source_code

type _RenderingFunction = Callable[..., RenderingInfo]

type RenderingNamespace = dict[str, object]

T = TypeVar("T", bound=_RenderingFunction)


@dataclass
class Inlined:
    pass


@dataclass
class CodeLike:
    language: str = "console"


type RenderedOutputType = CodeLike | Inlined


@dataclass
class RenderingInfo:
    content: str
    type: RenderedOutputType = field(default_factory=Inlined)


class RendererNamespace:
    """
    All the functions that can be called from the top-level,
    i.e., the code blocks embedded in the markdown
    """

    def __init__(self) -> None:
        """
        Creates an emtpy namespace
        """
        self._rendering_functions: dict[str, _RenderingFunction] = {}
        self._global_vars: dict[str, object] = {}

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
        if func_name in self._rendering_functions:
            raise ValueError(f"{func_name} already declared in namespace")

        self._rendering_functions[func_name] = func
        return func

    def add_global_var(self, var_name: str, value: object) -> None:
        self._global_vars[var_name] = value

    def export(self) -> RenderingNamespace:
        """
        Returns
        -------
        RenderingNamespace
            A dict version of this object that can be injected in eval() or exec()
        """
        return {**self._global_vars, **self._rendering_functions}


_MainNamespace: Final[RendererNamespace] = RendererNamespace()


@_MainNamespace.register
def show_command_output(cmd: str) -> RenderingInfo:
    """
    Runs the command and captures stdout
    """
    return RenderingInfo(get_command_output(cmd), type=CodeLike("console"))


@_MainNamespace.register
def show_help_menu(cmd: str) -> RenderingInfo:
    """
    Small wrapper around show_command_output; queries the help menu
    """
    return RenderingInfo(get_command_output(cmd + " --help"), type=CodeLike("console"))


@_MainNamespace.register
def show_source_code(
    import_path: str,
    declaration_only: bool = False,
    language: str = "python",
) -> RenderingInfo:
    """
    Displays the source code on the object at `import_path`

    Parameters
    ----------
    obj_import_path: str
        Path to the object from which to display the source code,
        as {import_path}:func_name.

    decl_only: bool
        Only shows the function (or class declaration), removes the body
        (show ... (Ellipsis) instead)
    """
    return RenderingInfo(
        get_source_code(import_path, decl_only=declaration_only),
        type=CodeLike(language),
    )


def evaluate_block(
    eval_code: str, namespace: RendererNamespace | None = None
) -> RenderingInfo:
    """
    Calls eval() on the passed code `eval_code`.
    Injects the MainNamespace before running the evaluation.

    Returns
    -------
    str
        The output of the called function
    """
    namespace = namespace or _MainNamespace
    rendering_info = eval(eval_code, _MainNamespace.export())
    assert isinstance(rendering_info, RenderingInfo), (
        "Namespace function does not comply to expected signature"
    )
    return rendering_info


def unwrap_tokens(root: Token) -> Iterator[Token]:
    """
    Flattens the hierarchy of mardkwon tokens and iterates over them
    in their apparition order
    """
    yield root
    children = list(root.children) if root.children else []
    for child in children:
        yield from unwrap_tokens(child)


def render_template(
    content: str, namespace: RendererNamespace | None = None
) -> Document:
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
    namespace = namespace or _MainNamespace
    doc = Document(content)
    if doc.children is None:
        return doc

    namespace.add_global_var("document", doc)
    current_fence: CodeFence | None = None
    for child in unwrap_tokens(doc):
        match child:
            case CodeFence():
                current_fence = child
            case RawText():
                if current_fence is None:
                    continue

                rendered = evaluate_block(child.content)
                child.content = rendered.content
                # Note: the `language` attribute of tokens
                # is not actually used by misteloe during rendering,
                # and `info_string` is used instead...
                match rendered.type:
                    case CodeLike(language):
                        current_fence.language = language
                        current_fence.info_string = language
                current_fence = None
            case _:
                continue

    return doc
