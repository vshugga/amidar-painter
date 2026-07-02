from pyray import *
import raylib as rl
from player import Player
from grid import Grid

class Trail():
    def __init__(self, player:Player, grid:Grid, color:Color) -> None:
        self.player = player
        self.points = [Vector2(player.pos.x, player.pos.y)]
        # self.last_intersection = Vector2(player.pos.x, player.pos.y)
        self.current_intersection = Vector2(player.pos.x, player.pos.y)
        self.line_segments = set()
        self.last_incomplete_segment = ((), ())
        self.line_segments_incomplete = set() 
        
        self.grid = grid
        self.color = color

    def on_incomplete_segment(self):
        '''if the player is on an incomplete segment (that is not the current trail), return it'''
        p = self.player
        for l in self.line_segments_incomplete: # TODO: optimization: loop through just the segments on current line.
            if l == self.last_incomplete_segment:
                continue
            xs = l[0][0], l[1][0]
            ys = l[0][1], l[1][1]
            if min(xs) <= p.drawn_pos.x <= max(xs) and min(ys) <= p.drawn_pos.y <= max(ys):
                return l
    

    def add_incomplete_segment(self):
        '''Creates an incomplete line segment and combines with the previous one if it exists, else start it at the last intersection.'''
        p = self.player

        end = (p.drawn_pos.x, p.drawn_pos.y)

        # this relies on being reset whenever player crosses an intersection (see update code) 
        last_start = self.last_incomplete_segment[0]
        last_end = self.last_incomplete_segment[1]        

        # do not add an incomplete segment if the new line would end in the previous segment (shortens the line)!
        if last_start and last_end:
            xs = last_start[0], last_end[0]
            ys = last_start[1], last_end[1]
            inside_last_x = min(xs) <= end[0] <= max(xs)
            inside_last_y = min(ys) <= end[1] <= max(ys)
            if inside_last_x and inside_last_y:
                return

        # if the last ending point exists, use it as the new starting point and remove the old segment (instead of the intersection)
        if last_end:
            start = last_start  
            self.line_segments_incomplete.discard(self.last_incomplete_segment) # discard will avoid errors when the segment was already removed
        else:
            start = (self.current_intersection.x, self.current_intersection.y)

        # do not store segments that are length 0
        if start == end:
            return

        segment = (start, end)
        self.line_segments_incomplete.add(segment)
        self.last_incomplete_segment = segment


    def add_complete_segment(self, start, end):
        for p in start, end:
            if p not in self.grid.intersections:
                raise Exception('The segment to be added is invalid! both points were not intersections.')

        # reorder start and end so they will always be consistent order when adding to the set.
        n_start = (min(start[0], end[0]),min(start[1], end[1]))
        n_end = (max(start[0], end[0]),max(start[1], end[1]))

        segment = (n_start, n_end)
        self.line_segments.add(segment)
        self.clean_incomplete_segments(segment)
        self.update_completion(segment)


    def combine_incomplete_segments(self, l1, l2):
        '''combine two incomplete segments into a whole one, which gets stored in self.line_segments'''

        xs = l1[0][0], l1[1][0], l2[0][0], l2[1][0]
        ys = l1[0][1], l1[1][1], l2[0][1], l2[1][1]
        min_x, max_x = min(xs), max(xs)
        min_y, max_y = min(ys), max(ys)
        start, end = (min_x, min_y), (max_x, max_y)
        
        if start == end: # they must differ!
            return 

        # the new segment must start/end on intersectinos (where start != end, done above)
        for s in start, end:
            if s not in self.grid.intersections:
                return

        self.add_complete_segment(start, end)


    def update(self):
        # return
        p = self.player

        # needs reset when player crosses an intersection so incomplete segments combine correctly in add_incomplete_segment()
        # if this isn't done, then incomplete segments would combine over intersections.
        if p.at_intersection:
            self.last_incomplete_segment = ((), ()) 
        
        # if the player is on an incomplete segment (that is not the current one) and not on an intersection, attempt to combine them
        on_incomplete = self.on_incomplete_segment()
        if on_incomplete and not p.at_intersection:
            current_trail = (p.cur_trail[0].x, p.cur_trail[0].y), (p.cur_trail[1].x, p.cur_trail[1].y) #TODO: don't like checking this every frame... is there a better way?
            self.combine_incomplete_segments(on_incomplete, current_trail)
            

        #if the player's intersection point changed, create and add a new line segment
        # if self.current_intersection.x != p.intersection_point.x or self.current_intersection.y != p.intersection_point.y:

        # if the player passed intersections, add line segments for each
        if p.passed_intersections and (self.current_intersection.x != p.intersection_point.x or self.current_intersection.y != p.intersection_point.y):
            intersections = [(self.current_intersection.x, self.current_intersection.y)]
            for intsc in p.passed_intersections:
                point = (intsc.x, intsc.y)
                intersections.append(point)
                
            for i, intsect in enumerate(intersections):
                if i < 1: continue
                start = intersections[i-1]
                end = intsect
                if start == end:
                    continue
                self.add_complete_segment(start, end)

            self.current_intersection = Vector2(p.intersection_point.x, p.intersection_point.y)
            p.cur_trail[0] = p.intersection_point
        # if players movement direction changed, store an incomplete line segment 
        # (also only if a full line segment WASNT made)
        elif p.movedir_change:
            self.add_incomplete_segment()


    def clean_incomplete_segments(self, seg):
        '''Remove all incomplete segments that are contained within a single complete one'''
        # new_incompletes = set()
        if seg not in self.line_segments:
            raise Exception('hey, this broke :/ - the seg line needs to be a valid complete segment.') 

        seg_xs = seg[0][0], seg[1][0]
        seg_ys = seg[0][1], seg[1][1]

        to_remove = set()

        for l in list(self.line_segments_incomplete):
            l_xs = l[0][0], l[1][0]
            l_ys = l[0][1], l[1][1]

            xs_contained = min(seg_xs) <= min(l_xs) <= max(l_xs) <= max(seg_xs)
            ys_contained = min(seg_ys) <= min(l_ys) <= max(l_ys) <= max(seg_ys)

            if xs_contained and ys_contained:
                self.line_segments_incomplete.remove(l)


    def update_completion(self, segment):
        '''Called whenever a complete segment is created to update completed rects.'''
        # get all the rects that this line is part of
        rects = self.grid.segment_rect_dict[segment] # if this causes a keyerror at some point, its because the segment is invalid!
        for r in rects:
            flag = False
            for seg in self.grid.rect_corners[r]["segments"]:
                if seg not in self.line_segments:
                    flag = True
                    break
            if not flag:
                self.grid.rect_corners[r]["complete"] = True


    def draw(self):
        if self.player.cur_trail:
            draw_spline_segment_linear(self.player.cur_trail[0], self.player.cur_trail[1], self.grid.line_thickness, self.color)

        # TODO: Use spline methods instead.
        for l in self.line_segments_incomplete:
            draw_line_ex(*l, 8.0, ORANGE)
        for l in self.line_segments:
            draw_line_ex(*l, 8.0, self.color) 