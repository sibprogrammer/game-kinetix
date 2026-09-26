import json
import sys
from pathlib import Path

from .high_scores import HIGH_SCORE_COUNT, top

SETTINGS_FILE_NAME = ".settings"
DEFAULT_SETTINGS = {
    "in_game_music": True,
    "sound_effects": True,
    "random_levels": False,
    "meanies": False,
    "high_scores": [0] * HIGH_SCORE_COUNT,
}


def file_path(executable_path=None):
    if executable_path is not None:
        executable = Path(executable_path)
    elif getattr(sys, "frozen", False):
        executable = Path(sys.executable)
    else:
        executable = Path(sys.argv[0])
    return executable.parent / SETTINGS_FILE_NAME


def load(path=None):
    path = Path(path) if path is not None else file_path()
    if not path.exists():
        return {
            **DEFAULT_SETTINGS,
            "high_scores": DEFAULT_SETTINGS["high_scores"].copy(),
        }

    with path.open(encoding="utf-8") as settings_file:
        loaded_settings = json.load(settings_file)
    return validate(loaded_settings)


def save(settings, path=None):
    path = Path(path) if path is not None else file_path()
    validated_settings = validate(settings)
    path.write_text(
        json.dumps(validated_settings, indent=2) + "\n",
        encoding="utf-8",
    )


def validate(settings):
    if not isinstance(settings, dict):
        raise TypeError("settings must be a JSON object")

    validated_settings = {}
    for name, default in DEFAULT_SETTINGS.items():
        value = settings.get(name, default)
        if name == "high_scores":
            if not isinstance(value, list) or any(
                not isinstance(score, int) or score < 0 for score in value
            ):
                raise ValueError("high_scores must be a list of nonnegative integers")
            validated_settings[name] = top(value)
        elif not isinstance(value, bool):
            raise ValueError(f"{name} must be a boolean")
        else:
            validated_settings[name] = value
    return validated_settings
