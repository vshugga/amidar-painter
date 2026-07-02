from pyray import *
import raylib as rl
from random import randrange

window_w, window_h = 1080, 720

init_window(window_w, window_h, 'amidar')
set_exit_key(rl.KEY_ESCAPE)
debug_key = rl.KEY_F3
debug_mode = True
# set_target_fps(3)


def debug_catch():
    if is_key_down(rl.KEY_D):
        pass



class Grid():
    def __init__(self, width=650, height=650, line_thickness=8.0, vertical_lines=6, h_lines_min=4, h_lines_max=6):
        self.width = width
        self.height = height 
        self.line_thickness = line_thickness
        self.rect_origin = Vector2((window_w/2)-(width/2),(window_h/2)-(height/2))
        # rect = Rectangle(rect_origin.x, rect_origin.y, rect_x, rect_y) # perimeter

        self.v_lines_num = vertical_lines
        # self.h_lines_minmax = (h_lines_min,h_lines_max) # number of horizontal lines in a column
        self.h_lines_range = (height // 10, width // 3) # min/max height of a cell

        self.cell_width = width/(self.v_lines_num-1)
        # pairs of vectors for inner lines top/bottom point
        self.v_positions = [(
                Vector2(self.rect_origin.x+self.cell_width*i,self.rect_origin.y), 
                Vector2(self.rect_origin.x+self.cell_width*i,self.rect_origin.y+height)) 
            for i in range(self.v_lines_num)
        ]

        # pairs of vectors for inner horizontal lines left/right point
        self.h_positions = [] 

        #TODO: This algorithm needs rewritten to avoid horizontal lines that are directly adjacent
        # probably have the h_lines thing place them as it goes, placing the earliest it can (have only the first column be random)

        for vl in range(vertical_lines-1): # -1 to prevent H lines on last v line
            # x = rect_origin.x+(vl*cell_width)
            x = self.v_positions[vl][0].x
            y = self.rect_origin.y
            h_lines = randrange(h_lines_min, h_lines_max)
            for hl in range(h_lines):
                ly = y
                y += randrange(*self.h_lines_range)
                if y > self.rect_origin.y+height - self.h_lines_range[0]: # do not place a horizontal line if it will be lower than lowest possible
                    remaining = self.rect_origin.y+height-ly
                    if remaining > self.h_lines_range[1]:
                        y = (remaining//2) + ly # if the remaining cell size would be larger than allowed, split it in half
                        # print('half on col ' + str(vl))
                    else:
                        break
                nl1 = Vector2(x, y)
                nl2 = Vector2(x+self.cell_width,y)
                self.h_positions += [(nl1, nl2)]

        #TODO: fix the corner edges           
        top_h_line = [(Vector2(self.rect_origin.x, self.rect_origin.y), Vector2(self.rect_origin.x+width, self.rect_origin.y))]
        bottom_h_line = [(Vector2(self.rect_origin.x, self.rect_origin.y+height), Vector2(self.rect_origin.x+width, self.rect_origin.y+height))]

        self.h_positions += top_h_line + bottom_h_line

    def draw(self):
        for p in self.v_positions + self.h_positions:
            draw_line_ex(*p,self.line_thickness, RED)


class Player():
    def __init__(self, x, y, w, h, grid:Grid) -> None:
        self.pos = Vector2(x, y)
        self.size = Vector2(w, h)
        # self.line_thickness = line_thickness
        self.direction = Vector2() # player controlled direction
        self.speed = 200
        self.move_dir = Vector2() # actual direction after updates
        self.cur_trail = [Vector2(x, y), self.pos] # trail that is drawn behind the player
        self.drawn_pos = Vector2()
        self.drawn_offset = Vector2(self.size.x / -2, self.size.y / -2) # drawing offset so player appears in the middle of the line
        # self.y_offset = ()
        # self.current_vline = ()
        # self.current_hline = ()
        self.intersection_point = Vector2(self.pos.x, self.pos.y)
        self.current_line = grid.v_positions[0]
        self.intersecting_line = ()
        self.grid = grid
        self.movedir_change = False
        self.stop_flag = True

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
        '''Get the first intersecting line between two points, and the side (1 for right/down, 0 for left/up)'''

        if p1.x == p2.x:
            # lines = [l for l in self.grid.h_positions if 
            # ((l[0].x == p1.x and p1.y <= l[0].y <= p2.y)
            #  or (l[1].x == p1.x and p1.y <= l[1].y <= p2.y))]
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

        on_vertical = self.is_vertical(self.current_line)

        if on_vertical:
            add_y = self.direction.y * self.speed * dt
        else:
            add_x = self.direction.x * self.speed * dt

        new_x = self.pos.x + add_x
        new_y = self.pos.y + add_y

        x_clamped = clamp(new_x, self.current_line[0].x, self.current_line[1].x)
        y_clamped = clamp(new_y, self.current_line[0].y, self.current_line[1].y)
        
        self.intersecting_line = self.get_intersecting_line()
        will_pass_line, side = self.get_passed_line(self.pos, Vector2(x_clamped, y_clamped))
        self.line_change = False
        
        # if self.intersecting_line:
        #     # print('On Intersection: ', self.intersecting_line[0].x, self.intersecting_line[0].y)
        #     if not self.is_vertical(self.intersecting_line):
        #         if self.direction.x != 0: #TODO: Change these to be left/right up/down specific probably
        #             self.current_line = self.intersecting_line
        #             add_x += self.direction.x # nudge the player 1 pixel in the direction they are going so they don't get stuck
        #             self.line_change = True
        #     else: # intersecting line is horizontal
        #         if self.direction.y != 0:
        #             self.current_line = self.intersecting_line
        #             add_y += self.direction.y
        #             self.line_change = True
        # print()
        if will_pass_line:
            # print('will pass')
            if will_pass_line == self.current_line and self.intersecting_line:
                self.current_line = self.intersecting_line
            elif on_vertical:
                if (self.direction.x > 0 and side) or (self.direction.x < 0 and not side):
                    self.current_line = will_pass_line
                    add_x += self.direction.x
                    self.line_change = True
                    # print('turn X')
            else:
                if (self.direction.y > 0 and side) or (self.direction.y < 0 and not side):
                    self.current_line = will_pass_line
                    add_y += self.direction.y
                    self.line_change = True
                    # print('turn Y')


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


class Trail():
    def __init__(self, player:Player, grid:Grid) -> None:
        self.player = player
        self.points = [Vector2(player.pos.x, player.pos.y)]
        self.grid = grid


    def update(self):
        p = self.player
        
        if p.movedir_change:
            if p.line_change:
                self.points.append(p.intersection_point)
            else:
                self.points.append(p.drawn_pos)
            p.cur_trail[0] = p.intersection_point


    def draw(self):
        if self.player.cur_trail:
            draw_spline_segment_linear(self.player.cur_trail[0], self.player.cur_trail[1], grid.line_thickness, YELLOW)
        draw_spline_linear(self.points, len(self.points), grid.line_thickness, YELLOW)

    

grid = Grid()
player = Player(grid.rect_origin.x, grid.rect_origin.y+grid.height, 20, 20, grid)
trail = Trail(player, grid)


while not window_should_close():

    debug_values = {
        'FPS':get_fps(),
        'X':player.pos.x, 
        'Y':player.pos.y,
        'Drawn X':player.drawn_pos.x,
        'Drawn Y':player.drawn_pos.y,
        'Intersection':(player.intersection_point.x,player.intersection_point.y),
        # 'Line intersection':(player.current_hline[0].y if player.current_hline),
        # 'Trail': [
        #     (p.x, p.y) for p in trail.points
        # ],
        'Trail points': len(trail.points),
        'Move direction':(player.move_dir.x, player.move_dir.y)
    }
    if is_key_pressed(debug_key):
        debug_mode = not debug_mode



    player.update()
    trail.update()

    begin_drawing()
    clear_background(BLACK)

    # Draw the grid thing
    grid.draw()
    # trail.draw()
    player.draw()


    if debug_mode:
        draw_text('\n'.join([f'{k}: {v}' for k, v in debug_values.items()]), 0, 0, 20, WHITE)
        if player.current_line:
            draw_line_ex(player.current_line[0], player.current_line[1], 2.0, GREEN)
        # if player.current_hline:
        #     draw_line_v(player.current_hline[0], player.current_hline[1],GREEN)
        
        debug_catch()

    end_drawing()

close_window()