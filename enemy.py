

class Enemy(Entity):
    def __init__(self, x, y, w, h, grid:Grid) -> None:
        super().__init__(x, y, w, h, grid)