"""Scorers: deterministic checks over (output, expectation).

Each scorer returns a Score with passed, a 0..1 value, and a detail string
explaining any failure - a red row with no reason is a dead end.
Scorers are pure functions so they are trivially unit-testable and the
same scorer can run offline (exact/phrase checks) or against an LLM judge.
"""

from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass(frozen=True)
class Score:
    passed: bool
    value: float  # 0.0 - 1.0, finer-grained than the boolean
    detail: str = ""


def _norm(s: str) -> str:
    return re.sub(r"\s+", " ", s.strip().lower())


def exact_match(output: str, expected: str) -> Score:
    ok = _norm(output) == _norm(expected)
    return Score(ok, 1.0 if ok else 0.0, "" if ok else f"expected {_norm(expected)!r}")


def key_phrases(output: str, phrases: list[str]) -> Score:
    """All key phrases must appear (case-insensitive, whitespace-tolerant).

    Value is the fraction present, so '12/15' style partial credit shows
    up in aggregates instead of a flat zero.
    """
    norm = _norm(output)
    missing = [p for p in phrases if _norm(p) not in norm]
    value = (len(phrases) - len(missing)) / len(phrases) if phrases else 1.0
    return Score(not missing, value, f"missing: {', '.join(missing)}" if missing else "")


def contains_all(output: str, phrases: list[str]) -> Score:
    return key_phrases(output, phrases)


def must_not_contain(output: str, phrases: list[str]) -> Score:
    norm = _norm(output)
    found = [p for p in phrases if _norm(p) in norm]
    return Score(not found, 0.0 if found else 1.0, f"found banned: {', '.join(found)}" if found else "")


def max_words(output: str, limit: int) -> Score:
    n = len(output.split())
    return Score(n <= limit, 1.0 if n <= limit else 0.0, f"{n} words > {limit}" if n > limit else "")


def min_words(output: str, limit: int) -> Score:
    n = len(output.split())
    return Score(n >= limit, 1.0 if n >= limit else 0.0, f"{n} words < {limit}" if n < limit else "")


REGISTRY = {
    "exact_match": exact_match,
    "key_phrases": key_phrases,
    "contains_all": contains_all,
    "must_not_contain": must_not_contain,
    "max_words": max_words,
    "min_words": min_words,
}
