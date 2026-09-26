from .actor import Actor


class Impact(Actor):
    def __init__(self, pos, impact_type):
        super().__init__("blank", pos)
        self.type = impact_type
        self.time = 0

    def update(self):
        self.image = (
            f"impactf{self.time // 4}"
            if self.type == "f"
            else "impact" + hex(self.type)[2:] + str(self.time // 4)
        )
        self.time += 1
