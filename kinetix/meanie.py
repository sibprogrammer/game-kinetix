from random import choice

from .actor import Actor
from .constants import SHADOW_OFFSET


class Meanie(Actor):
    FRAME_COUNTS = (8, 8, 16)

    def __init__(self, pos):
        super().__init__("blank", pos)
        self.type = choice(range(len(self.FRAME_COUNTS)))
        self.time = 0
        self.shadow = Actor(
            "blank", (self.x + SHADOW_OFFSET, self.y + SHADOW_OFFSET)
        )

    def update(self):
        self.time += 1
        self.y += 0.5
        frame = self.time // 5 % self.FRAME_COUNTS[self.type]
        self.image = f"meanie{self.type:x}{frame:x}"
        self.shadow.image = f"meanies{self.type:x}{frame:x}"
        self.shadow.pos = (self.x + SHADOW_OFFSET, self.y + SHADOW_OFFSET)
