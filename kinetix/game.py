import math
from random import randint, random

import pygame
from pygame import surface
from pygame.math import Vector2

from .assets import image, sound
from .ball import Ball
from .barrel import Barrel
from .bat import Bat
from .constants import (
    BALL_MAX_SPEED,
    BALL_MIN_SPEED,
    BALL_RADIUS,
    BAT_MAX_X,
    BAT_MIN_X,
    BAT_TOP_EDGE,
    BRICK_HEIGHT,
    BRICK_WIDTH,
    BRICKS_X_START,
    BRICKS_Y_START,
    HEIGHT,
    LEFT_EDGE,
    PORTAL_ANIMATION_SPEED,
    POWERUP_CHANCE,
    RIGHT_EDGE,
    SHADOW_OFFSET,
    TOP_EDGE,
    WIDTH,
)
from .controls import AIControls
from .impact import Impact
from .levels import LEVELS
from .types import BatType, CollisionType


def brick_collide(x, y, grid_x, grid_y, radius):
    x0, y0, x1, y1 = x - radius, y - radius, x + radius, y + radius
    brick_x0, brick_y0 = (
        grid_x * BRICK_WIDTH + BRICKS_X_START,
        grid_y * BRICK_HEIGHT + BRICKS_Y_START,
    )
    brick_x1, brick_y1 = brick_x0 + BRICK_WIDTH, brick_y0 + BRICK_HEIGHT
    center_x, center_y = (brick_x0 + brick_x1) // 2, (brick_y0 + brick_y1) // 2
    if x1 > brick_x0 and x0 < brick_x1 and brick_y0 < y < brick_y1:
        return (brick_x0 if x < center_x else brick_x1), y
    if brick_x0 < x < brick_x1 and y1 > brick_y0 and y0 < brick_y1:
        return x, (brick_y0 if y < center_y else brick_y1)
    position = Vector2(x, y)
    closest = min(
        (
            (brick_x0, brick_y0),
            (brick_x1, brick_y0),
            (brick_x0, brick_y1),
            (brick_x1, brick_y1),
        ),
        key=lambda point: (position - Vector2(point)).length_squared(),
    )
    return closest if (position - Vector2(closest)).length() < radius else None


class Game:
    def __init__(self, controls=None, lives=3):
        if controls is None:
            self.controls = (AIControls(),)
        elif isinstance(controls, tuple):
            self.controls = controls
        else:
            self.controls = (controls,)
        self.lives, self.score = lives, 0
        self.next_bat_index = randint(0, len(self.controls) - 1)
        self.new_level(randint(0, len(LEVELS) - 1))

    def new_level(self, level_num):
        self.play_sound("start_game")
        level_num %= len(LEVELS)
        self.brick_surface = surface.Surface((WIDTH, HEIGHT), flags=pygame.SRCALPHA)
        self.brick_surface.fill((0, 0, 0, 0))
        self.shadow_surface = surface.Surface((WIDTH, HEIGHT), flags=pygame.SRCALPHA)
        self.shadow_surface.fill((0, 0, 0, 0))
        level = LEVELS[level_num]
        self.num_rows, self.num_cols = len(level), len(level[0])
        self.bricks = [row.copy() for row in level]
        self.bricks_remaining = 0
        for y in range(self.num_rows):
            for x in range(self.num_cols):
                self.redraw_brick(x, y)
                if self.bricks[y][x] is not None and self.bricks[y][x] != 13:
                    self.bricks_remaining += 1
        if len(self.controls) == 1:
            self.bats = [Bat(self.controls[0])]
        else:
            half_width = WIDTH // 2
            self.bats = [
                Bat(
                    self.controls[1],
                    half_width // 2,
                    BAT_TOP_EDGE,
                    BAT_MIN_X,
                    half_width,
                    -1,
                ),
                Bat(
                    self.controls[0],
                    half_width + half_width // 2,
                    BAT_TOP_EDGE,
                    half_width,
                    BAT_MAX_X,
                ),
            ]
        self.bat = self.bats[0]
        self.balls = [Ball(bat=self.bats[self.next_bat_index])]
        self.bullets, self.barrels, self.impacts = [], [], []
        self.level_num, self.portal_active, self.portal_frame, self.portal_timer = (
            level_num,
            False,
            0,
            0,
        )

    def redraw_brick(self, x, y):
        screen_x, screen_y = (
            x * BRICK_WIDTH + BRICKS_X_START,
            y * BRICK_HEIGHT + BRICKS_Y_START,
        )
        if self.bricks[y][x] is not None:
            self.brick_surface.blit(
                image("brick" + hex(self.bricks[y][x])[2:]),
                (screen_x, screen_y),
            )
            self.shadow_surface.blit(
                image("bricks"), (screen_x + SHADOW_OFFSET, screen_y + SHADOW_OFFSET)
            )
        else:
            self.brick_surface.fill(
                (0, 0, 0, 0), (screen_x, screen_y, BRICK_WIDTH, BRICK_HEIGHT)
            )
            self.shadow_surface.fill(
                (0, 0, 0, 0),
                (
                    screen_x + SHADOW_OFFSET,
                    screen_y + SHADOW_OFFSET,
                    BRICK_WIDTH,
                    BRICK_HEIGHT,
                ),
            )

    def collide(self, x, y, direction, radius=BALL_RADIUS):
        dx, dy = direction
        if dx < 0 and x < LEFT_EDGE + radius:
            return (LEFT_EDGE, y), True, CollisionType.WALL
        if dx > 0 and x > RIGHT_EDGE - radius:
            return (RIGHT_EDGE, y), True, CollisionType.WALL
        if dy < 0 and y < TOP_EDGE + radius:
            return (x, TOP_EDGE), True, CollisionType.WALL
        x0, y0 = (
            max(0, math.floor((x - BRICKS_X_START - radius) / BRICK_WIDTH)),
            max(0, math.floor((y - BRICKS_Y_START - radius) / BRICK_HEIGHT)),
        )
        x1, y1 = (
            min(
                self.num_cols - 1,
                math.floor((x - BRICKS_X_START + radius) / BRICK_WIDTH),
            ),
            min(
                self.num_rows - 1,
                math.floor((y - BRICKS_Y_START + radius) / BRICK_HEIGHT),
            ),
        )
        for grid_y in range(y0, y1 + 1):
            for grid_x in range(x0, x1 + 1):
                if self.bricks[grid_y][grid_x] is not None:
                    collision = brick_collide(x, y, grid_x, grid_y, radius)
                    if collision is not None:
                        return self._damage_brick(grid_x, grid_y, collision)
        return None

    def _damage_brick(self, x, y, collision):
        center = (
            x * BRICK_WIDTH + BRICKS_X_START + BRICK_WIDTH // 2,
            y * BRICK_HEIGHT + BRICKS_Y_START + BRICK_HEIGHT // 2,
        )
        brick = self.bricks[y][x]
        collision_type = (
            CollisionType.INDESTRUCTIBLE_BRICK if brick == 13 else CollisionType.BRICK
        )
        if brick >= 12:
            self.impacts.append(Impact(center, 13))
            if brick == 12:
                self.bricks[y][x] = 11
        else:
            self.impacts.append(Impact(center, brick))
            if random() < POWERUP_CHANCE:
                self.barrels.append(Barrel(center))
            self.bricks[y][x] = None
            self.redraw_brick(x, y)
            self.bricks_remaining -= 1
            if self.bricks_remaining == 0:
                self.activate_portal()
            self.score += 10
        return collision, False, collision_type

    def activate_portal(self):
        self.portal_active = True
        self.play_sound("portal_exit")

    def update(self):
        for obj in self.bats + self.balls:
            obj.update()
        self.balls = [ball for ball in self.balls if ball.y < HEIGHT]
        if not self.balls:
            if self.lives > 0 or self.in_demo_mode():
                self.lives -= 1
                for bat in self.bats:
                    bat.target_type = BatType.NORMAL
                self.next_bat_index = (self.next_bat_index + 1) % len(self.bats)
                self.balls = [Ball(bat=self.bats[self.next_bat_index])]
            self.play_sound("lose_life")
        for obj in self.impacts + self.barrels + self.bullets:
            obj.update()
        self.impacts = [impact for impact in self.impacts if impact.time < 16]
        self.barrels = [barrel for barrel in self.barrels if barrel.y < HEIGHT]
        self.bullets = [bullet for bullet in self.bullets if bullet.alive]
        if self.portal_active:
            if self.portal_frame < 3:
                self.portal_timer -= 1
                if self.portal_timer <= 0:
                    self.portal_timer, self.portal_frame = (
                        PORTAL_ANIMATION_SPEED,
                        self.portal_frame + 1,
                    )
            elif any(bat.is_portal_transition_complete() for bat in self.bats):
                self.new_level(self.level_num + 1)
        if self.detect_stuck_balls():
            changed = False
            for row in range(self.num_rows):
                for col in range(self.num_cols):
                    if self.bricks[row][col] == 13:
                        self.bricks[row][col], changed = 12, True
                        self.redraw_brick(col, row)
            if changed:
                self.play_sound("bat_small", 1)
            if self.balls:
                self.balls[0].time_since_touched_bat = 0

    def detect_stuck_balls(self):
        return bool(self.balls) and all(
            ball.time_since_damaged_brick >= 30 * 60
            and ball.time_since_touched_bat >= 30 * 60
            for ball in self.balls
        )

    def draw(self, screen):
        screen.blit(image(f"arena{self.level_num % len(LEVELS)}"), (0, 0))
        screen.blit(image(f"portal_exit{self.portal_frame}"), (WIDTH - 90, HEIGHT - 70))
        if len(self.bats) == 2:
            screen.blit(image(f"portal_exit_left{self.portal_frame}"), (20, HEIGHT - 70))
        screen.blit(image("portal_meanie00"), (110, 40))
        screen.blit(image("portal_meanie10"), (440, 40))
        screen.set_clip((20, 42, 600, 598))
        screen.blit(self.shadow_surface, (0, 0))
        for obj in self.barrels + self.balls + self.bats:
            obj.shadow.draw(screen)
        screen.blit(self.brick_surface, (0, 0))
        for obj in self.balls + self.bats + self.barrels + self.bullets:
            obj.draw(screen)
        screen.set_clip(None)
        for impact in self.impacts:
            impact.draw(screen)
        if not self.in_demo_mode():
            for index, digit in enumerate(str(self.score)):
                screen.blit(image("digit" + digit), (15 + index * 55, 50))
            for index in range(self.lives):
                screen.blit(image("life"), (index * 50, HEIGHT - 20))

    def play_sound(self, name, count=1):
        if not self.in_demo_mode():
            try:
                sound(name + str(randint(0, count - 1))).play()
            except pygame.error as error:
                print(error)

    def change_all_ball_speeds(self, change):
        for ball in self.balls:
            ball.speed = min(max(ball.speed + change, BALL_MIN_SPEED), BALL_MAX_SPEED)

    def in_demo_mode(self):
        return all(isinstance(controls, AIControls) for controls in self.controls)
