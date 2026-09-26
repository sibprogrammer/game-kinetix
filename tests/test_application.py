from pygame.locals import K_ESCAPE, K_SPACE, K_d

from kinetix import application, runtime
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

    joystick.down = False
    joystick.fire = True
    application.handle_joystick_menu_input()
    assert application.state == State.SETTINGS

    application.handle_joystick_menu_input()
    assert application.in_game_music is False


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


def test_d_toggles_debug_information(monkeypatch):
    monkeypatch.setattr(application, "debug_mode", True)
    monkeypatch.setattr(application, "show_debug_info", False)

    application.on_key_down(K_d)

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
