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

# vertical and horizontal trail lines
vt_lines = {} #{x:[(startY, endY)]}
ht_lines = {} #{y:[(startX, endX)]}

def add_t_line(num, start, end, type):
    if type == 'v': 
        d = vt_lines
    elif type == 'h': 
        d = ht_lines
    else:
        return
    new = (round(start), round(end))
    n = round(num)
    if n not in d:
        d[n] = new
    old = (d[n][0], d[n][1])

    d[n] = (
        min(*new, *old),
        max(*new, *old)
    )





# def add_trail(start_x, start_y, end_x, end_y):
#     '''Add a new trail to draw'''
#     trail_lines[(start_x, start_y)] = end_x, end_y


class Player():
    def __init__(self, x, y, w, h) -> None:
        self.pos = Vector2(x, y)
        self.size = Vector2(w, h)
        # self.line_thickness = line_thickness
        self.direction = Vector2()
        self.speed = 500

    def update(self):
        self.direction.x = int(is_key_down(rl.KEY_RIGHT)) - int(is_key_down(rl.KEY_LEFT))
        self.direction.y = int(is_key_down(rl.KEY_DOWN)) - int(is_key_down(rl.KEY_UP))

        dt = get_frame_time()
        new_x = self.pos.x + (self.direction.x * self.speed * dt)
        new_y = self.pos.y + (self.direction.y * self.speed * dt)
        old_x = self.pos.x
        old_y = self.pos.y

        if new_x != self.pos.x:
            for hl in h_positions:
                if -1 < hl[0].y - new_y < 1 and hl[0].x <= new_x <= hl[1].x:
                    self.pos.y = hl[0].y
                    # ht_lines[self.pos.y] = (self.pos.x, new_x)
                    add_t_line(self.pos.y, self.pos.x, new_x, 'h')
                    self.pos.x = new_x
                    break
        if new_y != self.pos.y:
            for vl in v_positions:
                if -1 < vl[0].x - new_x < 1 and vl[0].y <= new_y <= vl[1].y:
                    # self.pos.x = vl[0].x # for some reason this breaks movement to h lines
                    # vt_lines[self.pos.x] = (self.pos.y, new_y)
                    add_t_line(self.pos.x, self.pos.y, new_y, 'v')
                    self.pos.y = new_y
                    break
        
        # if old_x != self.pos.x or old_y != self.pos.y:
        #     add_trail(old_x, old_y, self.pos.x, self.pos.y)


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


    for x, ys in vt_lines.items():
        start_y, end_y = ys
        draw_line_ex(Vector2(x, start_y), Vector2(x, end_y), line_thickness, YELLOW)
    for y, xs in ht_lines.items():
        start_x, end_x = xs
        draw_line_ex(Vector2(start_x, y), Vector2(end_x, y), line_thickness, YELLOW)

    #draw player
    player.draw()

    draw_fps(0,0)
    
    end_drawing()

close_window()