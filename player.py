from pyray import *
import raylib as rl
from grid import Grid

class Player():
    def __init__(self, x, y, w, h, grid:Grid) -> None:
        self.pos = Vector2(x, y)
        self.size = Vector2(w, h)
        # self.line_thickness = line_thickness
        self.direction = Vector2() # player controlled direction
        self.speed = 500
        self.move_dir = Vector2() # actual direction after updates
        self.cur_trail = [Vector2(x, y), self.pos] # trail that is drawn behind the player
        self.drawn_pos = Vector2()
        self.drawn_offset = Vector2(self.size.x / -2, self.size.y / -2) # drawing offset so player appears in the middle of the line
        # self.y_offset = ()
        # self.current_vline = ()
        # self.current_hline = ()
        self.intersection_point = Vector2(self.pos.x, self.pos.y)
        self.current_line = grid.v_positions[0]
        self.on_vertical = self.current_line[0].x == self.current_line[0].x
        self.intersecting_line = ()
        self.grid = grid
        self.movedir_change = False
        self.stop_flag = True
        self.at_intersection = True

    def get_curline_tuple(self):
        '''Get the players current line as a tuple ((x1, y1), (x2, y2)) '''
        return ((self.current_line[0].x, self.current_line[0].y), (self.current_line[1].x, self.current_line[1].y))

    # TODO: transition this to use the intersection pass method instead
    def is_on_line(self, line):
        on_x = line[0].x <= self.pos.x <= line[1].x
        on_y = line[0].y <= self.pos.y <= line[1].y
        return on_x and on_y

    def get_intersecting_line(self):
        '''Finds whether player is exactly on an intersection, returns the other line'''
        for l in self.grid.v_positions + self.grid.h_positions:
            if l == self.current_line:
                continue
            if self.is_on_line(l):
                return l
        return False

    # TODO: possibly combine with above function somehow to avoid looping through lines twice
    def get_passed_line(self, p1, p2):
        '''Get the first intersecting line between two points, and the side (1 for right/down, 0 for left/up)
        Can return the self.current_line
        '''
        #TODO: Possible optimization - only check the lines that are attached to the current line. (store this for each line in the grid)
        if p1.x == p2.x:
            for l in self.grid.h_positions: 
                # if l == self.current_line:
                #     continue
                if l[0].x != p1.x and l[1].x != p1.x:
                    continue
                if min(p1.y, p2.y) <= l[0].y <= max(p1.y, p2.y):
                    return l, int(l[0].x == p1.x)

        if p1.y == p2.y:
            for l in self.grid.v_positions:
                # if l == self.current_line:
                #     continue
                if l[0].y != p1.y and l[1].y != p1.y:
                    continue
                if min(p1.x, p2.x) <= l[0].x <= max(p1.x, p2.x):
                    return l, int(l[0].y == p1.y)

        return None, None

    def is_vertical(self, line):
        return line[0].x == line[1].x

    def update(self):
        self.direction.x = int(is_key_down(rl.KEY_RIGHT)) - int(is_key_down(rl.KEY_LEFT))
        self.direction.y = int(is_key_down(rl.KEY_DOWN)) - int(is_key_down(rl.KEY_UP))

        # FOR TESTING ONLY
        # self.direction.x = 1
        # self.direction.y = -1

        dt = get_frame_time()
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
        will_pass_line, is_up_right = self.get_passed_line(self.pos, Vector2(x_clamped, y_clamped))
        prev_line = self.current_line

        # if self.intersecting_line:
        #     self.intersection_point.x = self.pos.x
        #     self.intersection_point.y = self.pos.y

        self.at_intersection = False
        if will_pass_line is not None:
            self.at_intersection = True

            # print('will pass')
            # # self.line_change = True
            # self.intersection_point.x = self.pos.x
            # self.intersection_point.y = self.pos.y

            if is_up_right: # cleaner code at the expense of more calculations per frame
                new_intersection = Vector2(will_pass_line[0].x, will_pass_line[0].y)
            else:
                new_intersection = Vector2(will_pass_line[1].x, will_pass_line[1].y)


            if will_pass_line == self.current_line and self.intersecting_line: # catches whether player is at T intersection
                self.current_line = self.intersecting_line
                self.intersection_point.x = self.pos.x
                self.intersection_point.y = self.pos.y
            else:
                input_dir = self.direction.y
                if self.on_vertical:
                    input_dir = self.direction.x

                if (input_dir > 0 and is_up_right) or (input_dir < 0 and not is_up_right):
                    self.current_line = will_pass_line
            
            self.intersection_point = new_intersection

            # if is_up_right:
            #     self.intersection_point = will_pass_line[0]
            # else:
            #     self.intersection_point = will_pass_line[1]



        # self.line_change = False
        # if prev_line is not self.current_line:
        #     self.line_change = True
            # self.intersection_point.x = self.current_line

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
        draw_rectangle_v(pos_offset, self.size, GREEN)

