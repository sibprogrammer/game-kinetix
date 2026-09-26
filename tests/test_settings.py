import json

import pytest

from kinetix import settings
from kinetix.settings import DEFAULT_SETTINGS, file_path, load, save


def test_file_path_is_beside_the_executable(tmp_path):
    assert file_path(tmp_path / "Kinetix") == tmp_path / ".settings"


def test_file_path_is_beside_the_launched_script_in_development(monkeypatch, tmp_path):
    monkeypatch.setattr(settings.sys, "frozen", False, raising=False)
    monkeypatch.setattr(settings.sys, "argv", [str(tmp_path / "main.py")])

    assert file_path() == tmp_path / ".settings"


def test_missing_settings_use_defaults(tmp_path):
    assert load(tmp_path / ".settings") == DEFAULT_SETTINGS


def test_settings_are_saved_as_json_with_high_scores(tmp_path):
    path = tmp_path / ".settings"
    settings = {
        "in_game_music": False,
        "sound_effects": True,
        "random_levels": True,
        "meanies": False,
        "high_scores": [300, 100],
    }

    save(settings, path)

    assert json.loads(path.read_text()) == {
        **settings,
        "high_scores": [300, 100] + [0] * 8,
    }
    assert load(path) == {**settings, "high_scores": [300, 100] + [0] * 8}


def test_invalid_settings_are_rejected(tmp_path):
    path = tmp_path / ".settings"
    path.write_text('{"high_scores": [1, -1]}')

    with pytest.raises(ValueError, match="high_scores"):
        load(path)
