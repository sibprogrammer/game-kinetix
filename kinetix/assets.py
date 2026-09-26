from functools import lru_cache
from pathlib import Path

import pygame

ROOT = Path(__file__).parent.parent

DEBUG_FONT_PATH = ROOT / "fonts" / "ShareTechMono-Regular.ttf"
DEBUG_FONT_SIZE = 24
DEBUG_TEXT_COLOR = (79, 255, 112)
DEBUG_TEXT_OPACITY = 180
FONT_CHARACTERS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!?.,:;+-=*/()<>"
FONT_GLYPH_SIZE = (50, 50)
FONT_GLYPH_WIDTH = 38
FONT_GLYPH_ADVANCE = 34


@lru_cache
def image(name):
    return pygame.image.load(ROOT / "images" / f"{name}.png").convert_alpha()


@lru_cache
def sound(name):
    return pygame.mixer.Sound(ROOT / "sounds" / f"{name}.ogg")


@lru_cache
def debug_font():
    return pygame.font.Font(DEBUG_FONT_PATH, DEBUG_FONT_SIZE)


def render_debug_text(text):
    rendered = debug_font().render(text, True, DEBUG_TEXT_COLOR)
    rendered.fill(
        (255, 255, 255, DEBUG_TEXT_OPACITY), special_flags=pygame.BLEND_RGBA_MULT
    )
    return rendered


@lru_cache
def font_glyph(character):
    try:
        index = FONT_CHARACTERS.index(character)
    except ValueError as error:
        raise ValueError(f"Unsupported font character: {character!r}") from error

    glyph = image("font").subsurface(
        (index * FONT_GLYPH_SIZE[0], 0, *FONT_GLYPH_SIZE)
    )
    return pygame.transform.smoothscale(glyph, (FONT_GLYPH_WIDTH, FONT_GLYPH_SIZE[1]))


def draw_text(surface, text, position):
    x, y = position
    for character in text:
        if character == " ":
            x += FONT_GLYPH_ADVANCE // 2
        else:
            surface.blit(font_glyph(character), (x, y))
            x += FONT_GLYPH_ADVANCE
