"""Normalize instruction words without changing quoted content or line numbers."""

import re

from .model import Sentence

SYNONYMS = {"create": "add", "insert": "add"}
SYNONYMS.update({
    "place": "put", "move": "put", "over": "above", "under": "below",
    "large": "big", "regular": "medium",
})
# Quoted strings use JSON escapes, including \" and \\.
QUOTED = re.compile(r'("(?:[^"\\\r\n]|\\.)*")')
WORDS = re.compile(r"[A-Za-z]+")


def normalize(source: str) -> list[Sentence]:
    sentences = []
    for line, original in enumerate(source.splitlines(), start=1):
        if not original.strip():
            continue
        chunks = []
        start = 0
        quoted = False
        escaped = False
        for index, character in enumerate(original):
            if quoted and escaped:
                escaped = False
            elif quoted and character == "\\":
                escaped = True
            elif character == '"':
                quoted = not quoted
            elif not quoted and character == ".":
                remainder = original[index + 1:]
                if remainder.strip():
                    chunks.append(original[start:index + 1])
                    start = index + 1
        chunks.append(original[start:])
        for chunk in chunks:
            if not chunk.strip():
                continue
            parts = QUOTED.split(chunk)
            for index in range(0, len(parts), 2):
                parts[index] = WORDS.sub(
                    lambda match: SYNONYMS.get(match[0].lower(), match[0].lower()),
                    parts[index],
                )
                parts[index] = re.sub(r"\s+", " ", parts[index])
            sentences.append(Sentence(line, chunk.strip(), "".join(parts).strip()))
    return sentences
