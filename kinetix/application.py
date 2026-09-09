import os
import sys

import pgzero.screen
import pygame
from pgzero import music
from pygame.locals import K_ESCAPE, K_RETURN

from . import runtime
from .constants import HEIGHT, WIDTH
from .controls import AIControls, JoystickControls, KeyboardControls, PlayerControls
from .game import Game
from .types import State

fullscreen_mode = True
keyboard_controls = KeyboardControls()
player_controls = PlayerControls(keyboard_controls)
ai_controls = AIControls()
state = State.TITLE
total_frames = 0
paused = False


def get_joystick_if_exists():
    try:
        pygame.joystick.init()
    except Exception:
        pass
    return pygame.joystick.Joystick(0) if pygame.joystick.get_count() > 0 else None


def setup_joystick_controls():
    joystick = get_joystick_if_exists()
    runtime.joystick_controls = (
        JoystickControls(joystick) if joystick is not None else None
    )


def update_controls():
    keyboard_controls.update()
    if runtime.joystick_controls is None:
        setup_joystick_controls()
    if runtime.joystick_controls is not None:
        runtime.joystick_controls.update()
    player_controls.update()


def update():
    global state, total_frames, paused
    if runtime.game is None:
        runtime.game = Game(ai_controls)
    total_frames += 1
    update_controls()
    if (
        state == State.PLAY
        and runtime.joystick_controls is not None
        and runtime.joystick_controls.pause_pressed()
    ):
        toggle_pause()
    if state == State.TITLE:
        ai_controls.update()
        runtime.game.update()
        for controls in (keyboard_controls, runtime.joystick_controls):
            if controls is not None and controls.fire_pressed():
                runtime.game = Game(player_controls)
                state, paused = State.PLAY, False
                stop_music()
                break
    elif state == State.PLAY:
        if not paused:
            if runtime.game.lives > 0:
                runtime.game.update()
            else:
                runtime.game.play_sound("game_over")
                state = State.GAME_OVER
    elif state == State.GAME_OVER:
        for controls in (keyboard_controls, runtime.joystick_controls):
            if controls is not None and controls.fire_pressed():
                runtime.game = Game(ai_controls)
                state = State.TITLE
                play_music("title_theme")


def draw_overlay(screen):
    if state == State.TITLE:
        screen.blit("title", (0, 0))
        screen.blit("startgame", (20, 80))
        screen.blit(f"start{total_frames // 4 % 13}", (WIDTH // 2 - 125, 530))
    elif state == State.GAME_OVER:
        screen.blit(f"gameover{total_frames // 4 % 15}", (WIDTH // 2 - 225, 450))
    if paused:
        screen.draw.text(
            "PAUSED", center=(WIDTH // 2, HEIGHT // 2), fontsize=48, color="white"
        )


def draw():
    if runtime.game is None:
        return

    from pgzero import game as pgzero_game

    screen = pgzero.screen.Screen(pgzero_game.screen)
    pygame.mouse.set_visible(not fullscreen_mode)
    if not fullscreen_mode:
        runtime.game.draw(screen)
        draw_overlay(screen)
        return
    display_surface, actor_surface = screen.surface, pgzero_game.screen
    field_surface = pygame.Surface((WIDTH, HEIGHT))
    screen.surface = pgzero_game.screen = field_surface
    runtime.game.draw(screen)
    draw_overlay(screen)
    screen.surface, pgzero_game.screen = display_surface, actor_surface
    display_surface.fill((0, 0, 0))
    display_surface.blit(
        field_surface,
        (
            (display_surface.get_width() - WIDTH) // 2,
            (display_surface.get_height() - HEIGHT) // 2,
        ),
    )


def play_music(name):
    try:
        music.play(name)
    except Exception:
        pass


def stop_music():
    try:
        music.stop()
    except Exception:
        pass


def toggle_pause():
    global paused
    paused = not paused
    if paused:
        music.pause()
    else:
        music.unpause()


def on_key_down(key):
    if key == K_ESCAPE:
        if state == State.PLAY:
            return_to_title()
        else:
            sys.exit(0)
    if key == K_RETURN and state == State.PLAY:
        toggle_pause()


def return_to_title():
    global state, paused
    runtime.game = Game(ai_controls)
    state, paused = State.TITLE, False
    play_music("title_theme")


def initialize():
    global \
        fullscreen_mode, \
        keyboard_controls, \
        player_controls, \
        ai_controls, \
        state, \
        total_frames, \
        paused
    fullscreen_mode = "--debug" not in sys.argv
    if fullscreen_mode:
        from pgzero import game as pgzero_game

        pgzero_game.DISPLAY_FLAGS |= pygame.FULLSCREEN
    else:
        os.environ.setdefault("SDL_VIDEO_CENTERED", "1")
    try:
        pygame.mixer.quit()
        pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=1024)
        play_music("title_theme")
        music.set_volume(0.3)
    except Exception:
        pass
    keyboard_controls = KeyboardControls()
    setup_joystick_controls()
    player_controls, ai_controls = PlayerControls(keyboard_controls), AIControls()
    state, runtime.game, total_frames, paused = State.TITLE, None, 0, False
