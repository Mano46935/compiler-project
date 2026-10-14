"""Normalize instruction words without changing quoted content or line numbers."""

import re

from .model import Sentence

SYNONYMS = {"create": "add", "insert": "add"}
# Quoted strings use JSON escapes, including \" and \\.
QUOTED = re.compile(r'("(?:[^"\\\r\n]|\\.)*")')
WORDS = re.compile(r"[A-Za-z]+")


def normalize(source: str) -> list[Sentence]:
    sentences = []
    for line, original in enumerate(source.splitlines(), start=1):
        if not original.strip():
            continue
        parts = QUOTED.split(original)
        for index in range(0, len(parts), 2):
            parts[index] = WORDS.sub(
                lambda match: SYNONYMS.get(match[0].lower(), match[0].lower()),
                parts[index],
            )
            parts[index] = re.sub(r"\s+", " ", parts[index])
        sentences.append(Sentence(line, original, "".join(parts).strip()))
    return sentences
