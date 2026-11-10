"""evalkit - a from-scratch evaluation harness for LLM and RAG systems.

No framework dependencies: datasets are JSON, scorers are small functions,
reports are computed with bootstrap confidence intervals from the Python
standard library.
"""

from .dataset import Case, Dataset
from .scorers import exact_match, key_phrases, contains_all
from .runner import Runner, RunResult, CaseResult
from .stats import pass_rate, bootstrap_ci

__all__ = [
    "Case",
    "Dataset",
    "exact_match",
    "key_phrases",
    "contains_all",
    "Runner",
    "RunResult",
    "CaseResult",
    "pass_rate",
    "bootstrap_ci",
]
