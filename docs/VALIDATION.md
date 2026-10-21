# Project validation

## Automated tests

Run from the project folder:

```powershell
.\.venv\Scripts\python.exe -m pytest -q --tb=short
```

The latest full run completed with **59 passed**. Tests cover normalization and
same-line sentence recovery, Lark parsing, symbol references, type and
accessibility errors, contrast checks, cycle detection, nested row/column IR,
optimization, escaped HTML, local image copying and uploads, CLI behavior,
Flask preview/downloads, and failed-build handling.

## Manual checks

- The web editor returns a successful page and compiles the built-in fest example.
- The compiler generates deterministic HTML and CSS from the same source.
- The CLI refuses to write failed builds and protects existing output unless
  `--force` is provided.
- The compiler rejects missing image descriptions, invalid image sources,
  unsupported formatting, insufficient text contrast, and contradictory
  position constraints before generating HTML.
- Image uploads accept PNG, JPEG, GIF, and WebP content only; local image URLs
  are copied into the generated folder.

## Scope

These checks cover the documented controlled-English language and its compiler
workflow. They do not claim that Text2Web understands unrestricted English,
implements every WCAG requirement, or provides JavaScript, form submission,
database features, or production hosting.
