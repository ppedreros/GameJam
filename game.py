from scenes.scene_gameplay import GameplayScene

class Game:
    def __init__(self):
        self.current_scene = GameplayScene(self)
        
    def change_scene(self, scene):
        self.current_scene = scene
        
    def update(self, dt):
        if self.current_scene:
            self.current_scene.update(dt)
            
    def draw(self):
        if self.current_scene:
            self.current_scene.draw()