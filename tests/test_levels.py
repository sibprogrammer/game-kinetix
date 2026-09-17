from pathlib import Path

from kinetix.levels import LEVELS, _natural_sort_key


def test_levels_are_rectangular_and_use_supported_bricks():
    assert LEVELS
    for level in LEVELS:
        assert level
        assert len({len(row) for row in level}) == 1
        assert all(brick is None or 0 <= brick <= 13 for row in level for brick in row)


def test_natural_sort_orders_numeric_suffixes():
    paths = [Path("level10.tmx"), Path("level2.tmx"), Path("level1.tmx")]

    assert sorted(paths, key=_natural_sort_key) == [
        Path("level1.tmx"),
        Path("level2.tmx"),
        Path("level10.tmx"),
    ]
