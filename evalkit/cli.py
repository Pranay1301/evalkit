"""evalkit CLI.

    python3 -m evalkit.cli run DATASET.json --system module:function [--save run.json]
    python3 -m evalkit.cli diff BEFORE.json AFTER.json

--system names a callable `str -> str` as module:function, e.g.
examples.faq_bot:answer.
"""

from __future__ import annotations

import argparse
import importlib
import sys

from .dataset import Dataset
from .diff import diff_runs
from .report import render
from .runner import Runner, RunResult


def _load_system(spec: str):
    module_name, _, func = spec.partition(":")
    if not func:
        raise SystemExit("--system must be module:function")
    module = importlib.import_module(module_name)
    return getattr(module, func)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="evalkit")
    sub = parser.add_subparsers(dest="cmd", required=True)

    run_p = sub.add_parser("run", help="run a dataset against a system")
    run_p.add_argument("dataset")
    run_p.add_argument("--system", required=True, help="module:function callable")
    run_p.add_argument("--save", help="write the run result JSON here")
    run_p.add_argument("--show-outputs", action="store_true")

    diff_p = sub.add_parser("diff", help="compare two saved runs")
    diff_p.add_argument("before")
    diff_p.add_argument("after")

    args = parser.parse_args(argv)
    if args.cmd == "run":
        result = Runner(Dataset.load(args.dataset)).run(_load_system(args.system))
        print(render(result, show_outputs=args.show_outputs))
        if args.save:
            result.save(args.save)
            print(f"\nsaved run to {args.save}", file=sys.stderr)
        return 0 if all(c.passed for c in result.case_results) else 1
    before = RunResult.load(args.before)
    after = RunResult.load(args.after)
    print(diff_runs(before, after))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
