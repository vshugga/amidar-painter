from pyray import *
import raylib as rl
from grid import Grid
from entity import Entity
from timer import Timer
from random import choice

class Enemy(Entity):
    def __init__(self, x, y, w, h, current_line, grid:Grid) -> None:
        super().__init__(x, y, w, h, current_line, grid)
        self.color = ORANGE
        self.direction = Vector2(1, 1) # begin enemies with down direction
        self.turn_wait = 2 # wait this number of updates before changing directions.
        self.update_counter = 0
        self.speed = 500
        # self.timer = Timer()

    def line_callback(self, passed_dict:dict):
        '''callback for the entity class move() that adjusts direction based on line. ONLY called when will_pass_line is a line.
        What it does:
        - if we are on a vertical line, change the x direction to match that of the new horizontal line.
        - the Y direction is randomly chosen 50/50.
        '''

        if self.update_counter < self.turn_wait: # wait for this number of updates to avoid back and forth behavior
            return
        self.update_counter = 0

        first = next(iter(passed_dict)) # Only looks at the first intersection! (will always use first intersection if there are multiple passed)
        first_dir = passed_dict[first]["dir"] # tuple direction of the first turn
        
        if self.on_vertical:
            self.direction.x = first_dir[0] # set the x direction equal to the line that will be passed

        d = (-1, 1)
        self.direction.y = choice(d)


    def update(self):
        
        dt = get_frame_time()
        self.move(dt, self.line_callback)

        self.update_counter += 1