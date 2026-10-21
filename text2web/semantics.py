"""Resolve element references and reject properties that do not fit their target."""

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
            elif not (statement.text or "").strip():
                result.diagnostics.append(Diagnostic(
                    "semantic", statement.line, "Page title cannot be empty.",
                ))
            else:
                title = statement.text or ""
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
                element_id, statement.element_type or "", statement.text or "",
                dict(statement.properties), statement.line,
            ))
            statement.resolved_id = element_id
        elif statement.kind == "format":
            if not result.symbols:
                result.diagnostics.append(Diagnostic(
                    "reference", statement.line,
                    f'Cannot resolve "{statement.reference}": add an element before formatting it.',
                ))
                continue
            target = result.symbols[-1]
            statement.resolved_id = target.id
            if target.type == "image":
                result.diagnostics.append(Diagnostic(
                    "type", statement.line,
                    f'Images cannot have {", ".join(statement.properties)} formatting.',
                ))
                continue
            target.properties.update(statement.properties)
        else:
            if not result.symbols:
                result.diagnostics.append(Diagnostic(
                    "reference", statement.line,
                    f'Cannot resolve "{statement.reference}": add an element before positioning it.',
                ))
                continue
            source = result.symbols[-1]
            target = next(
                (element for element in reversed(result.symbols)
                 if element.type == statement.target_type),
                None,
            )
            statement.resolved_id = source.id
            if target is None:
                result.diagnostics.append(Diagnostic(
                    "reference", statement.line,
                    f'Cannot resolve "the {statement.target_type}": add one before positioning it.',
                ))
            else:
                statement.target_id = target.id
    return title
