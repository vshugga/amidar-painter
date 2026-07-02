from pyray import *
import raylib as rl

w, h = 1080, 720


init_window(w, h, 'amidar')
set_exit_key(rl.KEY_ESCAPE)

rect_size = Vector2(600, 600)
line_thickness = 8.0
rect_origin = Vector2((w/2)-(rect_size.x/2),(h/2)-(rect_size.y/2))
rect = Rectangle(rect_origin.x, rect_origin.y, rect_size.x, rect_size.y)

v_lines_num = 4
h_lines_minmax = (4,6) # number of horizontal lines in a column
h_lines_range = (rect_size.y/10, rect_size.y/3) # min/max height of a cell

cell_width = rect_size.x/(v_lines_num+1)
v_positions = [(Vector2(rect_origin.x+cell_width*i,rect_origin.y), Vector2(rect_origin.x+cell_width*i,rect_origin.y+rect_size.y)) for i in range(1, v_lines_num+1)]


while not window_should_close():
    begin_drawing()
    draw_rectangle_lines_ex(rect, line_thickness, RED)
    for l in v_positions:
        draw_line_ex(*l,line_thickness, RED)

    clear_background(BLACK)
    end_drawing()

close_window()