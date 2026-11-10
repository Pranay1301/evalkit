"""End-to-end: the shipped FAQ bot must fail the hours case (it omits
Sunday) and pass the rest - this is the demo's intentional red row."""

from pathlib import Path

from evalkit.dataset import Dataset
from evalkit.runner import Runner

from examples.faq_bot import answer


def test_faq_bot_demo_run():
    ds = Dataset.load(Path(__file__).parent.parent / "evals" / "faq-dataset.json")
    result = Runner(ds).run(answer)
    by_id = {c.case_id: c for c in result.case_results}
    assert not by_id["hours"].passed
    assert "Sunday" in by_id["hours"].scores["key_phrases"]["detail"]
    assert by_id["refund-policy"].passed
    assert by_id["shipping"].passed
    assert by_id["support"].passed
    assert by_id["out-of-scope"].passed
