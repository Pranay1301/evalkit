"""Diff two saved runs: which cases flipped, and did the rate really move?

Regression testing for prompts and pipelines: save a baseline run, change
something, run again, and diff. Flips are reported per case; the rate
change is flagged as possibly noise when the two bootstrap CIs overlap -
small-N evals produce apparent movements that are not signal.
"""

from __future__ import annotations

from .runner import RunResult
from .stats import bootstrap_ci, pass_rate


def diff_runs(before: RunResult, after: RunResult) -> str:
    a = {c.case_id: c for c in before.case_results}
    b = {c.case_id: c for c in after.case_results}
    lines = [
        f"diff: {before.dataset} @ {before.git_commit} -> {after.git_commit}",
        "",
    ]
    fixed = [cid for cid in a if cid in b and not a[cid].passed and b[cid].passed]
    broken = [cid for cid in a if cid in b and a[cid].passed and not b[cid].passed]
    lines.append(f"fixed:  {len(fixed)}" + (f"  ({', '.join(fixed)})" if fixed else ""))
    lines.append(f"broken: {len(broken)}" + (f"  ({', '.join(broken)})" if broken else ""))
    only_a = sorted(set(a) - set(b))
    only_b = sorted(set(b) - set(a))
    if only_a:
        lines.append(f"removed cases: {', '.join(only_a)}")
    if only_b:
        lines.append(f"new cases: {', '.join(only_b)}")

    shared = sorted(set(a) & set(b))
    va = [a[c].mean_value for c in shared]
    vb = [b[c].mean_value for c in shared]
    ra, rb = pass_rate(va), pass_rate(vb)
    cia, cib = bootstrap_ci(va), bootstrap_ci(vb)
    lines += [
        "",
        f"mean score: {ra:.1%} -> {rb:.1%}",
        f"  before 95% CI {cia[0]:.1%}-{cia[1]:.1%}   after 95% CI {cib[0]:.1%}-{cib[1]:.1%}",
    ]
    if cia[1] >= cib[0] and cib[1] >= cia[0]:
        lines.append("  CIs overlap: the rate change may be noise at this sample size.")
    else:
        direction = "improvement" if rb > ra else "regression"
        lines.append(f"  CIs do not overlap: likely a real {direction}.")
    return "\n".join(lines)
