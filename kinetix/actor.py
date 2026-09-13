from .assets import image


class Actor:
    def __init__(self, image_name, pos, anchor=("center", "center")):
        self.anchor = anchor
        self.image = image_name
        self.pos = pos

    @property
    def image(self):
        return self._image_name

    @image.setter
    def image(self, name):
        self._image_name = name
        self._surface = image(name)

    @property
    def pos(self):
        return self.x, self.y

    @pos.setter
    def pos(self, position):
        self.x, self.y = position

    @property
    def width(self):
        return self._surface.get_width()

    @property
    def height(self):
        return self._surface.get_height()

    def draw(self, surface):
        anchor_x, anchor_y = self.anchor
        offset_x = self.width / 2 if anchor_x == "center" else anchor_x
        offset_y = self.height / 2 if anchor_y == "center" else anchor_y
        surface.blit(self._surface, (round(self.x - offset_x), round(self.y - offset_y)))
