from scenes.scene_menu import MenuScene

class Game:
    def __init__(self):
        self.current_scene = MenuScene(self)
        
    def change_scene(self, scene):
        self.current_scene = scene
        
    def update(self, dt):
        if self.current_scene:
            self.current_scene.update(dt)
            
    def draw(self):
        if self.current_scene:
            self.current_scene.draw()