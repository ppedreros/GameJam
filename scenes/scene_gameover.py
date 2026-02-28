import math
from raylibpy import *
from utils.constants import SCREEN_WIDTH, SCREEN_HEIGHT

class GameOverScene:
    def __init__(self, game, final_score):
        self.game = game
        self.final_score = final_score

    def update(self, dt):
        if is_key_pressed(KEY_ENTER):
            from scenes.scene_gameplay import GameplayScene
            self.game.change_scene(GameplayScene(self.game))

    def draw(self):
        # We don't call clear_background here if we want the previous frame 
        # to stay behind an overlay, but since Raylib clears every frame,
        # we realistically must re-draw or just accept a black background.
        # So we just draw a solid color
        clear_background(fade(BLACK, 0.8))
        
        panel_w = 400
        panel_h = 300
        panel_x = SCREEN_WIDTH//2 - panel_w//2
        panel_y = SCREEN_HEIGHT//2 - panel_h//2
        
        draw_rectangle(panel_x, panel_y, panel_w, panel_h, Color(40, 40, 60, 255))
        draw_rectangle_lines(panel_x, panel_y, panel_w, panel_h, RAYWHITE)
        
        text1 = "GAME OVER"
        text2 = f"Final Score: {self.final_score}"
        text3 = "Press ENTER to restart"
        
        draw_text(text1, SCREEN_WIDTH//2 - measure_text(text1, 50)//2, panel_y + 40, 50, RED)
        draw_text(text2, SCREEN_WIDTH//2 - measure_text(text2, 30)//2, panel_y + 130, 30, WHITE)
        
        pulse = (math.sin(get_time() * 5.0) + 1.0) / 2.0
        pulse_color = fade(YELLOW, 0.5 + 0.5 * pulse)
        
        draw_rectangle(SCREEN_WIDTH//2 - measure_text(text3, 20)//2 - 20, panel_y + 210, measure_text(text3, 20) + 40, 40, pulse_color)
        draw_text(text3, SCREEN_WIDTH//2 - measure_text(text3, 20)//2, panel_y + 220, 20, BLACK)
