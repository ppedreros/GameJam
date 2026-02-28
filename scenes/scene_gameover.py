import math
import math
from raylibpy import *
from utils.constants import SCREEN_WIDTH, SCREEN_HEIGHT
from utils.draw_utils import draw_rounded_panel, draw_rounded_panel_outline, draw_text_shadow

class GameOverScene:
    def __init__(self, game, final_score):
        self.game = game
        self.final_score = final_score

    def update(self, dt):
        if is_key_pressed(KEY_ENTER):
            from scenes.scene_gameplay import GameplayScene
            self.game.change_scene(GameplayScene(self.game))

    def draw(self):
        # Frosted glass overlay effect
        draw_rectangle(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, fade(BLACK, 0.7))
        
        panel_w = 460
        panel_h = 320
        panel_x = SCREEN_WIDTH//2 - panel_w//2
        panel_y = SCREEN_HEIGHT//2 - panel_h//2
        
        # Soft glowing modal background
        draw_rounded_panel(panel_x, panel_y, panel_w, panel_h, fade(Color(30, 35, 55, 255), 0.95), shadow_offset=10, roundness=0.2, segments=20)
        # Inner bezel/reflection
        draw_rounded_panel_outline(panel_x, panel_y, panel_w, panel_h, fade(RAYWHITE, 0.15), segments=20, thickness=2)
        
        # Title with dramatic shadow and floating logic
        text1 = "GAME OVER"
        t1_w = measure_text(text1, 50)
        float_y = math.sin(get_time() * 2.5) * 6.0
        draw_text_shadow(text1, SCREEN_WIDTH//2 - t1_w//2, int(panel_y + 40 + float_y), 50, MAROON, shadow_color=fade(BLACK, 0.8), shadow_offset=4)
        
        # Divider line
        div_w = 200
        draw_rectangle_gradient_h(SCREEN_WIDTH//2 - div_w//2, int(panel_y + 110 + float_y), div_w, 2, fade(BLANK, 0.0), fade(WHITE, 0.5))
        draw_rectangle_gradient_h(SCREEN_WIDTH//2, int(panel_y + 110 + float_y), div_w, 2, fade(WHITE, 0.5), fade(BLANK, 0.0))
        
        # Score
        text2 = "Final Score"
        t2_w = measure_text(text2, 20)
        draw_text_shadow(text2, SCREEN_WIDTH//2 - t2_w//2, panel_y + 140, 20, LIGHTGRAY)
        
        score_str = str(self.final_score)
        score_w = measure_text(score_str, 60)
        draw_text_shadow(score_str, SCREEN_WIDTH//2 - score_w//2, panel_y + 165, 60, GOLD)
        
        # Pulsating restart instruction
        text3 = "Press ENTER to restart"
        t3_w = measure_text(text3, 20)
        
        pulse = (math.sin(get_time() * 6.0) + 1.0) / 2.0
        btn_w = t3_w + 60
        btn_h = 44
        btn_x = SCREEN_WIDTH//2 - btn_w//2
        btn_y = panel_y + 250
        
        draw_rounded_panel(btn_x, btn_y, btn_w, btn_h, fade(YELLOW, 0.2 + 0.4 * pulse), shadow_offset=0, roundness=0.5)
        draw_rounded_panel_outline(btn_x, btn_y, btn_w, btn_h, fade(YELLOW, 0.6), segments=10, thickness=2)
        
        draw_text_shadow(text3, SCREEN_WIDTH//2 - t3_w//2, btn_y + 12, 20, RAYWHITE)
