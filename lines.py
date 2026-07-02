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

class Player():
    def __init__(self, x, y, w, h) -> None:
        self.pos = Vector2(x, y)
        self.size = Vector2(w, h)
        # self.line_thickness = line_thickness
        self.direction = Vector2()
        self.speed = 100

    def move_x(self, x, y):
        for hl in h_positions:
            if -1 < hl[0].y - y < 1 and hl[0].x <= x <= hl[1].x:
                self.pos.x = x
                return

    def move_y(self, x, y):
        for vl in v_positions:
            if -1 < vl[0].x - x < 1 and vl[0].y <= y <= vl[1].y:
                self.pos.y = y
                return




    def update(self):
        self.direction.x = int(is_key_down(rl.KEY_RIGHT)) - int(is_key_down(rl.KEY_LEFT))
        self.direction.y = int(is_key_down(rl.KEY_DOWN)) - int(is_key_down(rl.KEY_UP))

        dt = get_frame_time()
        new_x = self.pos.x + (self.direction.x * self.speed * dt)
        new_y = self.pos.y + (self.direction.y * self.speed * dt)


        if new_x != self.pos.x:
            self.move_x(new_x, new_y)
        if new_y != self.pos.y:
            self.move_y(new_x, new_y)


    def draw(self):
        x_offset = 0#(self.size.x / -2) + (line_thickness / 2)
        y_offset = 0#(self.size.y / -2) - (line_thickness / 2) 
        p = Vector2(self.pos.x + x_offset, self.pos.y + y_offset)
        draw_rectangle_v(p, self.size, GREEN)



player = Player(rect_origin.x, rect_origin.y+rect_y, 20, 20)




while not window_should_close():
    player.update()

    begin_drawing()

    # Draw the grid thing
    # draw_rectangle_lines_ex(rect, line_thickness, RED)
    for l in v_positions:
        draw_line_ex(*l,line_thickness, RED)
    for h in h_positions:
        draw_line_ex(*h, line_thickness, RED)

    #draw player
    player.draw()

    clear_background(BLACK)
    end_drawing()

close_window()