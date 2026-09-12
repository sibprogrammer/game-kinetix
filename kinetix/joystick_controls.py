import pygame
from pygame._sdl2 import controller

from .constants import BAT_SPEED
from .controls_base import Controls


class JoystickControls(Controls):
    def __init__(self, joystick):
        super().__init__()
        self.joystick = joystick
        joystick.init()
        controller.init()
        self.controller = controller.Controller.from_joystick(joystick)
        self.pause_previous_down = self.is_pause_pressed = False

    def update(self):
        super().update()
        pause_down = self.controller.get_button(pygame.CONTROLLER_BUTTON_START) != 0
        self.is_pause_pressed = pause_down and not self.pause_previous_down
        self.pause_previous_down = pause_down

    def get_x(self):
        if self.joystick.get_numhats() > 0:
            hat_x = self.joystick.get_hat(0)[0]
            if hat_x != 0:
                return hat_x * BAT_SPEED
        if self.joystick.get_numaxes() <= 0:
            return 0
        axis_value = self.joystick.get_axis(0)
        return 0 if abs(axis_value) <= 0.2 else axis_value * BAT_SPEED

    def get_y(self):
        if self.joystick.get_numhats() > 0:
            hat_y = self.joystick.get_hat(0)[1]
            if hat_y != 0:
                return -hat_y * BAT_SPEED
        if self.joystick.get_numaxes() <= 1:
            return 0
        axis_value = self.joystick.get_axis(1)
        return 0 if abs(axis_value) <= 0.2 else axis_value * BAT_SPEED

    def fire_down(self):
        if self.joystick.get_numbuttons() <= 0:
            print("Joystick has no buttons.")
            return False
        return self.joystick.get_button(0) != 0

    def pause_pressed(self):
        return self.is_pause_pressed
