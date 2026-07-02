from pyray import *
import raylib as rl
from random import randrange

w, h = 1080, 720

init_window(w, h, 'amidar')
set_exit_key(rl.KEY_ESCAPE)


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
        self.speed = 1000
        self.move_dir = Vector2() # actual direction after updates
        self.previous_dir = Vector2()
        self.cur_trail = None # trail that is drawn behind the player

    def update(self):
        self.direction.x = int(is_key_down(rl.KEY_RIGHT)) - int(is_key_down(rl.KEY_LEFT))
        self.direction.y = int(is_key_down(rl.KEY_DOWN)) - int(is_key_down(rl.KEY_UP))

        dt = get_frame_time()
        new_x = self.pos.x + (self.direction.x * self.speed * dt)
        new_y = self.pos.y + (self.direction.y * self.speed * dt)
        old_x = self.pos.x
        old_y = self.pos.y

        self.previous_dir.x = self.move_dir.x
        self.previous_dir.y = self.move_dir.y

        if new_x == old_x:
             self.move_dir.x = 0
        if old_y == new_y:
             self.move_dir.y = 0

        move_flag = False


        if new_y != self.pos.y:
            for vl in v_positions:
                # if -1 < vl[0].x - new_x < 1 and vl[0].y <= new_y <= vl[1].y:
                if round(new_x) == vl[0].x and vl[0].y <= new_y <= vl[1].y:
                    move_flag = True
                    self.pos.x = vl[0].x
                    self.pos.y = new_y
                    self.move_dir.y = self.direction.y
                    self.move_dir.x = 0
                    break
        
        if new_x != self.pos.x:
            for hl in h_positions:
                # if -1 < hl[0].y - new_y < 1 and hl[0].x <= new_x <= hl[1].x:
                if round(new_y) == hl[0].y and hl[0].x <= new_x <= hl[1].x:
                    if not move_flag:
                        self.pos.y = hl[0].y
                        move_flag = True
                    self.pos.x = new_x
                    self.move_dir.x = self.direction.x
                    self.move_dir.y = 0
                    break
        
        movedir_change = self.previous_dir.x != self.move_dir.x or self.previous_dir.y != self.move_dir.y


        # if movedir_change or self.cur_trail is None:
        #     print(f'move direction change from {self.previous_dir.x}, {self.previous_dir.y} to {self.move_dir.x}, {self.move_dir.y}')
        #     print(len(trails))
        #     trails[(old_x, old_y)] = (new_x, new_y)
        #     self.cur_trail = (old_x, old_y)
        
        # if self.move_dir.x != 0 or self.move_dir.y != 0:
        #     trails[self.cur_trail] = (new_x, new_y)
        last_point = Vector2(old_x, old_y)
        new_point = Vector2(new_x, new_y)
        if self.cur_trail is None:
            self.cur_trail = [last_point, new_point]

        if movedir_change: # when the movement direction changes, update the trail points and set the current trail to current position
            trail_points.append(last_point)
            self.cur_trail = [new_point, new_point]
        
        if self.move_dir.x != 0 or self.move_dir.y != 0: # update the current trail's end point whenever the player moves
            self.cur_trail[1] = new_point


    def draw(self):
        x_offset = (self.size.x / -2)# + (line_thickness / 2)
        y_offset = (self.size.y / -2)# - (line_thickness / 2) 
        p = Vector2(self.pos.x + x_offset, self.pos.y + y_offset)
        draw_rectangle_v(p, self.size, GREEN)



player = Player(rect_origin.x, rect_origin.y+rect_y, 20, 20)




while not window_should_close():
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


    

    # print(f"trails: {len(trails)} Player pos: {player.pos.x}, {player.pos.y}")

    # if player.move_dir.x != 0:
    #     print('move x') 
    # if player.move_dir.y != 0:
    #     print('move y')

    # print(player.move_dir.x, player.move_dir.y)

    player.draw()

    draw_fps(0,0)
    
    end_drawing()

close_window()