from pyray import Vector3, DARKGREEN, Color

class Platform3D:
    def __init__(self, x, z, direction):
        self.pos = Vector3(x, 0.0, z)
        self.size = Vector3(3.0, 1.0, 3.0) # Unified size
        # A nice sleek violet/teal color for the platforms instead of basic DARKGREEN
        self.color = Color(80, 50, 150, 255)
        self.direction = direction # The key needed to jump FROM this platform
