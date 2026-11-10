import json

import pytest

from evalkit.dataset import Dataset


def _write(tmp_path, payload):
    p = tmp_path / "ds.json"
    p.write_text(json.dumps(payload))
    return p


def test_load_valid_dataset(tmp_path):
    ds = Dataset.load(_write(tmp_path, {
        "name": "t",
        "cases": [{"id": "a", "input": "hi", "expect": {"key_phrases": ["x"]}}],
    }))
    assert ds.name == "t"
    assert ds.cases[0].id == "a"


def test_unknown_scorer_is_rejected_not_ignored(tmp_path):
    p = _write(tmp_path, {
        "cases": [{"id": "a", "input": "hi", "expect": {"magic_check": 1}}],
    })
    with pytest.raises(ValueError, match="unknown scorers"):
        Dataset.load(p)


def test_duplicate_case_ids_rejected(tmp_path):
    p = _write(tmp_path, {
        "cases": [
            {"id": "a", "input": "1", "expect": {}},
            {"id": "a", "input": "2", "expect": {}},
        ],
    })
    with pytest.raises(ValueError, match="duplicate"):
        Dataset.load(p)


def test_empty_dataset_rejected(tmp_path):
    with pytest.raises(ValueError, match="no cases"):
        Dataset.load(_write(tmp_path, {"cases": []}))
