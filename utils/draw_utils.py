from raylibpy import *
from .constants import DIR_UP, DIR_DOWN, DIR_RIGHT, DIR_LEFT

def get_direction_vector(direction):
    # Only going forward now
    return Vector3(0, 0, 4.0)

def draw_arrow(platform):
    # Draw a clear, recognizable 3D arrow made of boxes
    pos = Vector3(platform.pos.x, platform.pos.y + 0.6, platform.pos.z)
    color = WHITE
    
    # Base dimensions for the arrow shaft
    shaft_width = 0.2
    shaft_height = 0.2
    shaft_length = 1.0
    
    if platform.direction == DIR_UP:
        # Shaft pointing Z-forward
        draw_cube(pos, shaft_width, shaft_height, shaft_length, color)
        # Arrowhead (V-shape using two angled boxes)
        # Approximated by placing boxes at the end
        front = Vector3(pos.x, pos.y, pos.z - shaft_length/2)
        draw_cube(Vector3(front.x - 0.2, front.y, front.z + 0.2), 0.4, 0.2, 0.1, color)
        draw_cube(Vector3(front.x + 0.2, front.y, front.z + 0.2), 0.4, 0.2, 0.1, color)
        draw_cube(front, 0.3, 0.2, 0.3, RED) # Tip
        
    elif platform.direction == DIR_DOWN:
        # Shaft pointing Z-backward
        draw_cube(pos, shaft_width, shaft_height, shaft_length, color)
        back = Vector3(pos.x, pos.y, pos.z + shaft_length/2)
        draw_cube(Vector3(back.x - 0.2, back.y, back.z - 0.2), 0.4, 0.2, 0.1, color)
        draw_cube(Vector3(back.x + 0.2, back.y, back.z - 0.2), 0.4, 0.2, 0.1, color)
        draw_cube(back, 0.3, 0.2, 0.3, RED)
        
    elif platform.direction == DIR_RIGHT:
        # Shaft pointing X-right
        draw_cube(pos, shaft_length, shaft_height, shaft_width, color)
        right = Vector3(pos.x + shaft_length/2, pos.y, pos.z)
        draw_cube(Vector3(right.x - 0.2, right.y, right.z - 0.2), 0.1, 0.2, 0.4, color)
        draw_cube(Vector3(right.x - 0.2, right.y, right.z + 0.2), 0.1, 0.2, 0.4, color)
        draw_cube(right, 0.3, 0.2, 0.3, RED)
        
    elif platform.direction == DIR_LEFT:
        # Shaft pointing X-left
        draw_cube(pos, shaft_length, shaft_height, shaft_width, color)
        left = Vector3(pos.x - shaft_length/2, pos.y, pos.z)
        draw_cube(Vector3(left.x + 0.2, left.y, left.z - 0.2), 0.1, 0.2, 0.4, color)
        draw_cube(Vector3(left.x + 0.2, left.y, left.z + 0.2), 0.1, 0.2, 0.4, color)
        draw_cube(left, 0.3, 0.2, 0.3, RED)
