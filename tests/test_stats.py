from evalkit.stats import pass_rate, bootstrap_ci, format_rate


def test_pass_rate():
    assert pass_rate([1, 1, 0, 0.5]) == 0.625
    assert pass_rate([]) == 0.0


def test_bootstrap_ci_is_deterministic():
    vals = [1.0, 1.0, 0.0, 1.0, 0.0]
    assert bootstrap_ci(vals) == bootstrap_ci(vals)


def test_ci_width_shrinks_with_n():
    small = bootstrap_ci([1.0, 0.0])
    large = bootstrap_ci([1.0, 0.0] * 50)
    assert (large[1] - large[0]) < (small[1] - small[0])


def test_all_pass_ci_is_tight():
    lo, hi = bootstrap_ci([1.0] * 10)
    assert lo == hi == 1.0


def test_format_rate_shows_n():
    assert "n=3" in format_rate([1.0, 0.0, 1.0])
