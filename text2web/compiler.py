"""Compiler driver. No output generation occurs while blocking errors exist."""

from .codegen import generate
from .accessibility import check_accessibility
from .layout import build_page_tree, optimize_page_tree
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
    check_accessibility(result)
    result.page_tree = build_page_tree(result, title)
    if not result.diagnostics:
        result.page_tree = optimize_page_tree(result.page_tree)
        result.html, result.css = generate(title, result.symbols, result.page_tree)
    return result
