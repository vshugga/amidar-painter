from pyray import *
import raylib as rl
from grid import Grid

class Entity():
    def __init__(self, x, y, width, height, current_line, grid:Grid) -> None:
        self.pos = Vector2(x, y)
        self.size = Vector2(width, height)
        self.speed = 200
        self.direction = Vector2() # direction controlled by player/enemy
        self.move_dir = Vector2() # actual movement direction after updates/constraints
        self.prev_pos = Vector2() # the position last frame
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
        # self.passed_dict = {}
        self.passed_intersections = []

    def get_curline_tuple(self):
        '''Get the entities current line as a tuple ((x1, y1), (x2, y2)) '''
        return ((self.current_line[0].x, self.current_line[0].y), (self.current_line[1].x, self.current_line[1].y))


    # TODO: transition this to use the intersection pass method instead
    def is_on_line(self, x, y, line=None, point_1=None, point_2=None):
        if point_1 and point_2:
            p1 = point_1
            p2 = point_2
        elif line:
            p1 = line[0]
            p2 = line[1]
        else:
            raise Exception("hey this function needs either a line or a 2 points bro")
        
        on_x = min(p1.x, p2.x) <= x <= max(p1.x, p2.x)
        on_y = min(p1.y, p2.y) <= y <= max(p1.y, p2.y)
        return on_x and on_y


    def get_intersecting_line(self):
        '''Finds whether entity is exactly on an intersection, returns the other line'''
        for l in self.grid.v_positions + self.grid.h_positions:
            if l == self.current_line:
                continue
            if self.is_on_line(self.pos.x, self.pos.y, line=l):
                return l
        return False

    # TODO: possibly combine with above function somehow to avoid looping through lines twice
    def get_passed_lines(self, p1, p2) -> dict:
        '''
        Get the intersecting lines between two points, and the direction as a tuple (x, y) for each.\n
        If the direction is (1, 1), that means the player has stopped at an intersection (p1 and p2 are equal).
        Returns a dict: {intersection point: {"dir":tuple, "line":line}}\n
        Can return the self.current_line.
        '''
        #TODO: Possible optimization - only check the lines that are attached to the current line. (store this for each line in the grid)
        lines = {}
        if p1.x == p2.x and p1.y == p2.y: # if they are the same point, get the intersecting line that is not current line. 
            int_point = p1
            for l in self.grid.v_positions + self.grid.h_positions:
                if self.is_on_line(p1.x, p1.y, line=l) and l != self.current_line:
                    lines[int_point] = {"dir":(1, 1),"line":l}
                    # break # 
            return lines

        reverse_sort = False
        sort_key = None

        if p1.x == p2.x: # if the points make a vertical line, check horizontal lines
            sort_key = lambda item: item[0].y
            if p1.y >= p2.y: # if the player is going up, reverse sort order
                reverse_sort = True
            for l in self.grid.h_positions: 
                left = l[0]
                right = l[1]
                # if l == self.current_line:
                #     continue

                 # skip if neither end (left/right) is on the vertical line
                if left.x != p1.x and right.x != p1.x:
                    continue
                 # store if the lines y value is within p1 - p2 - note that left.y will = right.y because l is horizontal
                if min(p1.y, p2.y) <= left.y <= max(p1.y, p2.y):
                    int_point = right if self.is_on_line(right.x, right.y, point_1=p1, point_2=p2) else left # it has to be either left or right point
                    xdir = 1 if left.x == p1.x else -1
                    lines[int_point] = {"dir":(xdir,0),"line":l}
                    # break # do not break because we want all the intersecting lines

        if p1.y == p2.y: # same as above but check for vertical lines if p1-p2 is horizontal
            sort_key = lambda item: item[0].x
            if p1.x >= p2.x:
                reverse_sort = True
            for l in self.grid.v_positions: 
                top = l[0]
                bottom = l[1]
                # if l == self.current_line:
                #     continue
                if top.y != p1.y and bottom.y != p1.y:
                    continue
                if min(p1.x, p2.x) <= top.x <= max(p1.x, p2.x):
                    int_point = top if self.is_on_line(top.x, top.y, point_1=p1, point_2=p2) else bottom
                    ydir = 1 if top.y == p1.y else -1
                    lines[int_point] = {"dir":(0,ydir),"line":l}
                    # break
        
        # sort the intersecting lines based on the order the player would pass them (their direction)
        # left/right: x decreasing/increasing
        # up/down: y decreasing/increasing
        sorted_dict = dict(sorted(lines.items(), key=sort_key, reverse=reverse_sort))

        return sorted_dict

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

        self.prev_pos.x = self.pos.x
        self.prev_pos.y = self.pos.y

        new_x = self.pos.x + add_x
        new_y = self.pos.y + add_y

        x_clamped = clamp(new_x, self.current_line[0].x, self.current_line[1].x)
        y_clamped = clamp(new_y, self.current_line[0].y, self.current_line[1].y)
        

        self.intersecting_line = self.get_intersecting_line()
        self.will_pass = {}
        self.will_pass = self.get_passed_lines(self.pos, Vector2(x_clamped, y_clamped))
        # prev_line = self.current_line

        if line_callback and self.will_pass: #TODO: needs updated for new dict layout
            line_callback(self.will_pass)
        
        self.passed_intersections = [] # vector2s for each intersection point the player passed last update
        self.at_intersection = False

        # if the player is exactly on an intersection point, do not check passed lines.


        if self.will_pass:
            self.at_intersection = True
            # we have a bunch of intersection points from the current frame to where the player would be on the next one. (in passed_dict)
            # loop over them and get the first one that is in the direction the player wants to go, and set that to the current line.
            # store the points the player did pass + turned onto in a new variable for the trail script to use instead of passed_dict.

            for int_vector, inner_dict in self.will_pass.items():
                self.intersection_point.x = int_vector.x
                self.intersection_point.y = int_vector.y
                new_line = inner_dict["line"]
                x_dir, y_dir = inner_dict["dir"] 

                input_dir = self.direction

                self.passed_intersections.append(int_vector)
                if x_dir and y_dir:
                    if input_dir.x or input_dir.y:
                        self.current_line = new_line
                        break      
                elif (input_dir.x == x_dir != 0) or (input_dir.y == y_dir != 0):
                    self.current_line = new_line
                    break      



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