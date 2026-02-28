import math
import math
from pyray import *
from utils.constants import SCREEN_WIDTH, SCREEN_HEIGHT
from utils.draw_utils import draw_rounded_panel, draw_rounded_panel_outline, draw_text_shadow

class GameOverScene:
    def __init__(self, game, winner, p1_score, p2_score):
        self.game = game
        self.winner = winner
        self.p1_score = p1_score
        self.p2_score = p2_score

    def update(self, dt):
        if is_key_pressed(KEY_ENTER):
            from scenes.scene_gameplay import GameplayScene
            self.game.change_scene(GameplayScene(self.game))

    def draw(self):
        # Frosted glass overlay effect
        draw_rectangle(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, fade(BLACK, 0.7))
        
        panel_w = 560
        panel_h = 350
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
        div_w = 300
        draw_rectangle_gradient_h(SCREEN_WIDTH//2 - div_w//2, int(panel_y + 110 + float_y), div_w, 2, fade(BLANK, 0.0), fade(WHITE, 0.5))
        draw_rectangle_gradient_h(SCREEN_WIDTH//2, int(panel_y + 110 + float_y), div_w, 2, fade(WHITE, 0.5), fade(BLANK, 0.0))
        
        # Winner
        w_text = f"{self.winner} Wins!" if self.winner != "Draw" else "It's a Draw!"
        w_color = BLUE if self.winner == "Player 1" else (RED if self.winner == "Player 2" else GRAY)
        w_w = measure_text(w_text, 40)
        draw_text_shadow(w_text, SCREEN_WIDTH//2 - w_w//2, panel_y + 140, 40, w_color)
        
        # Scores
        p1_text = f"P1 Score: {self.p1_score}"
        p2_text = f"P2 Score: {self.p2_score}"
        draw_text_shadow(p1_text, panel_x + 60, panel_y + 200, 20, BLUE)
        draw_text_shadow(p2_text, panel_x + panel_w - measure_text(p2_text, 20) - 60, panel_y + 200, 20, RED)
        
        # Pulsating restart instruction
        text3 = "Press ENTER to restart"
        t3_w = measure_text(text3, 20)
        
        pulse = (math.sin(get_time() * 6.0) + 1.0) / 2.0
        btn_w = t3_w + 60
        btn_h = 44
        btn_x = SCREEN_WIDTH//2 - btn_w//2
        btn_y = panel_y + 260
        
        draw_rounded_panel(btn_x, btn_y, btn_w, btn_h, fade(YELLOW, 0.2 + 0.4 * pulse), shadow_offset=0, roundness=0.5)
        draw_rounded_panel_outline(btn_x, btn_y, btn_w, btn_h, fade(YELLOW, 0.6), segments=10, thickness=2)
        
        draw_text_shadow(text3, SCREEN_WIDTH//2 - t3_w//2, btn_y + 12, 20, RAYWHITE)
