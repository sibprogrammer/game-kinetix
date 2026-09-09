from random import uniform

from pgzero.actor import Actor
from pygame.math import Vector2

from . import runtime
from .constants import (
    BALL_FAST_SPEED_THRESHOLD,
    BALL_INITIAL_OFFSET,
    BALL_MAX_SPEED,
    BALL_RADIUS,
    BALL_SPEED_UP_INTERVAL,
    BALL_SPEED_UP_INTERVAL_FAST,
    BALL_START_SPEED,
    BAT_TOP_EDGE,
)
from .impact import Impact
from .types import BatType, CollisionType


class Ball(Actor):
    def __init__(
        self,
        x=0,
        y=0,
        direction=Vector2(0, 0),
        stuck_to_bat=True,
        speed=BALL_START_SPEED,
    ):
        super().__init__("ball0", (0, 0))
        self.x, self.y, self.dir = x, y, Vector2(direction)
        self.stuck_to_bat = stuck_to_bat
        self.bat_offset, self.speed = BALL_INITIAL_OFFSET, speed
        self.speed_up_timer = self.time_since_touched_bat = (
            self.time_since_damaged_brick
        ) = 0
        self.shadow = Actor("balls", (self.x + 16, self.y + 16))

    def update(self):
        self.time_since_damaged_brick += 1
        if self.stuck_to_bat:
            self.x, self.y = (
                runtime.game.bat.x + self.bat_offset,
                runtime.game.bat.y - BALL_RADIUS,
            )
            if runtime.game.controls.fire_pressed():
                self.stuck_to_bat = False
                _, self.dir = self.get_bat_bounce_vector()
        else:
            self._move()
        self.shadow.pos = (self.x + 16, self.y + 16)

    def _move(self):
        self.time_since_touched_bat += 1
        self.speed_up_timer += 2 if self.time_since_touched_bat > 5 * 60 else 1
        interval = (
            BALL_SPEED_UP_INTERVAL
            if self.speed < BALL_FAST_SPEED_THRESHOLD
            else BALL_SPEED_UP_INTERVAL_FAST
        )
        if self.speed_up_timer > interval or (
            self.speed_up_timer > interval * 0.75
            and self.time_since_touched_bat > interval * 0.75
        ):
            self.increment_speed()
            self.speed_up_timer = 0
        for _ in range(self.speed):
            self.x += self.dir.x
            self._collide_axis("x")
            previous_y = self.y
            self.y += self.dir.y
            collision = runtime.game.collide(self.x, self.y, self.dir)
            if collision is not None:
                self.dir.y = -self.dir.y
                self.y += self.dir.y
                self._handle_collision(collision)
            elif self.dir.y > 0:
                self._handle_bat_collision(previous_y)
            if self.stuck_to_bat:
                break

    def _collide_axis(self, axis):
        collision = runtime.game.collide(self.x, self.y, self.dir)
        if collision is not None:
            self.dir.x = -self.dir.x
            self.x += self.dir.x
            self._handle_collision(collision)

    def _handle_collision(self, collision):
        if collision[1]:
            runtime.game.impacts.append(Impact(collision[0], 0xC))
        if collision[2] == CollisionType.BRICK:
            self.time_since_damaged_brick = 0
        self.collision_sound(collision[2])

    def _handle_bat_collision(self, previous_y):
        if previous_y + BALL_RADIUS <= BAT_TOP_EDGE < self.y + BALL_RADIUS:
            collided, direction = self.get_bat_bounce_vector()
            if collided:
                if runtime.game.bat.current_type == BatType.MAGNET:
                    self.stuck_to_bat, self.bat_offset, self.dir = (
                        True,
                        self.x - runtime.game.bat.x,
                        Vector2(0, 0),
                    )
                else:
                    self.dir = direction
                self.time_since_touched_bat = 0
                runtime.game.impacts.append(Impact((self.x, self.y), 0xC))
                self.collision_sound(CollisionType.BAT)
        elif self.y + BALL_RADIUS > BAT_TOP_EDGE and self.y < BAT_TOP_EDGE + 15:
            collided, _ = self.get_bat_bounce_vector()
            if collided:
                self.dir = Vector2(
                    1 if self.x > runtime.game.bat.x else -1, uniform(-0.3, -0.1)
                ).normalize()
                self.time_since_touched_bat = 0
                runtime.game.impacts.append(Impact((self.x, BAT_TOP_EDGE), 0xC))
                self.speed = min(self.speed + 4, BALL_MAX_SPEED)
                self.collision_sound(CollisionType.BAT_EDGE)

    def increment_speed(self):
        self.speed = min(self.speed + 1, BALL_MAX_SPEED)

    def get_bat_bounce_vector(self):
        dx = self.x - runtime.game.bat.x
        width = runtime.game.bat.width // 2 + BALL_RADIUS
        return (
            (True, Vector2(dx / width, -0.5).normalize())
            if abs(dx) < width
            else (False, Vector2(0, -1))
        )

    def generate_multiballs(self):
        balls = []
        for index in range(3):
            direction = self.dir.rotate(index * 120)
            if abs(direction.y) < 0.15:
                direction = Vector2(uniform(-1, 1), -1).normalize()
            balls.append(Ball(self.x, self.y, direction, False, self.speed))
        return balls

    @staticmethod
    def collision_sound(collision_type):
        sounds = {
            CollisionType.BRICK: "hit_brick",
            CollisionType.INDESTRUCTIBLE_BRICK: "hit_brick",
            CollisionType.WALL: "hit_wall",
        }
        if collision_type in sounds:
            runtime.game.play_sound(sounds[collision_type])
        elif collision_type in (CollisionType.BAT, CollisionType.BAT_EDGE):
            if runtime.game.bat.current_type == BatType.MAGNET:
                runtime.game.play_sound("ball_stick")
            else:
                runtime.game.play_sound(
                    "hit_fast"
                    if collision_type == CollisionType.BAT
                    else "hit_veryfast"
                )
