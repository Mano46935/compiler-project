"""Run with: python -m text2web examples/fest.sp --output build/fest --debug"""

import argparse
import json
from pathlib import Path
import sys

from .codegen import write_output
from .compiler import compile_source


def main() -> int:
    parser = argparse.ArgumentParser(description="Compile controlled English into a static webpage.")
    parser.add_argument("source", type=Path, help="UTF-8 .sp sentence file")
    parser.add_argument("--output", type=Path, default=Path("build/output"))
    parser.add_argument("--debug", action="store_true", help="Show tokens, AST, and symbols")
    parser.add_argument("--force", action="store_true", help="Replace index.html and style.css in output")
    args = parser.parse_args()
    try:
        result = compile_source(args.source.read_text(encoding="utf-8-sig"))
        if args.debug:
            print(json.dumps(result.debug_data(), indent=2, ensure_ascii=True))
        if not result.success:
            for error in result.diagnostics:
                print(f"Line {error.line} [{error.phase}]: {error.message}", file=sys.stderr)
            print("Compilation failed; no output files written.", file=sys.stderr)
            return 1
        write_output(result, args.output, overwrite=args.force)
    except (OSError, UnicodeError) as error:
        print(f"File error: {error}", file=sys.stderr)
        return 2
    print(f"Compiled {len(result.symbols)} elements into {args.output / 'index.html'} and style.css.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
