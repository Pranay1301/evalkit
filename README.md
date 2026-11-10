# evalkit — LLM evals from scratch

An evaluation harness for LLM apps, RAG pipelines and agents, built with
no framework: datasets are plain JSON, scorers are small deterministic
functions, and every pass rate ships with a bootstrap confidence interval
so a 5-question eval cannot masquerade as a precise measurement.

## What it does

1. **Datasets** (`evalkit/dataset.py`) — JSON files of cases: an input and
   named expectations. Unknown scorer names are rejected at load time, not
   silently skipped — an eval that ignores an expectation reports an
   inflated pass rate.
2. **Scorers** (`evalkit/scorers.py`) — deterministic checks: `exact_match`,
   `key_phrases` (with partial-credit values), `must_not_contain`,
   `max_words`, `min_words`. Each returns pass/fail, a 0–1 value, and a
   detail string explaining the failure.
3. **Runner** (`evalkit/runner.py`) — runs the dataset against any callable
   `str -> str` (an LLM endpoint, a RAG stack, a regex bot — evalkit does
   not care) and stamps the run with the git commit so saved runs are
   attributable.
4. **Statistics** (`evalkit/stats.py`) — pass rates with percentile
   bootstrap confidence intervals (fixed seed: reports are reproducible).
5. **Regression diff** (`evalkit/diff.py`) — compare two saved runs: which
   cases flipped fixed or broken, and whether the rate movement is real or
   inside overlapping confidence intervals (likely noise at small n).

## Quickstart

No dependencies beyond Python 3.10+ (pytest only for the tests).

```bash
# run the bundled demo: a deliberately mediocre FAQ bot
python3 -m evalkit.cli run evals/faq-dataset.json --system examples.faq_bot:answer --save run-1.json

# fix something in your system, run again, then diff
python3 -m evalkit.cli run evals/faq-dataset.json --system examples.faq_bot:answer --save run-2.json
python3 -m evalkit.cli diff run-1.json run-2.json

# tests
python3 -m pytest tests/ -q
```

Your own system: `--system yourmodule:your_function`, any callable that
takes a question string and returns an answer string.

## Measured results

Executed on this machine, 2026-11-11, Python 3.10:

- **21/21 unit and integration tests pass** (`python3 -m pytest tests/ -q`).
- The bundled demo run produces exactly the intended outcome — one FAIL
  row with an actionable detail, because the demo bot's hours answer omits
  Sunday (actual output):

```
FAIL hours  (key_phrases: missing: Sunday)
OK   refund-policy
OK   shipping
OK   support
OK   out-of-scope
case pass rate       80.0%  (95% CI 40.0% - 100.0%, n=5)
```

- The regression diff, run against a fixed copy of the bot (actual output):

```
fixed:  1  (hours)
broken: 0

mean score: 95.0% -> 100.0%
  before 95% CI 85.0%-100.0%   after 95% CI 100.0%-100.0%
  CIs overlap: the rate change may be noise at this sample size.
```

That last line is the point: with 5 cases, a one-case improvement cannot
be statistically distinguished from noise, and the tool says so instead of
declaring victory. The fixed/broken lists are what you act on at small n;
grow the dataset to tighten the intervals.

## Honest limits

- The scorers are lexical. `key_phrases` catches missing facts but cannot
  judge fluency or correctness of phrasing; that needs an LLM-judge
  scorer (not included — no scorer here hides an API dependency).
- Percentile bootstrap intervals at very small n are coarse (the 4/5 case
  above reports a CI floor of 40%). They are honest, not flattering.
- A passing eval means the system met these expectations on these inputs.
  It says nothing about inputs not in the dataset — the dataset is the
  product, and evalkit's job is to keep it honest.

## Layout

```
evalkit/    dataset, scorers, runner, stats, diff, report, cli
evals/      faq-dataset.json (demo dataset)
examples/   faq_bot.py (demo system under test, with one deliberate bug)
tests/      21 tests
```
