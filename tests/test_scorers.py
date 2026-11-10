from evalkit.scorers import (
    exact_match, key_phrases, must_not_contain, max_words, min_words,
)


def test_exact_match_normalizes_case_and_whitespace():
    assert exact_match("  Hello   World ", "hello world").passed
    assert not exact_match("hello", "goodbye").passed


def test_key_phrases_partial_credit_and_missing_detail():
    s = key_phrases("tax is 5 percent on food", ["5 percent", "18 percent", "tax"])
    assert not s.passed
    assert abs(s.value - 2 / 3) < 1e-9
    assert "18 percent" in s.detail


def test_key_phrases_all_present():
    assert key_phrases("Taxes: 5 percent and 18 percent.", ["5 percent", "18 percent"]).passed


def test_must_not_contain_flags_banned():
    s = must_not_contain("we offer store credit only", ["store credit only"])
    assert not s.passed
    assert "store credit only" in s.detail
    assert must_not_contain("full refund", ["store credit only"]).passed


def test_word_limits():
    assert max_words("one two three", 3).passed
    assert not max_words("one two three four", 3).passed
    assert min_words("one two three", 3).passed
    assert not min_words("one two", 3).passed
