import json

from evalkit.dataset import Dataset
from evalkit.diff import diff_runs
from evalkit.report import render
from evalkit.runner import Runner, RunResult


def _ds(tmp_path):
    p = tmp_path / "ds.json"
    p.write_text(json.dumps({
        "name": "echo",
        "cases": [
            {"id": "c1", "input": "hello", "expect": {"key_phrases": ["hello"]}},
            {"id": "c2", "input": "bye", "expect": {"key_phrases": ["bye"]}},
        ],
    }))
    return Dataset.load(p)


def test_runner_scores_each_case(tmp_path):
    result = Runner(_ds(tmp_path)).run(lambda s: f"echo {s}")
    assert all(c.passed for c in result.case_results)
    assert result.dataset == "echo"


def test_runner_failing_case_carries_detail(tmp_path):
    result = Runner(_ds(tmp_path)).run(lambda s: "nothing")
    assert not any(c.passed for c in result.case_results)
    assert "missing" in result.case_results[0].scores["key_phrases"]["detail"]


def test_save_load_roundtrip(tmp_path):
    result = Runner(_ds(tmp_path)).run(lambda s: f"echo {s}")
    path = tmp_path / "run.json"
    result.save(path)
    loaded = RunResult.load(path)
    assert loaded.case_results[0].case_id == "c1"
    assert loaded.case_results[0].scores == result.case_results[0].scores


def test_report_marks_failures(tmp_path):
    result = Runner(_ds(tmp_path)).run(lambda s: "nothing")
    text = render(result)
    assert "FAIL c1" in text and "FAIL c2" in text
    assert "case pass rate" in text


def _run(tmp_path, name, fn):
    ds = _ds(tmp_path)
    r = Runner(ds).run(fn)
    return r


def test_diff_reports_fixed_and_broken(tmp_path):
    before = _run(tmp_path, "b", lambda s: "nothing")
    after = _run(tmp_path, "a", lambda s: f"echo {s}")
    text = diff_runs(before, after)
    assert "fixed:  2" in text
    assert "broken: 0" in text


def test_diff_flags_overlapping_cis_as_noise(tmp_path):
    ds = _ds(tmp_path)
    before = Runner(ds).run(lambda s: "nothing" if s == "hello" else "bye")
    after = Runner(ds).run(lambda s: "hello" if s == "hello" else "nothing")
    text = diff_runs(before, after)
    assert "fixed:  1" in text and "broken: 1" in text
    assert "not a significance test" in text
