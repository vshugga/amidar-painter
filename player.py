from pyray import *
import raylib as rl
from grid import Grid
from entity import Entity
from timer import Timer
from trail import Trail
# from enemy import Enemy

class Player(Entity):
    def __init__(self, x, y, width, height, current_line, grid:Grid) -> None:
        super().__init__(x, y, width, height, current_line, grid)
        self.cur_trail = [Vector2(x, y), self.pos] # trail that is drawn behind the player
        self.color = GREEN
        self.lives = 3
        self.hit_cooldown = Timer(3)
        self.trail = Trail(self, self.grid, BLUE)
        self.score = 0
        
    def update(self):
        self.direction.x = int(is_key_down(rl.KEY_RIGHT)) - int(is_key_down(rl.KEY_LEFT))
        self.direction.y = int(is_key_down(rl.KEY_DOWN)) - int(is_key_down(rl.KEY_UP))

        # FOR TESTING ONLY
        # self.direction.x = 1
        # self.direction.y = -1
        dt = get_frame_time()
        self.move(dt)
        self.hit_cooldown.update()
        self.trail.update()

    def enemy_hit(self, enemy):
        if self.hit_cooldown.active:
            return
        self.lives -= 1
        self.hit_cooldown.activate()


