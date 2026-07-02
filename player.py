from pyray import *
import raylib as rl
from grid import Grid
from entity import Entity

class Player(Entity):
    def __init__(self, x, y, width, height, current_line, grid:Grid) -> None:
        super().__init__(x, y, width, height, current_line, grid)
        self.cur_trail = [Vector2(x, y), self.pos] # trail that is drawn behind the player
        self.color = GREEN


    def update(self):
        self.direction.x = int(is_key_down(rl.KEY_RIGHT)) - int(is_key_down(rl.KEY_LEFT))
        self.direction.y = int(is_key_down(rl.KEY_DOWN)) - int(is_key_down(rl.KEY_UP))

        # FOR TESTING ONLY
        # self.direction.x = 1
        # self.direction.y = -1
        dt = get_frame_time()
        self.move(dt)




