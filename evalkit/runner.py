"""Runner: execute a dataset against a system under test and score it.

The system under test is any callable `str -> str`; evalkit does not care
whether it wraps a RAG stack, an LLM endpoint, or a regex. Results carry
the git commit and timestamp so a saved run is attributable later.
"""

from __future__ import annotations

import json
import subprocess
import time
from dataclasses import dataclass, field, asdict
from pathlib import Path

from .dataset import Dataset
from .scorers import REGISTRY


@dataclass(frozen=True)
class CaseResult:
    case_id: str
    output: str
    scores: dict  # scorer name -> {"passed": bool, "value": float, "detail": str}

    @property
    def passed(self) -> bool:
        return all(s["passed"] for s in self.scores.values())

    @property
    def mean_value(self) -> float:
        vals = [s["value"] for s in self.scores.values()]
        return sum(vals) / len(vals) if vals else 0.0


@dataclass(frozen=True)
class RunResult:
    dataset: str
    git_commit: str
    started_at: float
    duration_s: float
    case_results: tuple[CaseResult, ...] = field(default_factory=tuple)

    def values(self, scorer: str) -> list[float]:
        return [c.scores[scorer]["value"] for c in self.case_results if scorer in c.scores]

    def save(self, path: str | Path) -> None:
        Path(path).write_text(json.dumps(asdict(self), indent=2))

    @classmethod
    def load(cls, path: str | Path) -> "RunResult":
        raw = json.loads(Path(path).read_text())
        return cls(
            dataset=raw["dataset"],
            git_commit=raw["git_commit"],
            started_at=raw["started_at"],
            duration_s=raw["duration_s"],
            case_results=tuple(
                CaseResult(case_id=c["case_id"], output=c["output"], scores=c["scores"])
                for c in raw["case_results"]
            ),
        )


def _git_commit() -> str:
    try:
        return subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            capture_output=True, text=True, check=True,
        ).stdout.strip()
    except Exception:
        return "unknown"


class Runner:
    def __init__(self, dataset: Dataset):
        self.dataset = dataset

    def run(self, system) -> RunResult:
        start = time.time()
        results = []
        for case in self.dataset.cases:
            output = system(case.input)
            scores = {}
            for name, expected in case.expect.items():
                score = REGISTRY[name](output, expected)
                scores[name] = {
                    "passed": score.passed,
                    "value": score.value,
                    "detail": score.detail,
                }
            results.append(CaseResult(case_id=case.id, output=output, scores=scores))
        return RunResult(
            dataset=self.dataset.name,
            git_commit=_git_commit(),
            started_at=start,
            duration_s=time.time() - start,
            case_results=tuple(results),
        )
