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
        self.turn_wait = 3 # wait this number of updates before changing directions.
        self.turn_counter = 0
        self.speed = 150
        # self.timer = Timer()

    def line_callback(self, passed_dict:dict):
        '''callback for the entity class move() that adjusts direction based on line. ONLY called when will_pass_line is a line.
        What it does:
        - if we are on a vertical line, change the x direction to match that of the new horizontal line.
        - the Y direction is randomly chosen 50/50.
        '''
        is_up_right = next(iter(passed_dict.values())) # Only looks at the first intersection! (will always turn down first intersection if there are multiple)

        if self.turn_counter < self.turn_wait: # wait for this number of updates to avoid back and forth behavior
            return
        self.turn_counter = 0


        # self.direction = vector2_negate(self.direction)
        # if self.on_vertical:
        #     self.direction.x = 0
        
        d = (-1, 1)
        if self.on_vertical:
            self.direction.x = 1 if is_up_right else -1


        # else:
        #     self.direction.y = 1 if is_up_right else -1

        self.direction.y = choice(d)
        # self.direction.x = choice(d)
        # else:
        #     self.direction.x = choice(d)


        # print('callback')
        pass


    def update(self):

        # if intersecting_line:
        #     self.current_line = intersecting_line

        # if self.at_intersection:
        #     self.direction.x = int(self.is_up_right)
        #     pass
        
        dt = get_frame_time()
        self.move(dt, self.line_callback)
        # print(self.move_dir.x, self.move_dir.y)
        # print(self.direction.x, self.direction.y)

        # if self.move_dir.x == 0 or self.move_dir.y == 0:
        #     self.direction = vector2_negate(self.direction)

        self.turn_counter += 1