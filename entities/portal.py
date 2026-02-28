from pyray import Vector3, Color

class Portal3D:
    def __init__(self, x, y, z):
        self.pos = Vector3(x, y, z)
        # We will use darkness modifier for this portal specifically
        self.modifier = "darkness"
        self.radius = 1.0
        self.active = True
        
        # Color of the portal rings
        self.color = Color(30, 30, 40, 255) # Dark center
        self.ring_color = Color(150, 0, 255, 200) # Purple/Dark magic vibe
