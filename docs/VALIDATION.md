# Review 1 verification

Verified on 14 October 2026 in the project workspace on Windows, using Python
3.14.3, Flask 3.1.3, Lark 1.3.1, and pytest 9.1.1. Exact installed dependency
versions are recorded in `requirements-lock.txt`.

## Automated tests

Command:

```powershell
.\.venv\Scripts\python.exe -m pytest -q --tb=short
```

Actual final result:

```text
........................................                                 [100%]
40 passed in 1.75s
```

The suite covers supported sentences, optional words and synonyms, quote and
line-number preservation, the LALR parser configuration, visible tokens, AST and
symbol-table reference behavior, malformed syntax, invalid string escapes,
unresolved references, document structure, deterministic generation, escaped
HTML, real file output, overwrite protection, CLI success/failure, Flask preview
and downloads, stale-preview prevention, and file-write error reporting.

An initial run exposed a keyword-prefix lexer bug (`a` consuming the start of
`add`). Keyword boundaries were corrected in the grammar before the passing run.

## Actual command-line output

```text
Compiled 3 elements into build\fest\index.html and style.css.
```

The generated HTML and CSS were read and checked. The document contains the
expected title, heading, paragraph, button, and relative stylesheet link.

The invalid example exited with status 1 and reported:

```text
Line 3 [syntax]: Unsupported or malformed instruction. Use the sentence guide; put one instruction on each line and surround text with double quotes.
Compilation failed; no output files written.
```

The `build/invalid` directory did not exist after that failed compilation.

## Running application and browser

- Started the Flask development server; `GET http://127.0.0.1:5000/` returned 200.
- Used an isolated headless Chrome profile to submit the preloaded instructions
  through the actual HTML form and inspect the sandboxed preview.
- Browser document title: `Techno Fest`.
- Heading: `Techno 2026`; paragraph: `Welcome to our college fest`.
- Button text: `Register`; computed font weight: `700`; computed background:
  `rgb(43, 108, 176)`.
- Submitted a page declaration followed by `Make it bold.` with no element.
  The browser displayed the line 2 reference error and removed the preview.
- Captured and visually inspected `build/review1-preview.png` at 1280 × 1000.

Sandboxed Chrome attempts initially lost their debugging connections. The final
browser check ran in a separate hidden Chrome instance outside that execution
sandbox and completed successfully. Temporary browser profiles were used only
for verification, not as project dependencies.

## Limits of the evidence

These checks verify the Review 1 subset. They do not establish full language
coverage, WCAG compliance, layout correctness, optimization correctness,
cross-browser compatibility, production readiness, or a numerical percentage
of completion against the full project. Those features remain planned.
