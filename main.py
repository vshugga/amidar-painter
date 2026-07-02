from pyray import *
import raylib as rl
from player import Player
from grid import Grid
from trail import Trail

window_w, window_h = 1080, 720

init_window(window_w, window_h, 'amidar')
set_exit_key(rl.KEY_ESCAPE)
debug_key = rl.KEY_F3
debug_mode = True
# set_target_fps(30)


def debug_catch():
    if is_key_down(rl.KEY_D):
        pass


grid = Grid(window_w, window_h)
player = Player(grid.rect_origin.x, grid.rect_origin.y+grid.height, 20, 20, grid)
trail = Trail(player, grid, BLUE)


while not window_should_close():

    debug_values = {
        'FPS':get_fps(),
        'X':player.pos.x, 
        'Y':player.pos.y,
        'Drawn X':player.drawn_pos.x,
        'Drawn Y':player.drawn_pos.y,
        'Intersection':(player.intersection_point.x,player.intersection_point.y),
        # 'Line intersection':(player.current_hline[0].y if player.current_hline),
        # 'Trail': [
        #     (p.x, p.y) for p in trail.points
        # ],
        'Trail points': len(trail.points),
        'Trail segments': '...'+str([l for l in trail.line_segments])[-50:],
        'Segment count': len(trail.line_segments),
        'Incomplete count': len(trail.line_segments_incomplete),
        'Current trail':((player.cur_trail[0].x, player.cur_trail[0].y), (player.cur_trail[1].x, player.cur_trail[1].y)),
        'Move direction':(player.move_dir.x, player.move_dir.y)
    }
    if is_key_pressed(debug_key):
        debug_mode = not debug_mode



    player.update()
    trail.update()

    begin_drawing()
    clear_background(BLACK)

    # Draw the grid thing
    grid.draw()
    trail.draw()
    player.draw()


    if debug_mode:
        draw_text('\n'.join([f'{k}: {v}' for k, v in debug_values.items()]), 0, 0, 20, WHITE)
        if player.current_line:
            draw_line_ex(player.current_line[0], player.current_line[1], 2.0, GREEN)
        # if player.current_hline:
        #     draw_line_v(player.current_hline[0], player.current_hline[1],GREEN)
        draw_circle_v(player.intersection_point, 8.0, ORANGE)
        if trail.last_incomplete_segment != ((),()):
            draw_line_ex(
                Vector2(trail.last_incomplete_segment[0][0], trail.last_incomplete_segment[0][1]),
                Vector2(trail.last_incomplete_segment[1][0],trail.last_incomplete_segment[1][1]),
                4.0, PURPLE)

        for k, v in grid.rect_corners.items():
            draw_circle(int(k[0]), int(k[1]), 3.0, PURPLE)
        debug_catch()

    end_drawing()

close_window()