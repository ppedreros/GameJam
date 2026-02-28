from pyray import Vector3, RED

class Player3D:
    def __init__(self):
        self.pos = Vector3(0.0, 2.0, 0.0)
        self.size = Vector3(1.0, 1.0, 1.0)
        self.color = RED
        self.score = 0
        
        # Jump animation variables
        self.is_jumping = False
        self.jump_start_pos = Vector3(0,0,0)
        self.jump_target_pos = Vector3(0,0,0)
        self.jump_progress = 0.0 # 0.0 to 1.0
