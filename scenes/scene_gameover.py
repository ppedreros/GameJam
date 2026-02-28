import math
from pyray import *
from utils.constants import SCREEN_WIDTH, SCREEN_HEIGHT
from utils.draw_utils import draw_rounded_panel, draw_rounded_panel_outline, draw_text_shadow

class GameOverScene:
    def __init__(self, game, winner, p1_score, p2_score, p1_combo=0, p2_combo=0, singleplayer=False):
        self.game = game
        self.winner = winner
        self.p1_score = p1_score
        self.p2_score = p2_score
        self.p1_combo = p1_combo
        self.p2_combo = p2_combo
        self.singleplayer = singleplayer
        self.enter_time = get_time()

    def update(self, dt):
        if get_time() - self.enter_time > 0.5 and is_key_pressed(KEY_ENTER):
            from scenes.scene_menu import MenuScene
            self.game.change_scene(MenuScene(self.game))

    def draw(self):
        # Frosted glass overlay
        draw_rectangle(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, fade(BLACK, 0.75))
        
        if self.singleplayer:
            self._draw_singleplayer()
        else:
            self._draw_multiplayer()
        
        # Restart button (shared)
        text3 = "Press ENTER to return to menu"
        t3_w = measure_text(text3, 20)
        
        pulse = (math.sin(get_time() * 6.0) + 1.0) / 2.0
        btn_w = t3_w + 60
        btn_h = 44
        btn_x = SCREEN_WIDTH // 2 - btn_w // 2
        btn_y = SCREEN_HEIGHT - 100
        
        draw_rounded_panel(btn_x, btn_y, btn_w, btn_h, fade(YELLOW, 0.15 + 0.35 * pulse), shadow_offset=0, roundness=0.5)
        draw_rounded_panel_outline(btn_x, btn_y, btn_w, btn_h, fade(YELLOW, 0.5 + 0.3 * pulse), segments=10, thickness=2)
        draw_text_shadow(text3, SCREEN_WIDTH // 2 - t3_w // 2, btn_y + 12, 20, RAYWHITE)

    def _draw_singleplayer(self):
        panel_w = 400
        panel_h = 300
        panel_x = SCREEN_WIDTH // 2 - panel_w // 2
        panel_y = SCREEN_HEIGHT // 2 - panel_h // 2 - 20
        
        draw_rounded_panel(panel_x, panel_y, panel_w, panel_h, fade(Color(20, 25, 45, 255), 0.95), shadow_offset=12, roundness=0.15, segments=20)
        draw_rounded_panel_outline(panel_x, panel_y, panel_w, panel_h, fade(RAYWHITE, 0.1), segments=20, thickness=2)
        
        # Title
        text1 = "GAME OVER"
        t1_w = measure_text(text1, 50)
        float_y = math.sin(get_time() * 2.5) * 5.0
        draw_text_shadow(text1, SCREEN_WIDTH // 2 - t1_w // 2, int(panel_y + 30 + float_y), 50, MAROON, shadow_color=fade(BLACK, 0.8), shadow_offset=4)
        
        # Divider
        div_w = 150
        draw_rectangle_gradient_h(SCREEN_WIDTH // 2 - div_w, int(panel_y + 95 + float_y), div_w, 2, fade(BLANK, 0.0), fade(WHITE, 0.5))
        draw_rectangle_gradient_h(SCREEN_WIDTH // 2, int(panel_y + 95 + float_y), div_w, 2, fade(WHITE, 0.5), fade(BLANK, 0.0))
        
        # Score
        score_label = "FINAL SCORE"
        sl_w = measure_text(score_label, 18)
        draw_text_shadow(score_label, SCREEN_WIDTH // 2 - sl_w // 2, panel_y + 120, 18, LIGHTGRAY)
        
        score_text = str(self.p1_score)
        st_size = 55
        st_w = measure_text(score_text, st_size)
        draw_text_shadow(score_text, SCREEN_WIDTH // 2 - st_w // 2, panel_y + 150, st_size, GOLD)
        
        # Best combo
        combo_text = f"Best Combo: x{self.p1_combo}"
        ct_w = measure_text(combo_text, 18)
        draw_text_shadow(combo_text, SCREEN_WIDTH // 2 - ct_w // 2, panel_y + 220, 18, Color(0, 200, 255, 255))

    def _draw_multiplayer(self):
        panel_w = 600
        panel_h = 350
        panel_x = SCREEN_WIDTH // 2 - panel_w // 2
        panel_y = SCREEN_HEIGHT // 2 - panel_h // 2 - 20
        
        draw_rounded_panel(panel_x, panel_y, panel_w, panel_h, fade(Color(20, 25, 45, 255), 0.95), shadow_offset=12, roundness=0.15, segments=20)
        draw_rounded_panel_outline(panel_x, panel_y, panel_w, panel_h, fade(RAYWHITE, 0.1), segments=20, thickness=2)
        
        # Title
        text1 = "GAME OVER"
        t1_w = measure_text(text1, 50)
        float_y = math.sin(get_time() * 2.5) * 5.0
        draw_text_shadow(text1, SCREEN_WIDTH // 2 - t1_w // 2, int(panel_y + 30 + float_y), 50, MAROON, shadow_color=fade(BLACK, 0.8), shadow_offset=4)
        
        # Divider
        div_w = 250
        draw_rectangle_gradient_h(SCREEN_WIDTH // 2 - div_w // 2, int(panel_y + 95 + float_y), div_w, 2, fade(BLANK, 0.0), fade(WHITE, 0.5))
        draw_rectangle_gradient_h(SCREEN_WIDTH // 2, int(panel_y + 95 + float_y), div_w, 2, fade(WHITE, 0.5), fade(BLANK, 0.0))
        
        # Winner announcement
        if self.winner != "Draw":
            w_text = f"{self.winner} Wins!"
            w_color = Color(0, 180, 255, 255) if self.winner == "Player 1" else Color(255, 80, 80, 255)
        else:
            w_text = "It's a Draw!"
            w_color = GRAY
        w_w = measure_text(w_text, 40)
        draw_text_shadow(w_text, SCREEN_WIDTH // 2 - w_w // 2, panel_y + 120, 40, w_color)
        
        # Score comparison
        col1_x = panel_x + 60
        col2_x = panel_x + panel_w - 200
        row_y = panel_y + 180
        
        draw_text_shadow("PLAYER 1", col1_x, row_y, 18, Color(0, 180, 255, 255))
        draw_text_shadow(f"Score: {self.p1_score}", col1_x, row_y + 30, 22, WHITE)
        draw_text_shadow(f"Best Combo: x{self.p1_combo}", col1_x, row_y + 60, 16, GOLD)
        
        draw_text_shadow("PLAYER 2", col2_x, row_y, 18, Color(255, 80, 80, 255))
        draw_text_shadow(f"Score: {self.p2_score}", col2_x, row_y + 30, 22, WHITE)
        draw_text_shadow(f"Best Combo: x{self.p2_combo}", col2_x, row_y + 60, 16, GOLD)
        
        # VS divider
        vs_x = SCREEN_WIDTH // 2
        draw_rectangle(vs_x - 1, row_y, 2, 80, fade(WHITE, 0.15))
        vs_w = measure_text("VS", 20)
        draw_text_shadow("VS", vs_x - vs_w // 2, row_y + 30, 20, fade(WHITE, 0.4))
