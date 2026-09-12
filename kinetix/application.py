import os
import sys

import pgzero.screen
import pygame
from pgzero import music
from pgzero.keyboard import keyboard
from pygame.locals import K_ESCAPE, K_RETURN, K_p

from . import runtime
from .constants import HEIGHT, WIDTH
from .controls import AIControls, JoystickControls, KeyboardControls, PlayerControls
from .game import Game
from .types import State

fullscreen_mode = True
keyboard_controls = KeyboardControls()
second_keyboard_controls = KeyboardControls("a", "d", "s")
player_controls = ()
ai_controls = AIControls()
state = State.TITLE
total_frames = 0
paused = False
num_players = 1


def setup_joystick_controls():
    try:
        pygame.joystick.init()
    except Exception:
        pass
    runtime.joystick_controls = [
        JoystickControls(pygame.joystick.Joystick(index))
        for index in range(min(2, pygame.joystick.get_count()))
    ]


def update_controls():
    keyboard_controls.update()
    second_keyboard_controls.update()
    for controls in runtime.joystick_controls:
        controls.update()
    for controls in player_controls:
        controls.update()


def update():
    global state, total_frames, paused, num_players
    if runtime.game is None:
        runtime.game = Game(ai_controls)
    total_frames += 1
    update_controls()
    if (
        state == State.PLAY
        and any(controls.pause_pressed() for controls in runtime.joystick_controls)
    ):
        toggle_pause()
    if state == State.TITLE:
        ai_controls.update()
        runtime.game.update()
        if keyboard.up or any(
            controls.get_y() < -4 for controls in runtime.joystick_controls
        ):
            num_players = 1
        elif keyboard.down or any(
            controls.get_y() > 4 for controls in runtime.joystick_controls
        ):
            num_players = 2
        if any(controls.fire_pressed() for controls in player_controls[:num_players]):
            runtime.game = Game(player_controls[:num_players])
            state, paused = State.PLAY, False
            stop_music()
    elif state == State.PLAY:
        if not paused:
            if runtime.game.lives > 0:
                runtime.game.update()
            else:
                runtime.game.play_sound("game_over")
                state = State.GAME_OVER
    elif state == State.GAME_OVER:
        if any(controls.fire_pressed() for controls in player_controls[:num_players]):
            runtime.game = Game(ai_controls)
            state = State.TITLE
            play_music("title_theme")


def draw_overlay(screen):
    if state == State.TITLE:
        screen.blit("title", (0, 0))

        menu_image = f'menu{num_players - 1}'
        screen.blit(menu_image, (0, 220))
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
    if key == K_p and not fullscreen_mode and state == State.PLAY:
        runtime.game.activate_portal()
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
        second_keyboard_controls, \
        player_controls, \
        ai_controls, \
        state, \
        total_frames, \
        paused, \
        num_players
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
    keyboard_controls, second_keyboard_controls = (
        KeyboardControls(),
        KeyboardControls("a", "d", "s"),
    )
    setup_joystick_controls()
    player_controls = (
        PlayerControls(
            keyboard_controls,
            runtime.joystick_controls[0] if runtime.joystick_controls else None,
        ),
        PlayerControls(
            second_keyboard_controls,
            runtime.joystick_controls[1]
            if len(runtime.joystick_controls) > 1
            else None,
        ),
    )
    ai_controls = AIControls()
    state, runtime.game, total_frames, paused, num_players = (
        State.TITLE,
        None,
        0,
        False,
        1,
    )
