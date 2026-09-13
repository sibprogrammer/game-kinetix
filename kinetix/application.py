import os
import sys
from pathlib import Path

import pygame
from pygame.locals import K_ESCAPE, K_RETURN, K_f, K_p

from . import runtime
from .assets import image
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
show_fps = False
fps = 0.0
ROOT = Path(__file__).parent.parent


def setup_joystick_controls():
    pygame.joystick.init()
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
        keys = pygame.key.get_pressed()
        if keys[pygame.K_UP] or any(
            controls.get_y() < -4 for controls in runtime.joystick_controls
        ):
            num_players = 1
        elif keys[pygame.K_DOWN] or any(
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
        screen.blit(image("title"), (0, 0))
        menu_image = f'menu{num_players - 1}'
        screen.blit(image(menu_image), (0, 220))
    elif state == State.GAME_OVER:
        screen.blit(image(f"gameover{total_frames // 4 % 15}"), (WIDTH // 2 - 225, 450))
    if paused:
        text = pygame.font.Font(None, 48).render("PAUSED", True, "white")
        screen.blit(text, text.get_rect(center=(WIDTH // 2, HEIGHT // 2)))
    if show_fps:
        text = pygame.font.Font(None, 24).render(f"FPS: {fps:.1f}", True, "white")
        screen.blit(text, text.get_rect(topright=(WIDTH - 10, 10)))


def draw():
    if runtime.game is None:
        return
    pygame.mouse.set_visible(not fullscreen_mode)
    if not fullscreen_mode:
        runtime.game.draw(runtime.screen)
        draw_overlay(runtime.screen)
        return
    field_surface = pygame.Surface((WIDTH, HEIGHT))
    runtime.game.draw(field_surface)
    draw_overlay(field_surface)
    runtime.screen.fill((0, 0, 0))
    field_size = runtime.screen.get_height()
    scaled_field = pygame.transform.smoothscale(field_surface, (field_size, field_size))
    runtime.screen.blit(
        scaled_field,
        (
            (runtime.screen.get_width() - field_size) // 2,
            0,
        ),
    )


def play_music(name):
    pygame.mixer.music.load(ROOT / "music" / f"{name}.ogg")
    pygame.mixer.music.play(-1)


def stop_music():
    pygame.mixer.music.stop()


def toggle_pause():
    global paused
    paused = not paused
    if paused:
        pygame.mixer.music.pause()
    else:
        pygame.mixer.music.unpause()


def on_key_down(key):
    global show_fps
    if key == K_f and not fullscreen_mode:
        show_fps = not show_fps
    if key == K_p and not fullscreen_mode and state == State.PLAY:
        runtime.game.activate_portal()
    if key == K_ESCAPE:
        if state == State.PLAY:
            return_to_title()
        else:
            runtime.running = False
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
        num_players, \
        show_fps, \
        fps
    fullscreen_mode = "--debug" not in sys.argv
    pygame.mixer.pre_init(frequency=44100, size=-16, channels=2, buffer=1024)
    pygame.init()
    if fullscreen_mode:
        runtime.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    else:
        os.environ.setdefault("SDL_VIDEO_CENTERED", "1")
        runtime.screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Kinetix")
    play_music("title_theme")
    pygame.mixer.music.set_volume(0.3)
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
    state, runtime.game, total_frames, paused, num_players, show_fps, fps = (
        State.TITLE,
        None,
        0,
        False,
        1,
        False,
        0.0,
    )
    runtime.running = True


def run():
    global fps
    clock = pygame.time.Clock()
    while runtime.running:
        clock.tick(60)
        fps = clock.get_fps()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                runtime.running = False
            elif event.type == pygame.KEYDOWN:
                on_key_down(event.key)
        update()
        draw()
        pygame.display.flip()
    pygame.quit()
