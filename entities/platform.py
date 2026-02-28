from pyray import Vector3, DARKGREEN, Color

class Platform3D:
    def __init__(self, x, z, directions, modifier=None, is_battle=False, is_inverted=False, is_swap=False, is_jump_pad=False):
        self.pos = Vector3(x, 0.0, z)
        self.size = Vector3(3.0, 1.0, 3.0)
        self.color = Color(80, 50, 150, 255)
        
        # directions can be a single int or a tuple/list. Jump pads might not have any
        if directions is None:
            self.directions = ()
        elif isinstance(directions, int):
            self.directions = (directions,)
        else:
            self.directions = tuple(sorted(directions))
        
        # Keep .direction as alias for backwards compatibility
        self.direction = self.directions[0] if self.directions else -1
        
        self.modifier = modifier   # "screen_swap", "darkness", etc.
        self.is_battle = is_battle
        self.battle_triggered = False
        self.is_inverted = is_inverted
        self.is_swap = is_swap
        self.is_jump_pad = is_jump_pad
        
        if is_battle:
            self.color = Color(255, 215, 0, 255)   # gold
        if is_swap:
            self.color = Color(255, 105, 180, 255)  # hot pink
        if is_jump_pad:
            self.color = Color(0, 255, 100, 255)   # neon green / emerald
