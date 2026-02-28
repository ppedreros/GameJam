from pyray import Vector3, DARKGREEN, Color

class Platform3D:
    def __init__(self, x, z, directions, modifier=None, is_battle=False, is_inverted=False, is_swap=False):
        self.pos = Vector3(x, 0.0, z)
        self.size = Vector3(3.0, 1.0, 3.0)
        self.color = Color(80, 50, 150, 255)
        
        # directions can be a single int or a tuple/list
        if isinstance(directions, int):
            self.directions = (directions,)
        else:
            self.directions = tuple(sorted(directions))
        
        # Keep .direction as alias for backwards compatibility
        self.direction = self.directions[0]
        
        self.modifier = modifier   # "screen_swap", "darkness", etc.
        self.is_battle = is_battle
        self.is_inverted = is_inverted
        self.is_swap = is_swap
        
        if is_battle:
            self.color = Color(255, 215, 0, 255)   # gold
        if is_swap:
            self.color = Color(255, 105, 180, 255)  # hot pink
