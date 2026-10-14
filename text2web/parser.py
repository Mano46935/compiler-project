"""Real Lark lexical analysis and LALR parsing for the Review 1 language."""

import json
from pathlib import Path

from lark import Lark, Token, UnexpectedInput

from .model import CompilationResult, Diagnostic, Sentence, Statement

PARSER = Lark(
    Path(__file__).with_name("grammar.lark").read_text(encoding="utf-8"),
    parser="lalr",
    lexer="basic",
    propagate_positions=True,
)


def parse_sentence(sentence: Sentence, result: CompilationResult) -> None:
    try:
        # Use Lark's own lexer for the visible token stream, including partial
        # tokens before lexical errors. The parser uses that same lexer grammar.
        for token in PARSER.lex(sentence.normalized):
            result.tokens.append({
                "line": sentence.line,
                "type": token.type,
                "value": str(token),
            })
        tree = PARSER.parse(sentence.normalized).children[0]
    except UnexpectedInput:
        result.diagnostics.append(Diagnostic(
            "syntax", sentence.line,
            'Unsupported or malformed instruction. Use the sentence guide; '
            'put one instruction on each line and surround text with double quotes.',
        ))
        return

    fields = {token.type: str(token) for token in tree.children if isinstance(token, Token)}
    try:
        text = json.loads(fields["STRING"]) if "STRING" in fields else None
        # Reject lone surrogate escapes, which cannot be written as UTF-8.
        if text is not None:
            text.encode("utf-8")
    except (ValueError, UnicodeError):
        result.diagnostics.append(Diagnostic(
            "syntax", sentence.line,
            'Invalid quoted text. Use JSON escapes such as \\" for a quote '
            'and \\\\ for a backslash; Unicode text must be valid.',
        ))
        return

    if tree.data == "page":
        statement = Statement("page", sentence.line, text=text)
    elif tree.data == "add_element":
        properties = {name.lower(): fields[name] for name in ("SIZE", "COLOR") if name in fields}
        statement = Statement("add", sentence.line, fields["ELEMENT"], text, properties)
    else:
        statement = Statement(
            "format", sentence.line,
            properties={"font-weight": "bold"}, reference=fields["REFERENCE"],
        )
    result.ast.append(statement)
