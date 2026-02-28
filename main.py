import sys
import os
from pyray import *
from game import Game
from utils.constants import SCREEN_WIDTH, SCREEN_HEIGHT

def main():
    init_window(SCREEN_WIDTH, SCREEN_HEIGHT, "React & Jump 3D!") # type: ignore
    set_target_fps(60) # type: ignore

    game = Game()

    while not window_should_close(): # type: ignore
        dt = get_frame_time() # type: ignore
        
        game.update(dt)
        
        begin_drawing() # type: ignore
        game.draw()
        end_drawing() # type: ignore

    close_window() # type: ignore
    return 0

if __name__ == '__main__':
    if len(sys.argv) >= 2 and isinstance(sys.argv[1], str):
        os.chdir(sys.argv[1])
    sys.exit(main())