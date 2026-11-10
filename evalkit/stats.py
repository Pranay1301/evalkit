"""Statistics: pass rates with bootstrap confidence intervals.

A pass rate of 4/5 (80%) and 800/1000 (80%) are not equally trustworthy.
Every reported rate ships with a percentile bootstrap CI so small fixture
evals cannot masquerade as precise measurements.
"""

from __future__ import annotations

import random


def pass_rate(values: list[float]) -> float:
    return sum(values) / len(values) if values else 0.0


def bootstrap_ci(
    values: list[float],
    *,
    resamples: int = 2000,
    level: float = 0.95,
    seed: int = 42,
) -> tuple[float, float]:
    """Percentile bootstrap CI for the mean of 0..1 values.

    Fixed seed: the report is reproducible - two runs of evalkit on the
    same results print the same interval.
    """
    if not values:
        return (0.0, 0.0)
    rng = random.Random(seed)
    n = len(values)
    means = sorted(
        sum(rng.choice(values) for _ in range(n)) / n for _ in range(resamples)
    )
    lo = means[int((1 - level) / 2 * resamples)]
    hi = means[min(int((1 + level) / 2 * resamples), resamples - 1)]
    return (lo, hi)


def format_rate(values: list[float], *, level: float = 0.95) -> str:
    lo, hi = bootstrap_ci(values, level=level)
    return f"{pass_rate(values):.1%}  (95% CI {lo:.1%} - {hi:.1%}, n={len(values)})"
