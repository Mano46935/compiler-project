"""Data shared across compiler phases; no HTML in the AST or symbol table."""

from dataclasses import asdict, dataclass, field


@dataclass
class Diagnostic:
    phase: str
    line: int
    message: str


@dataclass
class Sentence:
    line: int
    original: str
    normalized: str


@dataclass
class Statement:
    kind: str
    line: int
    element_type: str | None = None
    text: str | None = None
    properties: dict[str, str] = field(default_factory=dict)
    reference: str | None = None
    resolved_id: str | None = None


@dataclass
class Element:
    id: str
    type: str
    text: str
    properties: dict[str, str]
    line: int


@dataclass
class CompilationResult:
    sentences: list[Sentence] = field(default_factory=list)
    tokens: list[dict] = field(default_factory=list)
    ast: list[Statement] = field(default_factory=list)
    symbols: list[Element] = field(default_factory=list)
    diagnostics: list[Diagnostic] = field(default_factory=list)
    html: str | None = None
    css: str | None = None

    @property
    def success(self) -> bool:
        return not self.diagnostics and self.html is not None

    def debug_data(self) -> dict:
        return {
            "normalized_input": [asdict(s) for s in self.sentences],
            "tokens": self.tokens,
            "ast": [asdict(s) for s in self.ast],
            "symbol_table": [asdict(s) for s in self.symbols],
        }
