"""Checks for accessible names, safe image sources, and text contrast."""

from .assets import local_asset_path
from .codegen import COLORS
from .model import CompilationResult, Diagnostic, Element

WHITE = "#ffffff"


def _luminance(color: str) -> float:
    channels = [int(color[index:index + 2], 16) / 255 for index in (1, 3, 5)]
    linear = [value / 12.92 if value <= 0.04045 else ((value + 0.055) / 1.055) ** 2.4 for value in channels]
    return 0.2126 * linear[0] + 0.7152 * linear[1] + 0.0722 * linear[2]


def _contrast(first: str, second: str) -> float:
    lighter, darker = sorted((_luminance(first), _luminance(second)), reverse=True)
    return (lighter + 0.05) / (darker + 0.05)


def _check_image(element: Element, result: CompilationResult) -> None:
    if not element.text.strip():
        result.diagnostics.append(Diagnostic(
            "accessibility", element.line, "Images need a non-empty description for alternative text.",
        ))
    source = element.properties.get("src", "")
    try:
        local_asset_path(source)
    except ValueError:
        result.diagnostics.append(Diagnostic(
            "semantic", element.line,
            "Image sources must be a safe relative path or an HTTP(S) URL without credentials.",
        ))


def check_accessibility(result: CompilationResult) -> None:
    for element in result.symbols:
        if element.type == "image":
            _check_image(element, result)
            continue
        if element.type == "button" and not element.text.strip():
            result.diagnostics.append(Diagnostic(
                "accessibility", element.line, "Buttons need visible text to provide an accessible name.",
            ))
        elif not element.text.strip():
            result.diagnostics.append(Diagnostic(
                "accessibility", element.line,
                f"{element.type.capitalize()} elements need non-empty text.",
            ))
        color_name = element.properties.get("color")
        if not color_name:
            continue
        foreground = COLORS[color_name]
        background = WHITE
        if element.type == "button":
            background = foreground
            foreground = "#111827" if color_name == "white" else WHITE
        if _contrast(foreground, background) < 4.5:
            result.diagnostics.append(Diagnostic(
                "accessibility", element.line,
                f'The {color_name} color on this {element.type} does not meet the 4.5:1 text contrast minimum.',
            ))
