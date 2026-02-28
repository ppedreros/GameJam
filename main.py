import sys
import os
from pyray import *
from game import Game
from utils.constants import SCREEN_WIDTH, SCREEN_HEIGHT

def main():
    init_window(SCREEN_WIDTH, SCREEN_HEIGHT, "React & Jump 3D!")
    set_target_fps(60)

    game = Game()

    while not window_should_close():
        dt = get_frame_time()
        
        game.update(dt)
        
        begin_drawing()
        game.draw()
        end_drawing()

    close_window()
    return 0

if __name__ == '__main__':
    if len(sys.argv) >= 2 and isinstance(sys.argv[1], str):
        os.chdir(sys.argv[1])
    sys.exit(main())