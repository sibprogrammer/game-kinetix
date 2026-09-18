import pytest

from kinetix.high_scores import record, top


def test_missing_file_returns_ten_zero_scores(tmp_path):
    assert top(tmp_path / "scores") == [0] * 10


def test_missing_scores_are_zero_padded(tmp_path):
    file_path = tmp_path / "scores"
    file_path.write_text("100\n20\n")

    assert top(file_path) == [100, 20] + [0] * 8


def test_record_keeps_the_ten_highest_scores_one_per_line(tmp_path):
    file_path = tmp_path / "scores"

    record(120, file_path)
    record(200, file_path)
    record(10, file_path)

    assert file_path.read_text().splitlines() == [
        "200",
        "120",
        "10",
        "0",
        "0",
        "0",
        "0",
        "0",
        "0",
        "0",
    ]


def test_record_discards_scores_outside_the_top_ten(tmp_path):
    file_path = tmp_path / "scores"
    file_path.write_text("\n".join(map(str, range(100, 0, -10))) + "\n")

    record(5, file_path)

    assert top(file_path) == list(range(100, 0, -10))


def test_record_rejects_negative_scores(tmp_path):
    with pytest.raises(ValueError):
        record(-1, tmp_path / "scores")
