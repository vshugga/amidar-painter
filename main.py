from math import ceil
from pyray import *
import raylib as rl
from random import randrange

w, h = 1080, 720

init_window(w, h, 'amidar')
set_exit_key(rl.KEY_ESCAPE)
debug_key = rl.KEY_F3
debug_mode = True


def debug_catch():
    if is_key_down(rl.KEY_D):
        pass

rect_x, rect_y = 650, 650
line_thickness = 8.0
rect_origin = Vector2((w/2)-(rect_x/2),(h/2)-(rect_y/2))
# rect = Rectangle(rect_origin.x, rect_origin.y, rect_x, rect_y) # perimeter

v_lines_num = 6
h_lines_minmax = (4,6) # number of horizontal lines in a column
h_lines_range = (rect_y // 10, rect_y // 3) # min/max height of a cell

cell_width = rect_x/(v_lines_num-1)
# pairs of vectors for inner lines top/bottom point
v_positions = [(Vector2(rect_origin.x+cell_width*i,rect_origin.y), Vector2(rect_origin.x+cell_width*i,rect_origin.y+rect_y)) for i in range(v_lines_num)]

# pairs of vectors for inner horizontal lines left/right point
h_positions = [] 

#TODO: This algorithm needs rewritten to avoid horizontal lines that are directly adjacent
# probably have the h_lines thing place them as it goes, placing the earliest it can (have only the first column be random)

for vl in range(v_lines_num-1): # -1 to prevent H lines on last v line
    # x = rect_origin.x+(vl*cell_width)
    x = v_positions[vl][0].x
    y = rect_origin.y
    h_lines = randrange(*h_lines_minmax)
    for hl in range(h_lines):
        ly = y
        y += randrange(*h_lines_range)
        if y > rect_origin.y+rect_y - h_lines_range[0]: # do not place a horizontal line if it will be lower than lowest possible
            remaining = rect_origin.y+rect_y-ly
            if remaining > h_lines_range[1]:
                y = (remaining//2) + ly # if the remaining cell size would be larger than allowed, split it in half
                # print('half on col ' + str(vl))
            else:
                break
        nl1 = Vector2(x, y)
        nl2 = Vector2(x+cell_width,y)
        h_positions += [(nl1, nl2)]

#TODO: fix the corner edges           
top_h_line = [(Vector2(rect_origin.x, rect_origin.y), Vector2(rect_origin.x+rect_x, rect_origin.y))]
bottom_h_line = [(Vector2(rect_origin.x, rect_origin.y+rect_y), Vector2(rect_origin.x+rect_x, rect_origin.y+rect_y))]

h_positions += top_h_line + bottom_h_line

#TODO: change this to be one dict and simplify - there is an autocompletion bug when doing it this way
# vertical and horizontal trail lines
# vt_lines = {} #{x:[(startY, endY)]}
# ht_lines = {} #{y:[(startX, endX)]}

# def add_t_line(num, start, end, type):
#     if type == 'v': 
#         d = vt_lines
#     elif type == 'h': 
#         d = ht_lines
#     else:
#         return
#     new = (round(start), round(end))
#     n = round(num)
#     if n not in d:
#         d[n] = new
#     old = (d[n][0], d[n][1])

#     d[n] = (
#         min(*new, *old),
#         max(*new, *old)
#     )


# vt_lines = {} #{x:[y1, y2, y3, y4...]}
# ht_lines = {} #{y:[(startX, endX)]}

# def add_trail(start_x, start_y, end_x, end_y):
#     # if the start_y == the last end_y, continue the same line

#     sx, sy = round(start_x), round(start_y)
#     ex, ey = end_x, end_y

#     vt_lines.setdefault(sx, [start_y, end_y])#.extend([start_y, end_y])
#     # vt_lines[sx].sort()

#     for i, y in enumerate(vt_lines[sx]):
#         if start_y == y:
#             vt_lines[sx][i] = end_y
#             return
    
#     vt_lines[sx].extend([start_y, end_y])

    # # reverse[]
    # # s_ys, e_ys = zip(*vt_lines[sx])
    # for i, y in list(enumerate(vt_lines[sx]))[::-1]: # needs reversed so elements can be deleted without changing index values
    #     if i % 2 != 0 or i < 1:
    #         continue
    #     # if y <= vt_lines[sx][i-1]:
    #     #     pass

    #     if y == vt_lines[sx][i-1]:
    #         del vt_lines[sx][i-1:i+1]


    # pass

    #     # for vt_sy, vt_ey in vt_lines[sx]:
    #     #     if vt_sy <= sy <= vt_ey: # if point is where in the existing line, extend it
    #     #         vt_lines[sx][1] = ey
    #     #     else:
    #     #         vt_lines[




# trails = {}

# def add_trail(start_x, start_y, end_x, end_y):
    # trails.setdefault(Vector2(start_x, start_y), Vector2(end_x, end_y))
    # start, end = Vector2(round(start_x), round(start_y)), Vector2(round(end_x), round(end_y))
    # if start in trails:
    #     trails[start] = end
    #     print(f'update trail: {start}, {end}')
    # else:
    #     trails[end] = start


    # trails.append((Vector2(start_x, start_y), Vector2(end_x, end_y)))

    # for t in trails:
    #     if t[1].x == start.x and t[1].y == start.y:
    #         t[1].x = end.x
    #         t[1].y = end.y
    #         print(f'update trail: {end.x}, {end.y}')
    #         return

    # trails.append((Vector2(start_x, start_y), Vector2(end_x, end_y)))
    # pass


# new trail process

# determine whether player is going the same direction, changed, or started
# same direction: get the last trail and extend it 

trail_points = []


class Player():
    def __init__(self, x, y, w, h) -> None:
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
            for vl in v_positions:
                if round(new_x) == vl[0].x and vl[0].y <= new_y <= vl[1].y:
                    self.current_vline = vl
                    y_move = True
                    self.pos.x = vl[0].x
                    self.pos.y = new_y
                    self.move_dir.y = self.direction.y
                    self.move_dir.x = 0
                    break
        
        if new_x != self.pos.x:
            for hl in h_positions:
                if round(new_y) == hl[0].y and hl[0].x <= new_x <= hl[1].x:
                    self.current_hline = hl
                    x_move = True
                    if not y_move:
                        self.pos.y = hl[0].y # keeps player on H line when trying to go on vertical inner line
                        self.pos.x = new_x
                    self.move_dir.x = self.direction.x
                    self.move_dir.y = 0
                    break


        movedir_change = self.previous_dir.x != self.move_dir.x or self.previous_dir.y != self.move_dir.y

        
        stopped = self.move_dir.x == 0 and self.move_dir.y == 0
        started = self.previous_dir.x == 0 and self.previous_dir.y == 0

        # effectively determines if the player just turned and sets the player position to the intersection of the two lines they are on 
        # this is to prevent the trail from being diagonal (possible if the player position has a decimal on both axes)
        if movedir_change and self.current_hline and self.current_vline and not (stopped or started):
            self.pos.y = self.current_hline[0].y
            self.pos.x = self.current_vline[0].x
        

        if self.pos.x % 1 != 0 and self.pos.y % 1 != 0: # if this triggers, then diagonal trails are possible (bad!)
            pass
        
        if self.move_dir.x != 0 and self.move_dir.y != 0:
            pass
        

        # print(old_x, old_y)
        new_point = Vector2(new_x, new_y) # current position
        # print(new_x, new_y)
        # debug_catch()

        if movedir_change: # when the movement direction changes, update the trail points and set the current trail to current position
            # debug_catch()
            last_point = Vector2(self.pos.x, self.pos.y)
            # if self.current_hline:
            #     last_point.y = self.current_hline[0].y
            # if self.current_vline:
            #     last_point.x = self.current_vline[0].x

            trail_points.append(last_point)
            if len(trail_points) > 1 and last_point.x != trail_points[-2].x and last_point.y != trail_points[-2].y:
                print(f'mismatch in trail points: {last_point.x, last_point.y} AND {trail_points[-2].x, trail_points[-2].y}')
            self.cur_trail = [new_point, new_point]

        if self.move_dir.x != 0 or self.move_dir.y != 0: # update the current trail's end point whenever the player moves
            self.cur_trail[1] = new_point

    def draw(self):
        self.drawn_pos = vector2_add(Vector2(round(self.pos.x), round(self.pos.y)), self.drawn_offset)
        draw_rectangle_v(self.drawn_pos, self.size, GREEN)



player = Player(rect_origin.x, rect_origin.y+rect_y, 20, 20)



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
        'Trail points': len(trail_points)
    }
    if is_key_pressed(debug_key):
        debug_mode = not debug_mode



    player.update()

    begin_drawing()
    clear_background(BLACK)

    # Draw the grid thing
    for p in v_positions+h_positions:
        draw_line_ex(*p,line_thickness, RED)

    #draw player

    # for start, end in trails.items():
    #     draw_line_ex(Vector2(*start), Vector2(*end), line_thickness, YELLOW)
    if player.cur_trail:
        # print(player.cur_trail[0].x, player.cur_trail[0].y)
        draw_spline_segment_linear(player.cur_trail[0], player.cur_trail[1], line_thickness, YELLOW)
    draw_spline_linear(trail_points, len(trail_points), line_thickness, YELLOW)


    player.draw()


    if debug_mode:
        draw_text('\n'.join([f'{k}: {v}' for k, v in debug_values.items()]), 0, 0, 20, WHITE)
        if player.current_vline:
            draw_line_v(player.current_vline[0], player.current_vline[1],GREEN)
        if player.current_hline:
            draw_line_v(player.current_hline[0], player.current_hline[1],GREEN)
        
        debug_catch()

    # draw_fps(0,0)
    
    end_drawing()

close_window()