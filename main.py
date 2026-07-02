from pyray import *
import raylib as rl
from player import Player
from grid import Grid
from trail import Trail
from enemy import Enemy


class Game():
    def __init__(self) -> None:
        window_w, window_h = 1080, 720

        init_window(window_w, window_h, 'amidar')
        set_exit_key(rl.KEY_ESCAPE)
        self.debug_key = rl.KEY_F3
        self.debug_mode = True
        # set_target_fps(144)
        # set_target_fps(1)

        self.grid = Grid(window_w, window_h)
        self.player = Player(self.grid.rect_origin.x, self.grid.rect_origin.y+self.grid.height, 20, 20, self.grid.v_positions[0], self.grid)
        self.trail = Trail(self.player, self.grid, BLUE)
        self.enemies = [Enemy(v[0].x, v[0].y+1, 20, 20, v, self.grid, self.player) for v in self.grid.v_positions]
        # enemies =  []



    def update(self):
        if is_key_pressed(self.debug_key):
            self.debug_mode = not self.debug_mode

        self.debug_values = {
            'FPS':get_fps(),
            'X':self.player.pos.x, 
            'Y':self.player.pos.y,
            'Drawn X':self.player.drawn_pos.x,
            'Drawn Y':self.player.drawn_pos.y,
            'Intersection':(self.player.intersection_point.x,self.player.intersection_point.y),
            # 'Line intersection':(self.player.current_hline[0].y if self.player.current_hline),
            # 'Trail': [
            #     (p.x, p.y) for p in trail.points
            # ],
            # 'Trail points': len(trail.points),
            'Trail segments': '...'+str([l for l in self.trail.line_segments])[-50:],
            'Segment count': len(self.trail.line_segments),
            'Incomplete count': len(self.trail.line_segments_incomplete),
            'Current trail':((self.player.cur_trail[0].x, self.player.cur_trail[0].y), (self.player.cur_trail[1].x, self.player.cur_trail[1].y)),
            'Move direction':(self.player.move_dir.x, self.player.move_dir.y),
            'Complete rects':[k for k,v in self.grid.rect_corners.items() if v['complete']],
            'Enemy collisions':self.player.enemy_collisions,
            'Hit cooldown':self.player.hit_cooldown.time_left
        }
        self.player.update()
        self.trail.update()
        for e in self.enemies:
            e.update()

    def draw(self):
        # Draw the grid thing
        self.grid.draw()
        self.trail.draw()
        self.player.draw()
        for e in self.enemies:
            e.draw()


        if self.debug_mode:
            draw_text('\n'.join([f'{k}: {v}' for k, v in self.debug_values.items()]), 0, 0, 20, WHITE)
            if self.player.current_line:
                draw_line_ex(self.player.current_line[0], self.player.current_line[1], 2.0, GREEN)
            # if self.player.current_hline:
            #     draw_line_v(self.player.current_hline[0], self.player.current_hline[1],GREEN)
            draw_circle_v(self.player.intersection_point, 8.0, ORANGE)
            if self.trail.last_incomplete_segment != ((),()):
                draw_line_ex(
                    Vector2(self.trail.last_incomplete_segment[0][0],self.trail.last_incomplete_segment[0][1]),
                    Vector2(self.trail.last_incomplete_segment[1][0],self.trail.last_incomplete_segment[1][1]),
                    4.0, PURPLE)

            for k, v in self.grid.rect_corners.items():
                draw_circle(int(k[0]), int(k[1]), 3.0, PURPLE)
            for x, y in self.grid.intersections:
                draw_circle(int(x), int(y), 1.5, WHITE)


    def run(self):
        while not window_should_close():
            self.update()
            begin_drawing()
            clear_background(BLACK)
            self.draw()
            end_drawing()


if __name__ == "__main__":
    game = Game()
    game.run()

close_window()