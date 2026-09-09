from abc import ABC, abstractmethod


class Controls(ABC):
    def __init__(self):
        self.fire_previous_down = False
        self.is_fire_pressed = False

    def update(self):
        fire_down = self.fire_down()
        self.is_fire_pressed = fire_down and not self.fire_previous_down
        self.fire_previous_down = fire_down

    @abstractmethod
    def get_x(self):
        pass

    @abstractmethod
    def fire_down(self):
        pass

    def fire_pressed(self):
        return self.is_fire_pressed
