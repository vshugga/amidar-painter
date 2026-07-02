from pyray import *
import raylib as rl
from grid import Grid

class Entity():
    def __init__(self, x, y, width, height, current_line, grid:Grid) -> None:
        self.pos = Vector2(x, y)
        self.size = Vector2(width, height)
        self.speed = 500
        self.direction = Vector2() # direction controlled by player/enemy
        self.move_dir = Vector2() # actual movement direction after updates/constraints
        # self.cur_trail = [Vector2(x, y), self.pos] # trail that is drawn behind the player
        self.drawn_pos = Vector2()
        self.drawn_offset = Vector2(self.size.x / -2, self.size.y / -2) # drawing offset so entity appears in the middle of the line
        self.intersection_point = Vector2(self.pos.x, self.pos.y) # the last intersection that the player hit/crossed
        self.grid = grid
        self.current_line = current_line
        self.on_vertical = self.current_line[0].x == self.current_line[0].x
        self.intersecting_line = ()
        self.movedir_change = False
        # self.stop_flag = True
        self.at_intersection = True
        self.color = GREEN # default entity color
        self.is_up_right = False # stores whether the intersecting line is up/right or down/left
        self.passed_dict = {}

    def get_curline_tuple(self):
        '''Get the entities current line as a tuple ((x1, y1), (x2, y2)) '''
        return ((self.current_line[0].x, self.current_line[0].y), (self.current_line[1].x, self.current_line[1].y))

    # TODO: transition this to use the intersection pass method instead
    def is_on_line(self, line, x, y):
        on_x = line[0].x <= x <= line[1].x
        on_y = line[0].y <= y <= line[1].y
        return on_x and on_y

    def get_intersecting_line(self):
        '''Finds whether entity is exactly on an intersection, returns the other line'''
        for l in self.grid.v_positions + self.grid.h_positions:
            if l == self.current_line:
                continue
            if self.is_on_line(l, self.pos.x, self.pos.y):
                return l
        return False

    # TODO: possibly combine with above function somehow to avoid looping through lines twice
    def get_passed_lines(self, p1, p2) -> dict:
        f'''
        Get the intersecting lines between two points, and the side (True for right/down, False for left/up) for each.\n
        Returns a dict where keys = lines, values = side boolean
        Can return the self.current_line.
        '''
        #TODO: Possible optimization - only check the lines that are attached to the current line. (store this for each line in the grid)
        lines = {}
        if p1.x == p2.x:
            for l in self.grid.h_positions: 
                left = l[0]
                right = l[1]
                # if l == self.current_line:
                #     continue
                if left.x != p1.x and right.x != p1.x: # skip if the line has a different x value than the points
                    continue
                if min(p1.y, p2.y) <= left.y <= max(p1.y, p2.y): # store if the lines y value is in between the points
                    lines[l] = left.x == p1.x
                    break
                    # return l, l[0].x == p1.x
        if p1.y == p2.y:
            for l in self.grid.v_positions: # for every vertical line
                top = l[0]
                bottom = l[1]
                # if l == self.current_line:
                #     continue
                if top.y != p1.y and bottom.y != p1.y: # skip if the line's y values are not equal to the points
                    continue
                if min(p1.x, p2.x) <= top.x <= max(p1.x, p2.x):
                    lines[l] = top.x == p1.x
                    break
                    # return l, l[0].y == p1.y

        return lines

    def is_vertical(self, line): #TODO: move to grid?
        return line[0].x == line[1].x


    def move(self, dt, line_callback=None):
        add_x = 0.0
        add_y = 0.0

        self.on_vertical = self.is_vertical(self.current_line)

        if self.on_vertical:
            add_y = self.direction.y * self.speed * dt
        else:
            add_x = self.direction.x * self.speed * dt

        new_x = self.pos.x + add_x
        new_y = self.pos.y + add_y

        x_clamped = clamp(new_x, self.current_line[0].x, self.current_line[1].x)
        y_clamped = clamp(new_y, self.current_line[0].y, self.current_line[1].y)
        

        self.intersecting_line = self.get_intersecting_line()
        self.passed_dict = {}
        self.passed_dict = self.get_passed_lines(self.pos, Vector2(x_clamped, y_clamped))
        # prev_line = self.current_line

        if line_callback and self.passed_dict:
            line_callback(self.passed_dict)

        self.at_intersection = False
        if self.passed_dict:
            self.at_intersection = True
            will_pass_line = next(iter(self.passed_dict)) # ONLY GETS THE FIRST ONE!
            is_up_right = next(iter(self.passed_dict.values()))

            # catches whether player is at T intersection; if the player crossed an intersection of the line they are on
            # hey, this is causing the current line to bounce back and forth...
            if self.current_line in self.passed_dict and self.intersecting_line: 
                self.current_line = self.intersecting_line
                self.intersection_point.x = self.pos.x
                self.intersection_point.y = self.pos.y
            else:
                # if the passed line is up or to the right, use its first point as the intersection
                will_pass_start = Vector2(will_pass_line[0].x, will_pass_line[0].y)
                will_pass_end = Vector2(will_pass_line[1].x, will_pass_line[1].y)
                # if is_up_right: 
                #     #issue: setting the intersection as the first point of the line fails when that line is vertical, or the top/bottom horizontal
                # else:
                #     new_intersection = Vector2(will_pass_line[1].x, will_pass_line[1].y)
                if self.is_on_line(self.current_line, will_pass_start.x, will_pass_start.y):
                    new_intersection = will_pass_start
                elif self.is_on_line(self.current_line, will_pass_end.x, will_pass_end.y):
                    new_intersection = will_pass_end
                else:
                    raise Exception('this should not trigger.')

                input_dir = self.direction.y
                if self.on_vertical:
                    input_dir = self.direction.x

                if (input_dir > 0 and is_up_right) or (input_dir < 0 and not is_up_right):
                    self.current_line = will_pass_line

                self.intersection_point = new_intersection

        prev_x = self.pos.x
        prev_y = self.pos.y

        new_x = prev_x + add_x
        new_y = prev_y + add_y

        new_x_clamped = clamp(new_x, self.current_line[0].x, self.current_line[1].x)
        new_y_clamped = clamp(new_y, self.current_line[0].y, self.current_line[1].y)

        self.pos.x = new_x_clamped
        self.pos.y = new_y_clamped

        newdir_x = self.pos.x - prev_x
        newdir_y = self.pos.y - prev_y
        newdir_x = (newdir_x > 0) - (newdir_x < 0)
        newdir_y = (newdir_y > 0) - (newdir_y < 0)
        newdir = Vector2(newdir_x, newdir_y)

        self.movedir_change = newdir_x != self.move_dir.x or newdir_y != self.move_dir.y
        self.move_dir = newdir

    def draw(self):
        self.drawn_pos = Vector2(round(self.pos.x), round(self.pos.y))
        pos_offset = vector2_add(self.drawn_pos, self.drawn_offset)
        draw_rectangle_v(pos_offset, self.size, self.color)