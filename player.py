from pyray import *
import raylib as rl
from grid import Grid
from entity import Entity

class Player(Entity):
    def __init__(self, x, y, width, height, grid:Grid) -> None:
        super().__init__(x, y, width, height, grid)

    def update(self):
        self.direction.x = int(is_key_down(rl.KEY_RIGHT)) - int(is_key_down(rl.KEY_LEFT))
        self.direction.y = int(is_key_down(rl.KEY_DOWN)) - int(is_key_down(rl.KEY_UP))

        # FOR TESTING ONLY
        # self.direction.x = 1
        # self.direction.y = -1
        dt = get_frame_time()
        self.move(dt)


    def draw(self):
        self.drawn_pos = Vector2(round(self.pos.x), round(self.pos.y))
        pos_offset = vector2_add(self.drawn_pos, self.drawn_offset)
        draw_rectangle_v(pos_offset, self.size, GREEN)

