import math
from pyray import *
from utils.constants import SCREEN_WIDTH, SCREEN_HEIGHT
from utils.draw_utils import draw_rounded_panel, draw_rounded_panel_outline, draw_text_shadow

class GameOverScene:
    def __init__(self, game, winner, p1_score, p2_score, p1_combo=0, p2_combo=0, singleplayer=False, p1_color=None, p2_color=None, p1_crowns=0, p2_crowns=0):
        self.game = game
        self.winner = winner
        self.p1_score = p1_score
        self.p2_score = p2_score
        self.p1_combo = p1_combo
        self.p2_combo = p2_combo
        self.singleplayer = singleplayer
        self.p1_crowns = p1_crowns
        self.p2_crowns = p2_crowns
        # Final score = crowns * 25 + base score
        self.p1_final = p1_crowns * 25 + p1_score
        self.p2_final = p2_crowns * 25 + p2_score
        
        self.p1_color = p1_color if p1_color else Color(0, 180, 255, 255)
        self.p2_color = p2_color if p2_color else Color(255, 80, 80, 255)
        
        self.phase = 1 if singleplayer else 0
        self.enter_time = get_time()
        self.transition_alpha = 1.0
        
        self.camera = Camera3D()
        self.camera.position = Vector3(0.0, 3.0, -8.0)
        self.camera.target = Vector3(0.0, 0.0, 0.0)
        self.camera.up = Vector3(0.0, 1.0, 0.0)
        self.camera.fovy = 45.0
        self.camera.projection = CAMERA_PERSPECTIVE

    def update(self, dt):
        if self.transition_alpha > 0:
            self.transition_alpha -= dt * 2.0
            if self.transition_alpha < 0:
                self.transition_alpha = 0
                
        if get_time() - self.enter_time > 0.5:
            if self.phase == 0:
                if is_key_pressed(KEY_ENTER) and self.transition_alpha == 0:
                    self.phase = 1
                    self.transition_alpha = 1.0
            elif self.phase == 1:
                if is_key_pressed(KEY_SPACE):
                    # Restart same game mode
                    from scenes.scene_gameplay import GameplayScene
                    self.game.change_scene(GameplayScene(self.game, singleplayer=self.singleplayer))
                elif is_key_pressed(KEY_ENTER):
                    # Return to menu
                    from scenes.scene_menu import MenuScene
                    self.game.change_scene(MenuScene(self.game))

    def draw(self):
        # Clear background to prevent 3D elements from ghosting into a mess
        clear_background(Color(15, 20, 35, 255))
        
        if self.phase == 0:
            self._draw_winner_screen()
        else:
            if self.singleplayer:
                self._draw_singleplayer()
            else:
                self._draw_multiplayer()
        
        if self.phase == 0:
            text_enter = "Press ENTER to continue"
            t_w = measure_text(text_enter, 20)
            
            pulse = (math.sin(get_time() * 6.0) + 1.0) / 2.0
            btn_w = t_w + 60
            btn_h = 44
            btn_x = SCREEN_WIDTH // 2 - btn_w // 2
            btn_y = SCREEN_HEIGHT - 100
            
            draw_rounded_panel(btn_x, btn_y, btn_w, btn_h, fade(YELLOW, 0.15 + 0.35 * pulse), shadow_offset=0, roundness=0.5)
            draw_rounded_panel_outline(btn_x, btn_y, btn_w, btn_h, fade(YELLOW, 0.5 + 0.3 * pulse), segments=10, thickness=2)
            draw_text_shadow(text_enter, SCREEN_WIDTH // 2 - t_w // 2, btn_y + 12, 20, RAYWHITE)
        else:
            # Phase 1: Restart (SPACE) or Menu (ENTER)
            text_restart = "SPACE : Play Again"
            text_menu = "ENTER : Main Menu"
            
            tr_w = measure_text(text_restart, 20)
            tm_w = measure_text(text_menu, 20)
            
            pulse = (math.sin(get_time() * 6.0) + 1.0) / 2.0
            btn_w = max(tr_w, tm_w) + 80
            btn_h = 40
            
            # Left button: Play Again
            btn1_x = SCREEN_WIDTH // 2 - btn_w - 10
            btn_y = SCREEN_HEIGHT - 100
            
            draw_rounded_panel(btn1_x, btn_y, btn_w, btn_h, fade(LIME, 0.15 + 0.35 * pulse), shadow_offset=0, roundness=0.5)
            draw_rounded_panel_outline(btn1_x, btn_y, btn_w, btn_h, fade(LIME, 0.5 + 0.3 * pulse), segments=10, thickness=2)
            draw_text_shadow(text_restart, btn1_x + btn_w // 2 - tr_w // 2, btn_y + 10, 20, RAYWHITE)
            
            # Right button: Main Menu
            btn2_x = SCREEN_WIDTH // 2 + 10
            
            draw_rounded_panel(btn2_x, btn_y, btn_w, btn_h, fade(GRAY, 0.3), shadow_offset=0, roundness=0.5)
            draw_rounded_panel_outline(btn2_x, btn_y, btn_w, btn_h, fade(RAYWHITE, 0.3), segments=10, thickness=2)
            draw_text_shadow(text_menu, btn2_x + btn_w // 2 - tm_w // 2, btn_y + 10, 20, fade(RAYWHITE, 0.7))

        # Smooth Transition Overlay
        if self.transition_alpha > 0:
            draw_rectangle(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, fade(BLACK, self.transition_alpha))

    def _draw_winner_screen(self):
        t = get_time()
        
        # 3D Rotating Cube
        begin_mode_3d(self.camera)
        bob = math.sin(t * 3.0) * 0.5
        cube_pos = Vector3(0.0, bob, 0.0)
        
        if self.singleplayer:
            cube_color = self.p1_color
            win_text = "GAME OVER"
        else:
            if self.winner == "Player 1":
                cube_color = self.p1_color
                win_text = "PLAYER 1 WINS!"
            elif self.winner == "Player 2":
                cube_color = self.p2_color
                win_text = "PLAYER 2 WINS!"
            else:
                cube_color = GRAY
                win_text = "IT'S A DRAW!"
                
        # Draw Halo (an open ring above the head)
        glow = (math.sin(t * 8.0) + 1.0) / 2.0
        halo_y = bob + 1.5 + glow * 0.2
        if isinstance(cube_color, tuple):
            r, g, b = cube_color[0], cube_color[1], cube_color[2]
        else:
            r, g, b = cube_color.r, cube_color.g, cube_color.b
            
        halo_color = Color(r, g, b, int(150 + 100 * glow))
        draw_cylinder_wires(Vector3(0, halo_y, 0), 1.5, 1.5, 0.1, 12, halo_color)
        draw_cylinder_wires(Vector3(0, halo_y, 0), 1.6, 1.6, 0.1, 12, halo_color)  # Double wire for thickness
        
        draw_cube_v(cube_pos, Vector3(2.0, 2.0, 2.0), cube_color)
        draw_cube_wires_v(cube_pos, Vector3(2.0, 2.0, 2.0), WHITE)
        end_mode_3d()
        
        # 2D Text over the 3D scene
        float_y = math.sin(t * 2.5) * 5.0
        t1_w = measure_text(win_text, 60)
        draw_text_shadow(win_text, SCREEN_WIDTH // 2 - t1_w // 2, int(SCREEN_HEIGHT * 0.2 + float_y), 60, WHITE, shadow_color=fade(cube_color, 0.8), shadow_offset=6)

    def _draw_singleplayer(self):
        panel_w = 420
        panel_h = 330
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
        
        # Crowns row
        crown_label = f"♛ Crowns: {self.p1_crowns}  (+{self.p1_crowns * 25} pts)"
        cl_w = measure_text(crown_label, 18)
        draw_text_shadow(crown_label, SCREEN_WIDTH // 2 - cl_w // 2, panel_y + 115, 18, Color(255, 220, 80, 255))
        
        # Base score
        base_label = f"Platforms: {self.p1_score}"
        bl_w = measure_text(base_label, 16)
        draw_text_shadow(base_label, SCREEN_WIDTH // 2 - bl_w // 2, panel_y + 145, 16, LIGHTGRAY)
        
        # Final Score
        score_label = "TOTAL SCORE"
        sl_w = measure_text(score_label, 18)
        draw_text_shadow(score_label, SCREEN_WIDTH // 2 - sl_w // 2, panel_y + 172, 18, LIGHTGRAY)
        
        score_text = str(self.p1_final)
        st_size = 55
        st_w = measure_text(score_text, st_size)
        draw_text_shadow(score_text, SCREEN_WIDTH // 2 - st_w // 2, panel_y + 193, st_size, GOLD)
        
        # Best combo
        combo_text = f"Best Combo: x{self.p1_combo}"
        ct_w = measure_text(combo_text, 18)
        draw_text_shadow(combo_text, SCREEN_WIDTH // 2 - ct_w // 2, panel_y + 265, 18, Color(0, 200, 255, 255))

    def _draw_multiplayer(self):
        panel_w = 640
        panel_h = 380
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
        col1_x = panel_x + 50
        col2_x = panel_x + panel_w - 240
        row_y = panel_y + 180
        
        draw_text_shadow("PLAYER 1", col1_x, row_y, 18, Color(0, 180, 255, 255))
        draw_text_shadow(f"Platforms: {self.p1_score}", col1_x, row_y + 30, 18, WHITE)
        draw_text_shadow(f"♛ Crowns: {self.p1_crowns}", col1_x, row_y + 58, 16, Color(255, 220, 80, 255))
        draw_text_shadow(f"TOTAL: {self.p1_final}", col1_x, row_y + 85, 22, GOLD)
        draw_text_shadow(f"Best Combo: x{self.p1_combo}", col1_x, row_y + 115, 14, SKYBLUE)
        
        draw_text_shadow("PLAYER 2", col2_x, row_y, 18, Color(255, 80, 80, 255))
        draw_text_shadow(f"Platforms: {self.p2_score}", col2_x, row_y + 30, 18, WHITE)
        draw_text_shadow(f"♛ Crowns: {self.p2_crowns}", col2_x, row_y + 58, 16, Color(255, 220, 80, 255))
        draw_text_shadow(f"TOTAL: {self.p2_final}", col2_x, row_y + 85, 22, GOLD)
        draw_text_shadow(f"Best Combo: x{self.p2_combo}", col2_x, row_y + 115, 14, SKYBLUE)
        
        # VS divider
        vs_x = SCREEN_WIDTH // 2
        draw_rectangle(vs_x - 1, row_y, 2, 140, fade(WHITE, 0.15))
        vs_w = measure_text("VS", 20)
        draw_text_shadow("VS", vs_x - vs_w // 2, row_y + 55, 20, fade(WHITE, 0.4))
