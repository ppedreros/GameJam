from pyray import is_key_pressed, KEY_UP, KEY_W, KEY_RIGHT, KEY_D, KEY_DOWN, KEY_S, KEY_LEFT, KEY_A
from utils.constants import DIR_UP, DIR_RIGHT, DIR_DOWN, DIR_LEFT

def get_p1_pressed_direction():
    if is_key_pressed(KEY_W): return DIR_UP
    if is_key_pressed(KEY_D): return DIR_RIGHT
    if is_key_pressed(KEY_S): return DIR_DOWN
    if is_key_pressed(KEY_A): return DIR_LEFT
    return -1

def get_p2_pressed_direction():
    if is_key_pressed(KEY_UP): return DIR_UP
    if is_key_pressed(KEY_RIGHT): return DIR_RIGHT
    if is_key_pressed(KEY_DOWN): return DIR_DOWN
    if is_key_pressed(KEY_LEFT): return DIR_LEFT
    return -1

def get_p1_pressed_directions():
    dirs = []
    if is_key_pressed(KEY_W): dirs.append(DIR_UP)
    if is_key_pressed(KEY_D): dirs.append(DIR_RIGHT)
    if is_key_pressed(KEY_S): dirs.append(DIR_DOWN)
    if is_key_pressed(KEY_A): dirs.append(DIR_LEFT)
    return tuple(sorted(dirs))

def get_p2_pressed_directions():
    dirs = []
    if is_key_pressed(KEY_UP): dirs.append(DIR_UP)
    if is_key_pressed(KEY_RIGHT): dirs.append(DIR_RIGHT)
    if is_key_pressed(KEY_DOWN): dirs.append(DIR_DOWN)
    if is_key_pressed(KEY_LEFT): dirs.append(DIR_LEFT)
    return tuple(sorted(dirs))
