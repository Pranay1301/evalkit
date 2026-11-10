"""Datasets: a list of cases, each with an input and named expectations.

Format (JSON):

    {
      "name": "pos-corpus-v1",
      "cases": [
        {
          "id": "q1",
          "input": "How are taxes applied?",
          "expect": {
            "key_phrases": ["5 percent", "18 percent"],
            "must_not_contain": ["refund"]
          }
        }
      ]
    }

Every expectation key maps to a scorer with the same name; unknown keys are
a dataset error, not silently skipped - an eval that ignores half its
expectations reports inflated pass rates.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

from . import scorers


@dataclass(frozen=True)
class Case:
    id: str
    input: str
    expect: dict = field(default_factory=dict)


@dataclass(frozen=True)
class Dataset:
    name: str
    cases: tuple[Case, ...]

    @classmethod
    def load(cls, path: str | Path) -> "Dataset":
        raw = json.loads(Path(path).read_text())
        cases = []
        seen_ids: set[str] = set()
        for i, c in enumerate(raw["cases"]):
            cid = c.get("id") or f"case-{i}"
            if cid in seen_ids:
                raise ValueError(f"duplicate case id {cid!r} in {path}")
            seen_ids.add(cid)
            expect = c.get("expect", {})
            unknown = set(expect) - set(scorers.REGISTRY)
            if unknown:
                raise ValueError(
                    f"case {cid!r}: unknown scorers {sorted(unknown)}; "
                    f"available: {sorted(scorers.REGISTRY)}"
                )
            cases.append(Case(id=cid, input=c["input"], expect=expect))
        if not cases:
            raise ValueError(f"no cases in {path}")
        return cls(name=raw.get("name", Path(path).stem), cases=tuple(cases))
