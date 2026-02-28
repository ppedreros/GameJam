import sys
import os
from pyray import *
from game import Game
from utils.constants import SCREEN_WIDTH, SCREEN_HEIGHT

def main():
    init_window(SCREEN_WIDTH, SCREEN_HEIGHT, "Combo Crush")
    set_target_fps(60)
    set_exit_key(0) # Disable ESC to close window

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
    if getattr(sys, 'frozen', False):
        # PyInstaller bundled executable
        # sys._MEIPASS points to the _internal folder in onedir mode where assets are
        os.chdir(sys._MEIPASS)
    else:
        # Development environment
        base_dir = os.path.dirname(os.path.abspath(__file__))
        if len(sys.argv) >= 2 and isinstance(sys.argv[1], str) and os.path.isdir(sys.argv[1]):
            pass # We leave the argv[1] chdir below just in case
        else:
            os.chdir(base_dir)

    if len(sys.argv) >= 2 and isinstance(sys.argv[1], str) and os.path.isdir(sys.argv[1]):
        os.chdir(sys.argv[1])
        
    sys.exit(main())