from math import ceil
from pyray import *
import raylib as rl
from random import randrange

window_w, window_h = 1080, 720

init_window(window_w, window_h, 'amidar')
set_exit_key(rl.KEY_ESCAPE)
debug_key = rl.KEY_F3
debug_mode = True


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
        self.speed = 100
        self.move_dir = Vector2() # actual direction after updates
        self.previous_dir = Vector2()
        self.cur_trail = [self.pos, self.pos] # trail that is drawn behind the player
        self.drawn_pos = Vector2()
        self.drawn_offset = Vector2(self.size.x / -2, self.size.y / -2) # drawing offset so player appears in the middle of the line
        # self.y_offset = ()
        self.current_vline = ()
        self.current_hline = ()
        self.grid = grid

    def update(self):
        self.direction.x = int(is_key_down(rl.KEY_RIGHT)) - int(is_key_down(rl.KEY_LEFT))
        self.direction.y = int(is_key_down(rl.KEY_DOWN)) - int(is_key_down(rl.KEY_UP))

        dt = get_frame_time()
        new_x = self.pos.x + (self.direction.x * self.speed * dt)
        new_y = self.pos.y + (self.direction.y * self.speed * dt)
        new_pos = Vector2(new_x, new_y)

        old_x = self.pos.x
        old_y = self.pos.y

        self.previous_dir.x = self.move_dir.x
        self.previous_dir.y = self.move_dir.y

        if new_x == old_x:
             self.move_dir.x = 0
        if old_y == new_y:
             self.move_dir.y = 0

        x_move, y_move = False, False

        if new_y != self.pos.y:
            for vl in self.grid.v_positions:
                if round(new_x) == vl[0].x and vl[0].y <= new_y <= vl[1].y:
                    self.current_vline = vl
                    y_move = True
                    self.pos.x = vl[0].x
                    self.pos.y = new_y
                    self.move_dir.y = self.direction.y
                    self.move_dir.x = 0
                    break
        
        if new_x != self.pos.x:
            for hl in self.grid.h_positions:
                if round(new_y) == hl[0].y and hl[0].x <= new_x <= hl[1].x:
                    self.current_hline = hl
                    x_move = True
                    if not y_move:
                        self.pos.y = hl[0].y # keeps player on H line when trying to go on vertical inner line
                        self.pos.x = new_x
                    self.move_dir.x = self.direction.x
                    self.move_dir.y = 0
                    break

    def draw(self):
        self.drawn_pos = vector2_add(Vector2(round(self.pos.x), round(self.pos.y)), self.drawn_offset)
        draw_rectangle_v(self.drawn_pos, self.size, GREEN)


class Trail():
    def __init__(self, player:Player, grid:Grid) -> None:
        self.player = player
        self.points = []
        self.grid = grid


    def update(self):
        p = self.player

        movedir_change = p.previous_dir.x != p.move_dir.x or p.previous_dir.y != p.move_dir.y
        stopped = p.move_dir.x == 0 and p.move_dir.y == 0
        started = p.previous_dir.x == 0 and p.previous_dir.y == 0

        # effectively determines if the player just turned and sets the player position to the intersection of the two lines they are on 
        # this is to prevent the trail from being diagonal (possible if the player position has a decimal on both axes)
        # I don't like setting the player's position from here but it is going to have to work for now...
        if movedir_change and p.current_hline and p.current_vline and not (stopped or started):
            p.pos.y = p.current_hline[0].y
            p.pos.x = p.current_vline[0].x
        

        if p.pos.x % 1 != 0 and p.pos.y % 1 != 0: # if this triggers, then diagonal trails are possible (bad!)
            pass
        
        if p.move_dir.x != 0 and p.move_dir.y != 0:
            pass
        

        new_point = Vector2(p.pos.x, p.pos.y) # current position


        if movedir_change: # when the movement direction changes, update the trail points and set the current trail to current position
            # debug_catch()
            last_point = Vector2(p.pos.x, p.pos.y)

            self.points.append(last_point)
            if len(self.points) > 1 and last_point.x != self.points[-2].x and last_point.y != self.points[-2].y:
                print(f'mismatch in trail self.points: {last_point.x, last_point.y} AND {self.points[-2].x, self.points[-2].y}')
            p.cur_trail = [new_point, new_point]

        if p.move_dir.x != 0 or p.move_dir.y != 0: # update the current trail's end point whenever the player moves
            p.cur_trail[1] = new_point

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
        # 'Line intersection':(player.current_hline[0].y if player.current_hline),
        # 'Trail points': [
        #     (p.x, p.y) for p in trail_points
        # ]
        'Trail points': len(trail.points)
    }
    if is_key_pressed(debug_key):
        debug_mode = not debug_mode



    player.update()
    trail.update()

    begin_drawing()
    clear_background(BLACK)

    # Draw the grid thing
    grid.draw()
    player.draw()
    trail.draw()


    if debug_mode:
        draw_text('\n'.join([f'{k}: {v}' for k, v in debug_values.items()]), 0, 0, 20, WHITE)
        if player.current_vline:
            draw_line_v(player.current_vline[0], player.current_vline[1],GREEN)
        if player.current_hline:
            draw_line_v(player.current_hline[0], player.current_hline[1],GREEN)
        
        debug_catch()

    end_drawing()

close_window()