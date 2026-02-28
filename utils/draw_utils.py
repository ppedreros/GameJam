from pyray import *
from .constants import DIR_UP, DIR_DOWN, DIR_RIGHT, DIR_LEFT

def get_direction_vector(direction):
    # Only going forward now
    return Vector3(0, 0, 4.0)

def draw_arrow(platform):
    dirs = platform.directions
    if len(dirs) == 1:
        _draw_single_arrow(platform.pos, dirs[0], 0, getattr(platform, 'is_inverted', False))
    else:
        _draw_single_arrow(platform.pos, dirs[0], -0.6, getattr(platform, 'is_inverted', False))
        _draw_single_arrow(platform.pos, dirs[1], 0.6, getattr(platform, 'is_inverted', False))

def _draw_single_arrow(plat_pos, direction, offset_x, is_inverted=False):
    # Draw a clear, recognizable 3D arrow made of boxes
    pos = Vector3(plat_pos.x + offset_x, plat_pos.y + 0.6, plat_pos.z)
    
    shaft_color = RED if is_inverted else WHITE
    tip_color = WHITE if is_inverted else RED
    
    # Base dimensions for the arrow shaft
    shaft_width = 0.2
    shaft_height = 0.2
    shaft_length = 1.0
    
    if direction == DIR_UP:
        # Shaft pointing Z-forward
        draw_cube(pos, shaft_width, shaft_height, shaft_length, shaft_color)
        # Arrowhead (V-shape using two angled boxes)
        # Approximated by placing boxes at the end
        front = Vector3(pos.x, pos.y, pos.z - shaft_length/2)
        draw_cube(Vector3(front.x - 0.2, front.y, front.z + 0.2), 0.4, 0.2, 0.1, shaft_color)
        draw_cube(Vector3(front.x + 0.2, front.y, front.z + 0.2), 0.4, 0.2, 0.1, shaft_color)
        draw_cube(front, 0.3, 0.2, 0.3, tip_color) # Tip
        
    elif direction == DIR_DOWN:
        # Shaft pointing Z-backward
        draw_cube(pos, shaft_width, shaft_height, shaft_length, shaft_color)
        back = Vector3(pos.x, pos.y, pos.z + shaft_length/2)
        draw_cube(Vector3(back.x - 0.2, back.y, back.z - 0.2), 0.4, 0.2, 0.1, shaft_color)
        draw_cube(Vector3(back.x + 0.2, back.y, back.z - 0.2), 0.4, 0.2, 0.1, shaft_color)
        draw_cube(back, 0.3, 0.2, 0.3, tip_color)
        
    elif direction == DIR_RIGHT:
        # Shaft pointing X-right
        draw_cube(pos, shaft_length, shaft_height, shaft_width, shaft_color)
        right = Vector3(pos.x + shaft_length/2, pos.y, pos.z)
        draw_cube(Vector3(right.x - 0.2, right.y, right.z - 0.2), 0.1, 0.2, 0.4, shaft_color)
        draw_cube(Vector3(right.x - 0.2, right.y, right.z + 0.2), 0.1, 0.2, 0.4, shaft_color)
        draw_cube(right, 0.3, 0.2, 0.3, tip_color)
        
    elif direction == DIR_LEFT:
        # Shaft pointing X-left
        draw_cube(pos, shaft_length, shaft_height, shaft_width, shaft_color)
        left = Vector3(pos.x - shaft_length/2, pos.y, pos.z)
        draw_cube(Vector3(left.x + 0.2, left.y, left.z - 0.2), 0.1, 0.2, 0.4, shaft_color)
        draw_cube(Vector3(left.x + 0.2, left.y, left.z + 0.2), 0.1, 0.2, 0.4, shaft_color)
        draw_cube(left, 0.3, 0.2, 0.3, tip_color)

def draw_rounded_panel(x, y, width, height, bg_color, shadow_color=Color(0,0,0,100), shadow_offset=4, roundness=0.2, segments=10):
    """Draws a rounded rectangle with a soft drop shadow effect."""
    # Draw soft shadow using multiple passes
    if shadow_offset > 0:
        for i in range(3):
            alpha = int(shadow_color.a * (0.3 - i*0.1))
            shadow_step = Color(shadow_color.r, shadow_color.g, shadow_color.b, max(0, alpha))
            draw_rectangle_rounded(Rectangle(x + shadow_offset + i, y + shadow_offset + i, width, height), roundness, segments, shadow_step)
            
    # Draw main panel
    draw_rectangle_rounded(Rectangle(x, y, width, height), roundness, segments, bg_color)
    
def draw_rounded_panel_outline(x, y, width, height, color, roundness=0.2, segments=10, thickness=2):
    """Workaround for draw_rectangle_rounded_lines bug in raylibpy."""
    # Draw slightly larger outer rounded rect
    draw_rectangle_rounded(Rectangle(x, y, width, height), roundness, segments, color)
    # Draw slightly smaller inner rounded rect as "erase" using the parent background color
    # Wait, we can't erase if there is a complex background. 
    # Let's just draw 4 thin rectangles along the edges for a pseudo-outline instead of True rounded lines
    # It won't have rounded corners but it's safe.
    draw_rectangle(int(x), int(y), int(width), thickness, color) # Top
    draw_rectangle(int(x), int(y + height - thickness), int(width), thickness, color) # Bottom
    draw_rectangle(int(x), int(y), thickness, int(height), color) # Left
    draw_rectangle(int(x + width - thickness), int(y), thickness, int(height), color) # Right
    
def draw_text_shadow(text, x, y, font_size, color, shadow_color=Color(0,0,0,150), shadow_offset=2):
    """Draws text with a drop shadow for better legibility."""
    draw_text(text, x + shadow_offset, y + shadow_offset, font_size, shadow_color)
    draw_text(text, x, y, font_size, color)

