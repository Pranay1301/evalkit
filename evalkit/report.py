"""Human-readable run report: per-case table plus per-scorer rates with CIs."""

from __future__ import annotations

from .runner import RunResult
from .stats import format_rate


def render(result: RunResult, *, show_outputs: bool = False) -> str:
    lines = [
        f"dataset:  {result.dataset}",
        f"commit:   {result.git_commit}",
        f"duration: {result.duration_s:.2f}s",
        "",
    ]
    for c in result.case_results:
        mark = "OK  " if c.passed else "FAIL"
        detail = "; ".join(
            f"{name}: {s['detail']}" for name, s in c.scores.items() if s["detail"]
        )
        lines.append(f"{mark} {c.case_id}" + (f"  ({detail})" if detail else ""))
        if show_outputs:
            lines.append(f"    output: {c.output[:200]}")
    lines.append("")
    scorer_names = sorted({n for c in result.case_results for n in c.scores})
    for name in scorer_names:
        lines.append(f"{name:20s} {format_rate(result.values(name))}")
    all_pass = [1.0 if c.passed else 0.0 for c in result.case_results]
    lines.append(f"{'case pass rate':20s} {format_rate(all_pass)}")
    return "\n".join(lines)
