"""Basic page checks and symbol-table reference resolution, not full semantics."""

from .model import CompilationResult, Diagnostic, Element


def resolve(result: CompilationResult) -> str:
    title = ""
    page_seen = False
    for statement in result.ast:
        if statement.kind == "page":
            if page_seen:
                result.diagnostics.append(Diagnostic(
                    "semantic", statement.line, "Only one page title is allowed.",
                ))
            else:
                title = statement.text
                page_seen = True
            continue

        if not page_seen:
            result.diagnostics.append(Diagnostic(
                "semantic", statement.line,
                'Start with: Create a page titled "My Page".',
            ))
        if statement.kind == "add":
            element_id = f"element{len(result.symbols) + 1}"
            result.symbols.append(Element(
                element_id, statement.element_type, statement.text,
                dict(statement.properties), statement.line,
            ))
            statement.resolved_id = element_id
        elif not result.symbols:
            result.diagnostics.append(Diagnostic(
                "reference", statement.line,
                f'Cannot resolve "{statement.reference}": add a heading, paragraph, '
                'or button before formatting it.',
            ))
        else:
            target = result.symbols[-1]
            target.properties.update(statement.properties)
            statement.resolved_id = target.id
    return title
