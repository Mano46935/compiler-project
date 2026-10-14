"""Compiler driver. No output generation occurs while blocking errors exist."""

from .codegen import generate
from .model import CompilationResult, Diagnostic
from .normalizer import normalize
from .parser import parse_sentence
from .semantics import resolve


def compile_source(source: str) -> CompilationResult:
    result = CompilationResult(sentences=normalize(source))
    if not result.sentences:
        result.diagnostics.append(Diagnostic("input", 1, "Enter at least a page-title instruction."))
        return result
    for sentence in result.sentences:
        parse_sentence(sentence, result)
    # Continue parsing independent lines, but never resolve against a partial AST.
    if result.diagnostics:
        return result
    title = resolve(result)
    if not result.diagnostics:
        result.html, result.css = generate(title, result.symbols)
    return result
