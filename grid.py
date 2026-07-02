from pyray import *
import raylib as rl
from random import randrange

class Grid():
    def __init__(self, window_width, window_height, width=650, height=650, line_thickness=8.0, vertical_lines=6, h_lines_min=4, h_lines_max=6):
        self.width = width
        self.height = height 
        self.line_thickness = line_thickness
        self.rect_origin = Vector2((window_width/2)-(width/2),(window_height/2)-(height/2))
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

        self.intersections = set()
        for v1, v2 in self.h_positions + self.v_positions:
            self.intersections.add((v1.x, v1.y))
            self.intersections.add((v2.x, v2.y))
            


    def draw(self):
        for p in self.v_positions + self.h_positions:
            draw_line_ex(*p,self.line_thickness, RED) #TODO: use spline instead

        # intersections = self.v_positions + self.h_positions
        # draw_spline_linear(intersections, len(intersections), self.line_thickness, RED)