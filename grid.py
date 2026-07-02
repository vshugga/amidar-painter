from pyray import *
import raylib as rl
from random import randrange

class Grid():
    def __init__(self, window_width, window_height, width=650, height=650, line_thickness=8.0, vertical_lines=6, h_lines_min=4, h_lines_max=6):
        self.width = width
        self.height = height 
        self.line_thickness = line_thickness
        self.rect_origin = Vector2((window_width/2)-(width/2),(window_height/2)-(height/2))
        self.round_scores = 50 # round rect scores to the nearest 50
        self.score_divisor = 100
        self.score_font_size = 5
        self.h_lines_range = (height // 10, width // 3) # min/max height of a cell
        self.cell_width = width/(vertical_lines-1)
        self.v_positions = [(
                Vector2(self.rect_origin.x+self.cell_width*i,self.rect_origin.y), 
                Vector2(self.rect_origin.x+self.cell_width*i,self.rect_origin.y+height)) 
            for i in range(vertical_lines)
        ]
        self.vertical_x_positions = [self.rect_origin.x+self.cell_width*i for i in range(vertical_lines)]


        self.h_positions = [] # pairs of vectors for lines left/right point
        #TODO: This algorithm needs rewritten to avoid horizontal lines that are directly adjacent
        # probably have the h_lines thing place them as it goes, placing the earliest it can (have only the first column be random)

        for vl in range(vertical_lines-1): # -1 to prevent H lines on last v line
            x = self.vertical_x_positions[vl]
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
                start_h = Vector2(x, y)
                end_h = Vector2(x+self.cell_width,y)
                self.h_positions += [(start_h, end_h)]


        #TODO: fix the corner edges           
        top_h_line = [(Vector2(self.rect_origin.x, self.rect_origin.y), Vector2(self.rect_origin.x+width, self.rect_origin.y))]
        bottom_h_line = [(Vector2(self.rect_origin.x, self.rect_origin.y+height), Vector2(self.rect_origin.x+width, self.rect_origin.y+height))]

        self.h_positions += top_h_line + bottom_h_line

        self.intersections = set()
        for v1, v2 in self.h_positions + self.v_positions:
            self.intersections.add((v1.x, v1.y))
            self.intersections.add((v2.x, v2.y))

        self.calculate_segments()
        self.calculate_scores()


    def calculate_segments(self):
        '''Calculates the segments required to be filled for each rectangle.'''
        # stores all the rect's corners as keys, the value is a dict where {"segments": list of segments, "complete": whether the rect is completed}
        self.rect_corners = {}
        bottom_y = self.rect_origin.y + self.height
        right_x = self.rect_origin.x + self.width
        
        # Find all rect's top left corners (unique)
        for start, end in self.v_positions+self.h_positions:
            if start.y >= bottom_y: #avoid adding the bottom hline!
                continue
            if start.x >= right_x:
                continue
            self.rect_corners[(start.x, start.y)] = {"segments":[],"complete":False}


        # go around the top left corner point, adding segments as we go (down, right, up, left)
        for (corner_x, corner_y), v in self.rect_corners.items():
            last_point = (corner_x, corner_y)
            x = corner_x
            y = corner_y

            # add = lambda x, y: (y := y + 1)

            while True: # get to the next square corner (or the bottom) directly below, adding segments along the way
                y += 1
                if (x, y) in self.intersections:
                    v["segments"].append((last_point, (x, y)))
                    last_point = (x, y)
                    if (x, y) in self.rect_corners or y >= bottom_y:
                        break
            
            v["height"] = y - corner_y # store this for drawing the complete rect later
            v["center"] = (corner_x + (self.cell_width / 2), corner_y + (v["height"] / 2))
            # since we are at the start of another square, just add the cell width to get the bottom right corner.
            bottom_right = (x+self.cell_width, y)
            if bottom_right not in self.intersections:
                raise Exception("Hey, this point is not valid! it needs to be an intersection")

            bottom_segment = (last_point, bottom_right)
            v["segments"].append(bottom_segment)

            last_point = bottom_right
            x += self.cell_width
            # y -= 1
            while True: # get to the top right square corner directly above, adding segments along the way
                y -= 1
                if (x, y) in self.intersections:
                    v["segments"].append(((x, y), last_point)) # Last point must come second to avoid order issues!
                    last_point = (x, y)
                    if y <= corner_y:
                        break

            if last_point not in self.intersections:
                raise Exception("Hey, this point is not valid! it needs to be an intersection")

            # add the final segment, which is from the starting corner to the right corner (which is last point)
            last_segment = ((corner_x, corner_y),last_point)
            v["segments"].append(last_segment)

        # stores every grid segment as a key, and the values a list of rects it belongs to (their upper right point)
        # used to quickly check rects for completion
        self.segment_rect_dict = {}

        for corner_point, v in self.rect_corners.items():
            segments = v["segments"]  
            for s in segments:
                self.segment_rect_dict.setdefault(s, []).append(corner_point)


    def calculate_scores(self): 
        for (corner_x, corner_y), v in self.rect_corners.items():
            v["score"] = v["height"] * self.cell_width 
            v["score"] = v["score"] / self.score_divisor
            v["score"] = round(v["score"] / self.round_scores) * self.round_scores


    def update_completion(self, segment, line_segments, player):
        '''Called whenever a complete segment is created to update completed rects.'''
        # get all the rects that this line is part of
        rects = self.segment_rect_dict[segment] # if this causes a keyerror at some point, its because the segment is invalid!
        for r in rects:
            rect = self.rect_corners[r]
            flag = False
            for seg in rect["segments"]:
                if seg not in line_segments:
                    flag = True
                    break
            if not flag:
                completed = rect["complete"] 
                if not completed:
                    rect["complete"] = True
                    player.score += self.rect_corners[r]["score"]
        

    def draw(self):
        for p in self.h_positions + self.v_positions:
            draw_line_ex(*p,self.line_thickness, RED) #TODO: use spline instead
            # draw_text('1', int(p[0].x), int(p[0].y), 5, WHITE)
            # draw_text('2', int(p[1].x), int(p[1].y), 5, WHITE)

        # fill in complete rects
        for rect, v in self.rect_corners.items():
            if v["complete"]:
                draw_rectangle(int(rect[0]), int(rect[1]), int(self.cell_width), int(v["height"]), WHITE) #TODO: ugly int conversions... use some other function?
            else:
                text = str(v["score"])
                text_size = measure_text(text, self.score_font_size)
                text_pos = (int((v["center"][0])-(text_size/2)),int(v["center"][1]))
                draw_text(text, *text_pos, self.score_font_size, WHITE)


        # intersections = self.v_positions + self.h_positions
        # draw_spline_linear(intersections, len(intersections), self.line_thickness, RED)