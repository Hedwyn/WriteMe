# WriteMe
`WriteMe` is a CLI tool for painless templating of README or other markdown files.
Ever been tired of copy-pasting snippets of code, command-outputs, and other dynamic-ish things for which your README itself is not the source of truth ? That's where `writeme` comes in. Create a `WRITEME.md` file, write your README template in there and let `WriteMe` autogenerate your README, so that your README is always in sync with your project.
## Not yet-another-templating-language
One of the main pain point with standard templating solutions is that they have to define their own custom syntax, which then gets plugged into some arbitrary other format (HTML, Javascript, or even C, you call it) in ways that look extremly ugly most of the time. This leads to some tangled mess in the template files themselves (which become incomprehensible by linters/LSPs, thus harder to read and check for human developers), on top of having to learn of whole new syntax solely for the templating needs.<br>
This is particularly bad for Markdown, which is format that has been designed to be fairly readable even *before* rendering, and also to be simple to use.<br>
To tackle this problem, `WriteMe` is designed as follows:
* A `WriteMe` template file is still 100% valid markdown, and your markdown LSP/linters will work properly on them. The macros used for markdown generation are always guarded in code fences, making them isolated and easy to read by design.
* There's little to no custom syntax: `WriteMe` macros are python code, which get replaced by their output after rendering.
## Usage
### Calling writeme from command-line
This project is self-hosted, meaning that this README is generated using WriteMe. The template file used to generate this README is located at the root of this repo, in [WRITEME.md](WRITEME.md). You can render a WriteMe template using the `writeme render` command:
```console
Welcome to WriteMe !
Usage: writeme render [OPTIONS] MARKDOWN_PATH

  Renders a WriteMe template. Formats all found `writeme` code blocks in the
  passed markdown file. Output is written the the file given by -o if passed,
  and to stdout otherwise.

Options:
  -o, --output TEXT               Path to the file to render to. If omitted,
                                  uses stdout
  -mxl, --max-line-length INTEGER
                                  Maximum line length to apply when formatting
                                  Markdown
  -norm, --normalize-whitespaces  Normalizes whitespaces
  --help                          Show this message and exit.
```
### Actually writing the template file
WriteMe generation macros should be wrapped in code fences, using the `writeme` as the language.  You can refer to WRITEME.md for examples.<br>
The syntax within the code blocks is pure Python; the function called will be replaced by its output in the rendered file. Available functions are as follows:
```python
@_MainNamespace.register
def show_source_code(import_path: str, declaration_only: bool=False, language: str='python') -> RenderingInfo:
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
    ..
```
```python
@_MainNamespace.register
def show_command_output(cmd: str) -> RenderingInfo:
    """
    Runs the command and captures stdout
    """
    ..
```
```python
@_MainNamespace.register
def show_help_menu(cmd: str) -> RenderingInfo:
    """
    Small wrapper around show_command_output; queries the help menu
    """
    ..
```
## Status
`WriteMe` is under construction and not production-ready yet.
