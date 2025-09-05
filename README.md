# WriteMe

`WriteMe` is a CLI tool for painless templating of README or other markdown files.
Ever been tired of copy-pasting snippets of code, command-outputs, and other dynamic-ish things for which your README itself is not the source of truth ? That's where `writeme` comes in. Create a `WRITEME.md` file, write your README template in there and let `WriteMe` autogenerate your README, so that your README is always in sync with your project.

## Not yet-another-templating-language

One of the main pain point with standard templating solutions is that they have to define their own custom syntax, which then gets plugged into some arbitrary other format (HTML, Javascript, or even C, you call it) in ways that look extremly ugly most of the time. This leads to some tangled mess in the template files themselves (which become incomprehensible by linters/LSPs, thus harder to read and check for human developers), on top of having to learn of whole new syntax solely for the templating needs.<br>
This is particularly bad for Markdown, which is format that has been designed to be fairly readable even *before* rendering, and also to be simple to use.<br>
To tackle this problem, `WriteMe` is designed as follows:

* A `WriteMe` template file is still 100% valid markdown, and your markdown LSP/linters will work properly on them. The macros used for markdown generation are always guarded in code fences, making them isolated and easy to read by design.
* There's little to no custom syntax: `WriteMe` macros are python code, which get replaced by their output after rendering.

# Status

`WriteMe` is under construction and not production-ready yet.
