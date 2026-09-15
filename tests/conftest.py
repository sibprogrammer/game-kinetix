import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame
import pytest


@pytest.fixture(scope="session", autouse=True)
def pygame_runtime():
    pygame.init()
    yield
    pygame.quit()
