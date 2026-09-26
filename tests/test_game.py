import pygame
import pytest

from kinetix import application, runtime
from kinetix.ball import Ball
from kinetix.bullet import Bullet
from kinetix.constants import (
    BALL_MAX_SPEED,
    BALL_MIN_SPEED,
    LEFT_EDGE,
    MEANIE_PORTAL_HOLD_DURATION,
    PORTAL_ANIMATION_SPEED,
)
from kinetix.game import Game, brick_collide
from kinetix.meanie import Meanie
from kinetix.types import CollisionType, State


@pytest.mark.parametrize(
    ("position", "expected"),
    [
        ((19, 110), (20, 110)),
        ((40, 99), (40, 100)),
        ((16, 96), (20, 100)),
        ((0, 0), None),
    ],
)
def test_brick_collide_returns_the_contact_point(position, expected):
    assert brick_collide(*position, 0, 0, 7) == expected


@pytest.fixture
def game(monkeypatch):
    def image_stub(_name):
        return pygame.Surface((40, 20), flags=pygame.SRCALPHA)

    monkeypatch.setattr("kinetix.actor.image", image_stub)
    monkeypatch.setattr("kinetix.game.image", image_stub)
    return Game()


def test_collision_with_left_wall_returns_wall_contact(game):
    collision = game.collide(LEFT_EDGE + 6, 200, (-1, 0))

    assert collision == ((LEFT_EDGE, 200), True, CollisionType.WALL)


def test_change_all_ball_speeds_respects_limits(game):
    game.change_all_ball_speeds(BALL_MAX_SPEED)
    assert [ball.speed for ball in game.balls] == [BALL_MAX_SPEED]

    game.change_all_ball_speeds(-2 * BALL_MAX_SPEED)
    assert [ball.speed for ball in game.balls] == [BALL_MIN_SPEED]


def test_game_starts_with_the_first_level_by_default(game):
    assert game.level_num == 0


def test_random_levels_use_a_shuffled_level_order(game, monkeypatch):
    monkeypatch.setattr("kinetix.game.shuffle", lambda levels: levels.sort())
    random_game = Game(random_levels=True)

    assert [
        random_game.level_num,
        random_game.next_level_number(),
        random_game.next_level_number(),
    ] == [20, 19, 18]


def test_meanies_setting_is_disabled_by_default_and_can_be_enabled(monkeypatch):
    monkeypatch.setattr(application, "state", State.SETTINGS)
    monkeypatch.setattr(application, "settings_selection", 3)
    monkeypatch.setattr(application, "meanies", False)

    application.on_key_down(pygame.K_SPACE)

    assert application.SETTINGS_OPTIONS[3] == "MEANIES"
    assert application.meanies is True


def test_meanies_do_not_spawn_when_disabled(game, monkeypatch):
    monkeypatch.setattr("kinetix.game.LEVELS", ([[0] * 8],))
    monkeypatch.setattr("kinetix.game.randint", lambda _minimum, _maximum: 3)
    monkeypatch.setattr("kinetix.game.random", lambda: 1)
    game.new_level(0)
    assert game.meanies_enabled is False

    for column in range(8):
        game._damage_brick(column, 0, (20 + column * 40, 100))

    assert game.meanie_portal_index is None
    assert game.meanies == []


def test_meanie_spawns_after_half_the_bricks_are_destroyed(game, monkeypatch):
    monkeypatch.setattr("kinetix.game.LEVELS", ([[0] * 8],))
    monkeypatch.setattr(
        "kinetix.game.randint",
        lambda minimum, maximum: 0 if minimum == maximum else 3,
    )
    monkeypatch.setattr("kinetix.game.random", lambda: 1)
    meanie_game = Game(meanies=True)

    for column in range(3):
        meanie_game._damage_brick(column, 0, (20 + column * 40, 100))
    assert meanie_game.meanies == []

    meanie_game._damage_brick(3, 0, (140, 100))

    assert meanie_game.next_meanie_at == 7
    assert meanie_game.meanie_portal_index in (0, 1)


def test_meanie_portal_opens_releases_and_closes(game, monkeypatch):
    monkeypatch.setattr("kinetix.game.choice", lambda _portals: 0)
    game.meanies_enabled = True

    game.spawn_meanie()
    for _ in range(3 * PORTAL_ANIMATION_SPEED):
        game._update_meanie_portal()
    assert game.meanie_portal_frames == [3, 0]
    assert game.meanie_portal_hold_timer == MEANIE_PORTAL_HOLD_DURATION

    for _ in range(MEANIE_PORTAL_HOLD_DURATION):
        game._update_meanie_portal()
    assert len(game.meanies) == 1

    for _ in range(MEANIE_PORTAL_HOLD_DURATION + 3 * PORTAL_ANIMATION_SPEED):
        game._update_meanie_portal()
    assert game.meanie_portal_frames == [0, 0]
    assert game.meanie_portal_index is None


def test_ball_collision_destroys_meanie_and_returns_meanie_collision(game):
    meanie = Meanie((200, 500))
    game.meanies.append(meanie)

    collision = game.collide(200, 500, (1, 0))

    assert collision == ((200, 500), False, CollisionType.MEANIE)
    assert game.meanies == []
    assert game.impacts[-1].type == "f"
    assert game.score == 10


def test_ball_meanie_collision_uses_the_brick_hit_sound(game, monkeypatch):
    played_sounds = []
    monkeypatch.setattr(runtime, "game", game, raising=False)
    monkeypatch.setattr(game, "play_sound", played_sounds.append)

    Ball.collision_sound(CollisionType.MEANIE)

    assert played_sounds == ["hit_brick"]


def test_bullet_collision_destroys_meanie(game, monkeypatch):
    monkeypatch.setattr(runtime, "game", game, raising=False)
    meanie = Meanie((200, 500))
    game.meanies.append(meanie)
    bullet = Bullet((200, 508), 0)

    bullet.update()

    assert bullet.alive is False
    assert game.meanies == []
    assert any(impact.type == "f" for impact in game.impacts)
    assert game.score == 10


def test_meanie_hitting_bat_explodes_with_the_brick_hit_sound(game, monkeypatch):
    meanie = Meanie((game.bat.x, game.bat.y))
    game.meanies.append(meanie)
    played_sounds = []
    monkeypatch.setattr(game, "play_sound", played_sounds.append)

    game.destroy_meanies_hit_by_bats()

    assert game.meanies == []
    assert game.impacts[-1].type == "f"
    assert game.score == 10
    assert played_sounds == ["hit_brick"]
