import pygame
import pytest

from kinetix.constants import BALL_MAX_SPEED, BALL_MIN_SPEED, LEFT_EDGE
from kinetix.game import Game, brick_collide
from kinetix.types import CollisionType


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
