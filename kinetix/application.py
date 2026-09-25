import os
import sys
from pathlib import Path

import pygame
from pygame.locals import K_DOWN, K_ESCAPE, K_RETURN, K_SPACE, K_UP, K_f, K_g, K_p

from . import runtime
from .assets import (
    FONT_GLYPH_ADVANCE,
    FONT_GLYPH_SIZE,
    FONT_GLYPH_WIDTH,
    draw_text,
    image,
)
from .constants import HEIGHT, WIDTH
from .controls import AIControls, JoystickControls, KeyboardControls, PlayerControls
from .game import Game
from .high_scores import record as record_high_score
from .high_scores import top as top_high_scores
from .types import State

fullscreen_mode = True
debug_mode = False
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
GAME_OVER_TEXT = "GAME OVER"
GAME_OVER_ANIMATION_FRAMES = 15
GAME_OVER_MASK_OPACITY = 128
MAIN_MENU_OPTIONS = ("1 PLAYER", "2 PLAYERS", "SETTINGS")
SETTINGS_OPTIONS = ("MUSIC", "RANDOM LEVEL", "BACK")
main_menu_selection = 0
settings_selection = 0
in_game_music = True
random_levels = False


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
    global state, total_frames
    if runtime.game is None:
        runtime.game = Game(ai_controls)
    total_frames += 1
    update_controls()
    if (
        state == State.PLAY
        and any(controls.pause_pressed() for controls in runtime.joystick_controls)
    ):
        toggle_pause()
    if state in (State.TITLE, State.SETTINGS):
        ai_controls.update()
        runtime.game.update()
        if (
            state == State.TITLE
            and main_menu_selection < 2
            and any(controls.fire_pressed() for controls in player_controls[:num_players])
        ):
            start_game(main_menu_selection + 1)
    elif state == State.PLAY:
        if not paused:
            if runtime.game.lives > 0:
                runtime.game.update()
            else:
                runtime.game.play_sound("game_over")
                if not debug_mode:
                    record_high_score(runtime.game.score)
                state = State.GAME_OVER
    elif state == State.GAME_OVER:
        if any(controls.fire_pressed() for controls in player_controls[:num_players]):
            runtime.game = Game(ai_controls)
            state = State.TITLE
            if in_game_music:
                play_music("title_theme")


def draw_overlay(screen):
    if state == State.TITLE:
        screen.blit(image("title"), (0, 0))
        for index, option in enumerate(MAIN_MENU_OPTIONS):
            y = 430 + index * 60
            if index == main_menu_selection:
                draw_text(screen, ">", (120, y))
            draw_text(screen, option, (163, y))
    elif state == State.SETTINGS:
        screen.blit(image("title"), (0, 0))
        draw_sprite_text_centered(screen, "SETTINGS", 300, "white")
        for index, option in enumerate(SETTINGS_OPTIONS):
            y = 390 + index * 70
            if index == settings_selection:
                draw_text(screen, ">", (30, y))
            draw_text(screen, option, (70, y))
            if index < 2:
                value = in_game_music if index == 0 else random_levels
                draw_text(screen, "ON" if value else "OFF", (470, y))
    elif state == State.GAME_OVER:
        draw_game_over(screen)
        draw_sprite_text_centered(screen, "HIGH SCORES", 70, "white")
        scores = top_high_scores()[:5]
        current_score = runtime.game.score if runtime.game is not None else None
        current_score_position = (
            scores.index(current_score) + 1 if current_score in scores else None
        )
        current_score_color = "yellow" if total_frames // 15 % 2 == 0 else "white"
        for position, score in enumerate(scores, start=1):
            score_text = f"{position:02d} - {score:05d}"
            color = (
                current_score_color if position == current_score_position else "white"
            )
            draw_sprite_text_centered(screen, score_text, 70 + position * 65, color)
    if paused:
        pause_text = "PAUSED"
        pause_width = FONT_GLYPH_WIDTH + FONT_GLYPH_ADVANCE * (len(pause_text) - 1)
        draw_text(
            screen,
            pause_text,
            ((WIDTH - pause_width) // 2, 500),
        )
    if show_fps:
        text = pygame.font.Font(None, 24).render(f"FPS: {fps:.1f}", True, "white")
        screen.blit(text, text.get_rect(topright=(WIDTH - 10, 10)))


def draw_game_over(screen):
    text_width = (
        FONT_GLYPH_WIDTH
        + FONT_GLYPH_ADVANCE * (len(GAME_OVER_TEXT) - 2)
        + FONT_GLYPH_ADVANCE // 2
    )
    text_surface = pygame.Surface((text_width, FONT_GLYPH_SIZE[1]), pygame.SRCALPHA)
    draw_text(text_surface, GAME_OVER_TEXT, (0, 0))

    mask_width = text_width // 3
    animation_frame = total_frames // 4 % GAME_OVER_ANIMATION_FRAMES
    mask_x = (
        animation_frame * (text_width + mask_width) // GAME_OVER_ANIMATION_FRAMES
        - mask_width
    )
    mask = pygame.Surface((mask_width, FONT_GLYPH_SIZE[1]), pygame.SRCALPHA)
    mask.fill((0, 0, 0, GAME_OVER_MASK_OPACITY))
    mask.blit(text_surface, (-mask_x, 0), special_flags=pygame.BLEND_RGBA_MULT)
    text_surface.blit(mask, (mask_x, 0))
    screen.blit(text_surface, ((WIDTH - text_width) // 2, 500))


def draw_sprite_text_centered(screen, text, y, color):
    text_width = FONT_GLYPH_WIDTH + sum(
        FONT_GLYPH_ADVANCE // 2 if character == " " else FONT_GLYPH_ADVANCE
        for character in text[:-1]
    )
    text_surface = pygame.Surface((text_width, FONT_GLYPH_SIZE[1]), pygame.SRCALPHA)
    draw_text(text_surface, text, (0, 0))
    text_surface.fill(color, special_flags=pygame.BLEND_RGB_MULT)

    shadow = text_surface.copy()
    shadow.fill("black", special_flags=pygame.BLEND_RGB_MULT)
    x = (WIDTH - text_width) // 2
    screen.blit(shadow, (x + 2, y + 2))
    screen.blit(text_surface, (x, y))


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
    global main_menu_selection, paused, settings_selection, show_fps, state
    global in_game_music, random_levels
    if key == K_f and debug_mode:
        show_fps = not show_fps
    if key == K_g and debug_mode:
        state, paused = State.GAME_OVER, False
    if key == K_p and debug_mode and state == State.PLAY:
        runtime.game.activate_portal()
    if state == State.TITLE:
        if key == K_UP:
            main_menu_selection = max(0, main_menu_selection - 1)
        elif key == K_DOWN:
            main_menu_selection = min(
                len(MAIN_MENU_OPTIONS) - 1, main_menu_selection + 1
            )
        elif key == K_SPACE:
            if main_menu_selection == len(MAIN_MENU_OPTIONS) - 1:
                state = State.SETTINGS
            else:
                start_game(main_menu_selection + 1)
        elif key == K_ESCAPE:
            runtime.running = False
        return
    if state == State.SETTINGS:
        if key == K_UP:
            settings_selection = max(0, settings_selection - 1)
        elif key == K_DOWN:
            settings_selection = min(
                len(SETTINGS_OPTIONS) - 1, settings_selection + 1
            )
        elif key == K_SPACE:
            if settings_selection == 0:
                in_game_music = not in_game_music
                if in_game_music:
                    play_music("title_theme")
                else:
                    stop_music()
            elif settings_selection == 1:
                random_levels = not random_levels
            else:
                state = State.TITLE
        elif key == K_ESCAPE:
            state = State.TITLE
        return
    if key == K_ESCAPE:
        if state == State.PLAY:
            return_to_title()
        else:
            runtime.running = False
    if key == K_RETURN and state == State.PLAY:
        toggle_pause()


def start_game(players):
    global num_players, paused, state
    num_players = players
    runtime.game = Game(player_controls[:num_players], random_levels=random_levels)
    state, paused = State.PLAY, False
    if not in_game_music:
        stop_music()


def return_to_title():
    global state, paused
    runtime.game = Game(ai_controls)
    state, paused = State.TITLE, False
    if in_game_music:
        play_music("title_theme")


def initialize():
    global \
        fullscreen_mode, \
        debug_mode, \
        keyboard_controls, \
        second_keyboard_controls, \
        player_controls, \
        ai_controls, \
        state, \
        total_frames, \
        paused, \
        num_players, \
        main_menu_selection, \
        settings_selection, \
        in_game_music, \
        random_levels, \
        show_fps, \
        fps
    fullscreen_mode = "--windowed" not in sys.argv
    debug_mode = "--debug" in sys.argv
    pygame.mixer.pre_init(frequency=44100, size=-16, channels=2, buffer=1024)
    pygame.init()
    if fullscreen_mode:
        runtime.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    else:
        os.environ.setdefault("SDL_VIDEO_CENTERED", "1")
        runtime.screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Kinetix")
    pygame.display.set_icon(image("app_icon"))
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
    (
        state,
        runtime.game,
        total_frames,
        paused,
        num_players,
        main_menu_selection,
        settings_selection,
        in_game_music,
        random_levels,
        show_fps,
        fps,
    ) = (
        State.TITLE,
        None,
        0,
        False,
        1,
        0,
        0,
        True,
        False,
        False,
        0.0,
    )
    if in_game_music:
        play_music("title_theme")
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
