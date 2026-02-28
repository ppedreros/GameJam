from raylibpy import Vector3, DARKGREEN

class Platform3D:
    def __init__(self, x, z, direction):
        self.pos = Vector3(x, 0.0, z)
        self.size = Vector3(3.0, 1.0, 3.0) # Unified size
        self.color = DARKGREEN
        self.direction = direction # The key needed to jump FROM this platform
