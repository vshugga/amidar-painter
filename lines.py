from pyray import *
import raylib as rl
from random import randrange


w, h = 1080, 720


init_window(w, h, 'amidar')
set_exit_key(rl.KEY_ESCAPE)

rect_x, rect_y = 600, 600
line_thickness = 8.0
rect_origin = Vector2((w/2)-(rect_x/2),(h/2)-(rect_y/2))
rect = Rectangle(rect_origin.x, rect_origin.y, rect_x, rect_y)

v_lines_num = 4 # number of inner vertical lines, excludes perimeter
h_lines_minmax = (4,6) # number of horizontal lines in a column
h_lines_range = (rect_y // 10, rect_y // 3) # min/max height of a cell

cell_width = rect_x/(v_lines_num+1)
v_positions = [(Vector2(rect_origin.x+cell_width*i,rect_origin.y), Vector2(rect_origin.x+cell_width*i,rect_origin.y+rect_y)) for i in range(1, v_lines_num+1)]
h_positions = []

#TODO: This algorithm needs rewritten to avoid horizontal lines that are directly adjacent 

for vl in range(v_lines_num+1):
    x = rect_origin.x+(vl*cell_width)
    y = rect_origin.y
    h_lines = randrange(*h_lines_minmax)
    for hl in range(h_lines):
        ly = y
        y += randrange(*h_lines_range)
        if y > rect_origin.y+rect_y - h_lines_range[0]: # do not place a horizontal line if it will be lower than lowest possible
            remaining = rect_origin.y+rect_y-ly
            if remaining > h_lines_range[1]:
                y = (remaining//2) + ly # if the remaining cell size would be larger than allowed, split it in half
                print('half on col ' + str(vl))
            else:
                break
        nl1 = Vector2(x, y)
        nl2 = Vector2(x+cell_width,y)
        h_positions += [(nl1, nl2)]
            

while not window_should_close():
    begin_drawing()
    draw_rectangle_lines_ex(rect, line_thickness, RED)
    for l in v_positions:
        draw_line_ex(*l,line_thickness, RED)

    for h in h_positions:
        draw_line_ex(*h, line_thickness, RED)

    clear_background(BLACK)
    end_drawing()

close_window()