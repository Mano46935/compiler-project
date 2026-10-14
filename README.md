# Text2Web — Review 1 prototype

Text2Web compiles a small controlled-English language into actual `index.html`
and `style.css` files. This milestone demonstrates a real Lark LALR parser, an
AST, a symbol table, basic reference resolution, and deterministic code generation.
It is a foundation for the full project, not a claim that 30% of every requirement
is complete. Layout checking, full semantics, accessibility validation, and
optimization are not implemented.

## Run on this machine

Open PowerShell in `C:\Users\abhis\OneDrive\Desktop\compiler`.
The approved project-local environment is already installed. No activation is needed:

```powershell
.\.venv\Scripts\python.exe app.py
```

Open <http://127.0.0.1:5000>, then select **Build page**. Stop the server with
Ctrl+C. This is a local development application, not a deployed production service.

To compile the demonstration from the command line:

```powershell
.\.venv\Scripts\python.exe -m text2web examples\fest.sp --output build\fest --debug --force
Start-Process .\build\fest\index.html
```

`--debug` displays normalized input, tokens, the AST, and the symbol table.
`--force` explicitly replaces `index.html` and `style.css` in the selected folder;
omit it to protect existing output. Other files are not replaced. The generated
files work together in an ordinary browser without Flask. Buttons have no behavior.

Run tests:

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```

For a fresh environment, after approving installation:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-lock.txt
```

On this machine, if `python` resolves to an unusable Windows Store alias, use:

```powershell
& "$env:LOCALAPPDATA\Python\pythoncore-3.14-64\python.exe" -m venv .venv
```

`requirements.txt` records supported dependency ranges; `requirements-lock.txt`
records the versions installed for this review. Python 3.14.3 was used for validation.

## Supported language

Write one instruction per nonblank line. Start with exactly one page declaration.
Blank lines are allowed and still count toward source line numbers. The terminal
full stop is optional. Double-quoted text uses JSON escapes such as `\"`, `\\`,
and `\n`; literal multiline strings are not supported.

```text
Create a page titled "Techno Fest".
Add a big heading that says "Techno 2026".
Add a paragraph that says "Welcome to our college fest".
Add a blue button that says "Register".
Make it bold.
```

| Pattern | Meaning |
| --- | --- |
| `Create a page titled "Title".` | Set the document's browser-tab title |
| `Add a heading that says "Text".` | Add an `h1` |
| `Add a paragraph that says "Text".` | Add a `p` |
| `Add a button that says "Text".` | Add a visual-only `button` |
| `Make it bold.` / `Make this bold.` | Set the last introduced element's font weight |

- `add`, `create`, and `insert` are equivalent after normalization.
- Keywords are case-insensitive; quoted text keeps its case, spaces, and punctuation.
- `please` can prefix an instruction. `a` or `the` can precede a page or element.
  `that` before `says` is optional. These words remain grammar tokens rather than
  being removed globally, which avoids changing quoted content.
- Elements optionally accept size **then** color:
  `Insert a small green paragraph that says "Hello".`
- Sizes: `small` = `0.875rem`, `medium` = `1.125rem`, `big` = `2.5rem`.
- Colors: `blue`, `red`, `green`, `black`, `white`.
- Color means text color for headings/paragraphs and background color for buttons.
  Buttons use preset foreground colors. No contrast calculation is performed.
- The page declaration is not an eligible reference target. `it`/`this` selects
  the most recently **introduced** heading, paragraph, or button. Repeated formatting
  keeps targeting that element; missing targets produce errors.
- No arbitrary CSS values, images, layout instructions, named references, comments,
  JavaScript, forms, databases, or multiple instructions per line are accepted.

The quoted text is preserved in the AST and escaped for HTML. Normal browser
whitespace rules still apply to titles, headings, and buttons; paragraphs use
`white-space: pre-wrap`.

## Compiler design mapping and progress

| PDF stage / concept | Review 1 implementation | Remaining work |
| --- | --- | --- |
| 1. Input and normalization | Original source lines; keyword case folding and synonyms; quoted text preservation | Broader controlled wording |
| 2. Lexical analysis | Lark lexer; visible token types, values, and original line numbers | Additional vocabulary |
| 3. Syntax analysis | EBNF-style Lark grammar, LALR parsing, statement AST | Broader grammar and sentence-boundary recovery |
| 4. Reference resolution | Symbol records with IDs, types, text, properties, source lines; resolved AST IDs | Named targets and richer resolution rules |
| 5. Layout constraints | Not implemented | Directed constraints, cycle detection, conflicting source lines |
| 6. Type/accessibility checks | Basic page structure and missing-reference diagnostics only | Property/type rules, image descriptions, contrast checks |
| 7. IR and optimization | AST and symbol records are independent of HTML; no dedicated page-tree IR or optimizer | Container/page IR, style merging, unused-style removal, safe dead-store elimination |
| 8. Code generation | Escaped deterministic static HTML/CSS for the subset | Layout-aware generation |
| Error reporting | Original line numbers; independent syntax errors collected by line; no output on blocking errors | Comprehensive recovery across compiler phases |
| Interface | Flask editor, status/errors, sandboxed preview, HTML/CSS downloads, phase inspector | Broader sentence guide and later-phase inspection |

Normalization uses regular expressions only to preserve strings and normalize
words. **Lark's grammar and LALR parser decide whether a sentence is valid**.
The parser's structured tree is converted to explicit `Statement` records.
Resolved `Element` records are the symbol table and feed the minimal generator.
They do not yet implement the PDF's hierarchical page-tree IR.

If any line has a syntax error, parsing continues on other lines but semantic
resolution and generation are skipped. This prevents an invalid declaration from
silently changing what `it` means. If semantic checks fail, no HTML/CSS is generated.
Previously successful builds are retained, but the UI does not show them as the
result of a failed attempt. Disk failures are reported separately; writing two
files is not an atomic filesystem transaction.

## Files created

The workspace was empty before implementation; no existing project files were changed.

| Files | Responsibility |
| --- | --- |
| `text2web/__init__.py`, `compiler.py` | Public compiler entry point and phase orchestration |
| `text2web/model.py` | Sentences, AST statements, symbols, diagnostics, result records |
| `text2web/normalizer.py` | Quote-preserving normalization and original line tracking |
| `text2web/grammar.lark`, `parser.py` | Formal grammar, Lark lexer/LALR parser, AST construction |
| `text2web/semantics.py` | Basic page rules, symbol table, `it`/`this` resolution |
| `text2web/codegen.py` | HTML/CSS generation and guarded output writing |
| `text2web/__main__.py` | Command-line entry point |
| `app.py`, `templates/index.html`, `static/app.css`, `static/app.js` | Flask editor, inspector, responsive preview, file downloads, writing-guide toggle and line count |
| `examples/fest.sp`, `examples/invalid.sp` | Successful and failing review demonstrations |
| `tests/test_compiler.py`, `tests/test_web.py`, `pytest.ini` | Compiler, CLI, and Flask integration checks |
| `requirements.txt`, `requirements-lock.txt`, `.gitignore` | Dependencies and generated-file exclusions |
| `README.md`, `docs/REVIEW1_DEMO.md`, `docs/VALIDATION.md` | Run instructions, presentation script, actual verification results |
| `build/fest/index.html`, `build/fest/style.css` | Generated demonstration artifacts |

The `.venv` directory contains the approved local dependencies. Flask saves each
successful compilation under `build/web/<build-id>/`. Build history has no automatic
cleanup in this milestone.

## Review and next milestone

See [the short demonstration script](docs/REVIEW1_DEMO.md) and
[actual verification results](docs/VALIDATION.md).

For Review 2, extend the grammar with images and explicit targets, introduce a
hierarchical page-tree IR, and add property/type and missing-description checks.
Then implement axis-aware layout constraints with cycle diagnostics and simple
rows/columns. Contrast checking and safe optimization follow once those semantics
are defined. Keep each phase separately testable and retain the shared compiler
entry point for both CLI and Flask.

Implementation references: [Lark API](https://lark-parser.readthedocs.io/en/stable/classes.html)
and [Flask testing documentation](https://flask.palletsprojects.com/en/stable/testing/).
