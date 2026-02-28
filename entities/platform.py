from pyray import Vector3, DARKGREEN, Color

class Platform3D:
    def __init__(self, x, z, directions, is_battle=False, is_inverted=False, is_swap=False):
        self.pos = Vector3(x, 0.0, z)
        self.size = Vector3(3.0, 1.0, 3.0) # Unified size
        # A nice sleek violet/teal color for the platforms instead of basic DARKGREEN
        self.color = Color(80, 50, 150, 255)
        self.is_battle = is_battle
        if is_battle:
            # Cute gold color for battle tile
            self.color = Color(255, 215, 0, 255)  
        if is_swap:
            # Hot Pink color for swap tile
            self.color = Color(255, 105, 180, 255)
        if isinstance(directions, int):
            self.directions = (directions,)
        else:
            self.directions = tuple(sorted(directions))
        self.is_inverted = is_inverted
        self.is_swap = is_swap
