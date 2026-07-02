from grid import Grid
from entity import Entity

class Enemy(Entity):
    def __init__(self, x, y, w, h, current_line, grid:Grid) -> None:
        super().__init__(x, y, w, h, current_line, grid)

    def update(self):
        pass

    def draw(self):
        pass