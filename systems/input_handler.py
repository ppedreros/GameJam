from raylibpy import is_key_pressed, KEY_UP, KEY_W, KEY_RIGHT, KEY_D, KEY_DOWN, KEY_S, KEY_LEFT, KEY_A
from utils.constants import DIR_UP, DIR_RIGHT, DIR_DOWN, DIR_LEFT

def get_pressed_direction():
    if is_key_pressed(KEY_UP) or is_key_pressed(KEY_W): return DIR_UP
    if is_key_pressed(KEY_RIGHT) or is_key_pressed(KEY_D): return DIR_RIGHT
    if is_key_pressed(KEY_DOWN) or is_key_pressed(KEY_S): return DIR_DOWN
    if is_key_pressed(KEY_LEFT) or is_key_pressed(KEY_A): return DIR_LEFT
    return -1
