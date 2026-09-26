import pytest

from kinetix.high_scores import record, top


def test_missing_scores_are_zero_padded():
    assert top() == [0] * 10


def test_scores_are_sorted_and_zero_padded():
    assert top([100, 20]) == [100, 20] + [0] * 8


def test_record_keeps_the_ten_highest_scores():
    scores = record(120)
    scores = record(200, scores)
    scores = record(10, scores)

    assert scores == [200, 120, 10, 0, 0, 0, 0, 0, 0, 0]


def test_record_discards_scores_outside_the_top_ten():
    scores = record(5, range(100, 0, -10))
    assert scores == list(range(100, 0, -10))


def test_record_rejects_negative_scores():
    with pytest.raises(ValueError):
        record(-1)
