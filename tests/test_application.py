import pygame
import pytest
from pygame.locals import K_DOWN, K_ESCAPE, K_SLASH, K_SPACE, K_UP

from kinetix import application, runtime
from kinetix.controls import KeyboardControls, PlayerControls
from kinetix.joystick_controls import JoystickControls
from kinetix.state import State


class FakeJoystickControls:
    def __init__(self, *, up=False, down=False, fire=False):
        self.up = up
        self.down = down
        self.fire = fire

    def update(self):
        pass

    def menu_up_pressed(self):
        return self.up

    def menu_down_pressed(self):
        return self.down

    def fire_pressed(self):
        return self.fire


def test_joystick_navigates_and_confirms_player_selection(monkeypatch):
    joystick = FakeJoystickControls()
    monkeypatch.setattr(runtime, "joystick_controls", [joystick])
    monkeypatch.setattr(application, "player_controls", (joystick,))
    monkeypatch.setattr(application, "state", State.TITLE)
    monkeypatch.setattr(application, "main_menu_selection", 0)
    monkeypatch.setattr(application, "player_selection", 0)
    started_players = []
    monkeypatch.setattr(
        application,
        "start_game",
        lambda players, joystick_index=None: started_players.append(
            (players, joystick_index)
        ),
    )

    joystick.fire = True
    application.handle_joystick_menu_input()
    assert application.state == State.PLAYER_SELECTION

    joystick.fire = False
    joystick.down = True
    application.handle_joystick_menu_input()
    assert application.player_selection == 1

    joystick.down = False
    joystick.fire = True
    application.handle_joystick_menu_input()
    assert started_players == [(2, 0)]


def test_joystick_confirming_single_player_controls_the_game(monkeypatch):
    first_joystick = FakeJoystickControls()
    second_joystick = FakeJoystickControls(fire=True)
    monkeypatch.setattr(runtime, "joystick_controls", [first_joystick, second_joystick])
    monkeypatch.setattr(
        application,
        "player_controls",
        (object(), object()),
    )
    monkeypatch.setattr(application, "state", State.PLAYER_SELECTION)
    monkeypatch.setattr(application, "player_selection", 0)
    started_games = []
    monkeypatch.setattr(
        application,
        "start_game",
        lambda players, joystick_index=None: started_games.append(
            (players, joystick_index)
        ),
    )

    application.handle_joystick_menu_input()

    assert started_games == [(1, 1)]


def test_joystick_navigates_and_confirms_settings(monkeypatch):
    joystick = FakeJoystickControls(down=True)
    monkeypatch.setattr(runtime, "joystick_controls", [joystick])
    monkeypatch.setattr(application, "player_controls", (joystick,))
    monkeypatch.setattr(application, "state", State.TITLE)
    monkeypatch.setattr(application, "main_menu_selection", 0)
    monkeypatch.setattr(application, "in_game_music", True)

    application.handle_joystick_menu_input()
    assert application.main_menu_selection == 1

    application.handle_joystick_menu_input()
    assert application.main_menu_selection == 2

    joystick.down = False
    joystick.fire = True
    application.handle_joystick_menu_input()
    assert application.state == State.SETTINGS

    application.handle_joystick_menu_input()
    assert application.in_game_music is False


def test_main_menu_opens_high_scores_and_back_returns_to_title(monkeypatch):
    monkeypatch.setattr(application, "state", State.TITLE)
    monkeypatch.setattr(application, "main_menu_selection", 0)
    monkeypatch.setattr(application, "high_scores_selection", 0)

    application.handle_menu_input(1)
    application.handle_menu_input(0, True)

    assert application.state == State.HIGH_SCORES
    assert application.high_scores_selection == 0

    application.handle_menu_input(0, True)

    assert application.state == State.TITLE


def test_space_confirms_a_setting_once_when_keyboard_fire_is_pressed(monkeypatch):
    keyboard_player = type(
        "KeyboardPlayer", (), {"fire_pressed": lambda _self: True}
    )()
    monkeypatch.setattr(runtime, "joystick_controls", [])
    monkeypatch.setattr(application, "player_controls", (keyboard_player,))
    monkeypatch.setattr(application, "state", State.SETTINGS)
    monkeypatch.setattr(application, "settings_selection", 0)
    monkeypatch.setattr(application, "in_game_music", True)
    monkeypatch.setattr(application, "stop_music", lambda: None)

    application.on_key_down(K_SPACE)
    application.handle_joystick_menu_input()

    assert application.in_game_music is False


def test_escape_returns_to_title_from_game_over(monkeypatch):
    monkeypatch.setattr(application, "state", State.GAME_OVER)
    returned_to_title = []
    monkeypatch.setattr(
        application,
        "return_to_title",
        lambda: returned_to_title.append(True),
    )

    application.on_key_down(K_ESCAPE)

    assert returned_to_title == [True]


@pytest.mark.parametrize(("players", "joystick_index"), [(1, 1), (2, None)])
def test_play_again_preserves_the_finished_games_players_and_settings(
    monkeypatch, players, joystick_index
):
    pygame.display.set_mode((1, 1))
    keyboard = KeyboardControls()
    fire_down = False
    monkeypatch.setattr(keyboard, "fire_down", lambda: fire_down)
    monkeypatch.setattr(application, "keyboard_controls", keyboard)
    monkeypatch.setattr(
        application,
        "player_controls",
        (PlayerControls(keyboard), PlayerControls(KeyboardControls("a", "d", "s"))),
    )
    monkeypatch.setattr(runtime, "joystick_controls", [])
    monkeypatch.setattr(runtime, "game", None)
    monkeypatch.setattr(application, "state", State.TITLE)
    monkeypatch.setattr(application, "paused", False)
    monkeypatch.setattr(application, "debug_mode", False)
    monkeypatch.setattr(application, "random_levels", True)
    monkeypatch.setattr(application, "sound_effects", False)
    monkeypatch.setattr(application, "meanies", True)
    monkeypatch.setattr(application, "high_scores", [])
    monkeypatch.setattr(application, "post_game_selection", 1)

    application.start_game(players, joystick_index)
    finished_game = runtime.game
    finished_game.lives, finished_game.score = 0, 500
    application.update()
    assert application.state == State.GAME_OVER

    fire_down = True
    application.update()
    application.update()
    assert application.state == State.POST_GAME_MENU
    assert application.post_game_selection == 0
    assert runtime.game is finished_game

    fire_down = False
    application.update()
    fire_down = True
    application.update()
    application.update()

    assert application.state == State.PLAY
    assert runtime.game is not finished_game
    assert runtime.game.controls is finished_game.controls
    assert runtime.game.random_levels is True
    assert runtime.game.meanies_enabled is True
    assert runtime.game.sound_effects is False
    assert runtime.game.lives == 3
    assert runtime.game.score == 0
    assert runtime.game.balls[0].stuck_to_bat
    assert application.high_scores.count(500) == 1


def test_joystick_confirms_main_menu_after_game_over(monkeypatch):
    joystick = FakeJoystickControls(down=True)
    monkeypatch.setattr(runtime, "joystick_controls", [joystick])
    monkeypatch.setattr(application, "state", State.POST_GAME_MENU)
    monkeypatch.setattr(application, "post_game_selection", 0)
    returned_to_title = []
    monkeypatch.setattr(
        application, "return_to_title", lambda: returned_to_title.append(True)
    )

    application.handle_joystick_menu_input()
    assert application.post_game_selection == 1

    joystick.down = False
    joystick.fire = True
    application.handle_joystick_menu_input()

    assert returned_to_title == [True]


def test_pause_menu_navigates_and_resumes(monkeypatch):
    monkeypatch.setattr(application, "state", State.PLAY)
    monkeypatch.setattr(application, "paused", True)
    monkeypatch.setattr(application, "pause_selection", 1)
    resumed = []
    monkeypatch.setattr(application, "toggle_pause", lambda: resumed.append(True))

    application.on_key_down(K_UP)
    application.on_key_down(K_SPACE)

    assert application.pause_selection == 0
    assert resumed == [True]


def test_pause_menu_exit_returns_to_title_without_recording_score(monkeypatch):
    monkeypatch.setattr(application, "state", State.PLAY)
    monkeypatch.setattr(application, "paused", True)
    monkeypatch.setattr(application, "pause_selection", 0)
    monkeypatch.setattr(application, "high_scores", [400] + [0] * 9)
    returned_to_title = []
    monkeypatch.setattr(
        application,
        "return_to_title",
        lambda: returned_to_title.append(True),
    )

    application.on_key_down(K_DOWN)
    application.on_key_down(K_SPACE)

    assert application.pause_selection == 1
    assert returned_to_title == [True]
    assert application.high_scores == [400] + [0] * 9


def test_joystick_confirms_pause_menu_selection(monkeypatch):
    joystick = FakeJoystickControls(down=True)
    monkeypatch.setattr(runtime, "joystick_controls", [joystick])
    monkeypatch.setattr(application, "state", State.PLAY)
    monkeypatch.setattr(application, "paused", True)
    monkeypatch.setattr(application, "pause_selection", 0)
    returned_to_title = []
    monkeypatch.setattr(
        application,
        "return_to_title",
        lambda: returned_to_title.append(True),
    )

    application.handle_joystick_menu_input()
    joystick.down = False
    joystick.fire = True
    application.handle_joystick_menu_input()

    assert application.pause_selection == 1
    assert returned_to_title == [True]


def test_slash_toggles_debug_information(monkeypatch):
    monkeypatch.setattr(application, "debug_mode", True)
    monkeypatch.setattr(application, "show_debug_info", False)

    application.on_key_down(K_SLASH)

    assert application.show_debug_info is True


def test_joystick_directional_menu_input_is_edge_triggered():
    controls = object.__new__(JoystickControls)
    controls.fire_previous_down = False
    controls.is_fire_pressed = False
    controls.pause_previous_down = False
    controls.menu_y_previous = 0
    controls.controller = type(
        "Controller",
        (),
        {"get_button": lambda _self, _button: 0},
    )()
    controls.fire_down = lambda: False
    controls.get_y = lambda: 8

    controls.update()
    assert controls.menu_down_pressed()

    controls.update()
    assert not controls.menu_down_pressed()

    controls.get_y = lambda: 0
    controls.update()
    controls.get_y = lambda: -8
    controls.update()
    assert controls.menu_up_pressed()


def test_debug_mode_does_not_record_high_scores(monkeypatch):
    game = type(
        "Game",
        (),
        {"lives": 0, "score": 500, "play_sound": lambda _self, _sound: None},
    )()
    monkeypatch.setattr(runtime, "game", game)
    monkeypatch.setattr(runtime, "joystick_controls", [])
    monkeypatch.setattr(application, "state", State.PLAY)
    monkeypatch.setattr(application, "paused", False)
    monkeypatch.setattr(application, "debug_mode", True)
    monkeypatch.setattr(application, "high_scores", [400] + [0] * 9)

    application.update()

    assert application.high_scores == [400] + [0] * 9


def test_ai_controlled_title_game_uses_random_levels(monkeypatch):
    created_games = []

    class FakeGame:
        def __init__(self, controls, **kwargs):
            created_games.append((controls, kwargs))

    monkeypatch.setattr(application, "Game", FakeGame)
    monkeypatch.setattr(application, "state", State.GAME_OVER)
    monkeypatch.setattr(application, "paused", True)

    application.return_to_title()

    assert created_games == [
        (
            application.ai_controls,
            {
                "random_levels": True,
                "sound_effects": application.sound_effects,
                "meanies": application.meanies,
            },
        )
    ]
