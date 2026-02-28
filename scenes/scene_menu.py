import math
from pyray import *
from utils.constants import SCREEN_WIDTH, SCREEN_HEIGHT
from utils.draw_utils import draw_rounded_panel, draw_rounded_panel_outline, draw_text_shadow

class MenuScene:
    def __init__(self, game):
        self.game = game
        
        # Phase 0: Mode selection, Phase 1: Hold to start, Phase 2: How to Play
        self.phase = 0
        self.selected_mode = 0  # 0 = 1 Player, 1 = 2 Players, 2 = How to Play
        
        # Hold-to-start state
        self.p1_hold_time = 0.0
        self.p2_hold_time = 0.0
        self.HOLD_REQUIRED = 1.0
        
        # Tutorial scrolling
        self.tutorial_scroll = 0.0
        self.max_scroll = 500.0

    def update(self, dt):
        if self.phase == 0:
            # Mode selection with any directional key
            if is_key_pressed(KEY_LEFT) or is_key_pressed(KEY_A):
                self.selected_mode = (self.selected_mode - 1) % 3
            if is_key_pressed(KEY_RIGHT) or is_key_pressed(KEY_D):
                self.selected_mode = (self.selected_mode + 1) % 3
                
            if is_key_pressed(KEY_ESCAPE):
                close_window() # Manually close since we disabled default esc
            
            if is_key_pressed(KEY_ENTER) or is_key_pressed(KEY_SPACE):
                if self.selected_mode == 0:
                    # Single player — go straight to gameplay
                    from scenes.scene_gameplay import GameplayScene
                    self.game.change_scene(GameplayScene(self.game, singleplayer=True))
                elif self.selected_mode == 1:
                    self.phase = 1  # Go to hold-to-start
                elif self.selected_mode == 2:
                    self.phase = 2  # Go to How to Play
        
        elif self.phase == 1:
            # P1 holds W
            if is_key_down(KEY_W):
                self.p1_hold_time = min(self.HOLD_REQUIRED, self.p1_hold_time + dt)
            else:
                self.p1_hold_time = max(0.0, self.p1_hold_time - dt * 2.0)
            
            # P2 holds UP
            if is_key_down(KEY_UP):
                self.p2_hold_time = min(self.HOLD_REQUIRED, self.p2_hold_time + dt)
            else:
                self.p2_hold_time = max(0.0, self.p2_hold_time - dt * 2.0)
            
            # Back to selection
            if is_key_pressed(KEY_ESCAPE):
                self.phase = 0
                self.p1_hold_time = 0.0
                self.p2_hold_time = 0.0
            
                from scenes.scene_gameplay import GameplayScene
                self.game.change_scene(GameplayScene(self.game, singleplayer=False))
                
        elif self.phase == 2:
            # Scroll with wheel or arrows
            scroll_speed = 40.0 * 60 * dt
            if get_mouse_wheel_move() > 0 or is_key_down(KEY_UP):
                self.tutorial_scroll += scroll_speed
            elif get_mouse_wheel_move() < 0 or is_key_down(KEY_DOWN):
                self.tutorial_scroll -= scroll_speed
                
            self.tutorial_scroll = max(-self.max_scroll, min(0.0, self.tutorial_scroll))
            
            if is_key_pressed(KEY_ESCAPE) or is_key_pressed(KEY_ENTER) or is_key_pressed(KEY_SPACE):
                self.phase = 0

    def draw(self):
        t = get_time()
        
        # Background
        draw_rectangle_gradient_v(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, Color(8, 12, 25, 255), Color(20, 30, 60, 255))
        
        # Animated floating dots
        for i in range(30):
            dx = (i * 97 + int(t * 20 * (i % 3 + 1))) % SCREEN_WIDTH
            dy = (i * 53 + int(t * 10 * (i % 2 + 1))) % SCREEN_HEIGHT
            alpha = int(40 + 30 * math.sin(t * 2.0 + i))
            draw_rectangle(dx, dy, 2, 2, Color(255, 255, 255, alpha))
        
        # Title
        title = "REACT & JUMP 3D"
        title_size = 60
        title_w = measure_text(title, title_size)
        title_y = 60
        float_y = math.sin(t * 2.0) * 8.0
        
        for g in range(3):
            glow_alpha = int(30 - g * 10)
            draw_text(title, SCREEN_WIDTH // 2 - title_w // 2 - g, int(title_y + float_y - g), title_size, Color(100, 200, 255, glow_alpha))
        draw_text_shadow(title, SCREEN_WIDTH // 2 - title_w // 2, int(title_y + float_y), title_size, Color(0, 200, 255, 255), shadow_offset=4)
        
        sub = "MULTIPLAYER SPLIT-SCREEN"
        sub_w = measure_text(sub, 18)
        draw_text_shadow(sub, SCREEN_WIDTH // 2 - sub_w // 2, int(title_y + 75 + float_y), 18, Color(180, 180, 200, 200))
        
        if self.phase == 0:
            self._draw_mode_selection(t)
        elif self.phase == 1:
            self._draw_hold_to_start(t)
        elif self.phase == 2:
            self._draw_how_to_play(t)
        
        # Bottom hint
        hint = "Jump on the correct platform to score!"
        hint_w = measure_text(hint, 14)
        pulse = (math.sin(t * 3.0) + 1.0) / 2.0
        draw_text(hint, SCREEN_WIDTH // 2 - hint_w // 2, SCREEN_HEIGHT - 40, 14, Color(150, 150, 170, int(120 + 80 * pulse)))

    def _draw_mode_selection(self, t):
        # Panel
        panel_w = 980
        panel_h = 300
        panel_x = SCREEN_WIDTH // 2 - panel_w // 2
        panel_y = 250
        
        draw_rounded_panel(panel_x, panel_y, panel_w, panel_h, fade(Color(20, 25, 50, 255), 0.85), shadow_offset=8, roundness=0.15)
        draw_rounded_panel_outline(panel_x, panel_y, panel_w, panel_h, fade(WHITE, 0.08), segments=10, thickness=2)
        
        inst = "SELECT MODE"
        inst_w = measure_text(inst, 32)
        draw_text_shadow(inst, SCREEN_WIDTH // 2 - inst_w // 2, panel_y + 30, 32, Color(220, 220, 240, 255))
        
        # Three mode buttons
        btn_w = 280
        btn_h = 160
        gap = 40
        total = btn_w * 3 + gap * 2
        start_x = SCREEN_WIDTH // 2 - total // 2
        btn_y = panel_y + 90
        
        for i, (label, sub_label, icon) in enumerate([
            ("1 PLAYER", "Solo Mode", "WASD"),
            ("2 PLAYERS", "Split Screen", "WASD + Arrows"),
            ("HOW TO PLAY", "Tutorial", "Rules & Tips")
        ]):
            bx = start_x + i * (btn_w + gap)
            selected = (self.selected_mode == i)
            
            # Button bg
            if selected:
                pulse = (math.sin(t * 4.0) + 1.0) / 2.0
                bg_color = fade(Color(0, 180, 255, 255), 0.2 + 0.1 * pulse)
                border_color = Color(0, 200, 255, int(180 + 75 * pulse))
            else:
                bg_color = fade(Color(40, 45, 70, 255), 0.6)
                border_color = fade(WHITE, 0.08)
            
            draw_rounded_panel(bx, btn_y, btn_w, btn_h, bg_color, shadow_offset=4 if selected else 2, roundness=0.2)
            draw_rounded_panel_outline(bx, btn_y, btn_w, btn_h, border_color, segments=10, thickness=2 if selected else 1)
            
            # Label
            lw = measure_text(label, 28)
            label_color = WHITE if selected else Color(150, 150, 170, 255)
            draw_text_shadow(label, bx + btn_w // 2 - lw // 2, btn_y + 30, 28, label_color)
            
            # Sub label
            sw = measure_text(sub_label, 18)
            draw_text(sub_label, bx + btn_w // 2 - sw // 2, btn_y + 75, 18, Color(120, 120, 150, 200))
            
            # Controls hint
            iw = measure_text(icon, 16)
            draw_text(icon, bx + btn_w // 2 - iw // 2, btn_y + 110, 16, Color(100, 100, 130, 180))
            
            # Selection arrow
            if selected:
                arrow = ">"
                aw = measure_text(arrow, 40)
                bob = math.sin(t * 5.0) * 3.0
                draw_text_shadow(arrow, int(bx - 30 + bob), btn_y + 60, 40, Color(0, 200, 255, 255))
        
        # Navigation hint
        nav = "< A/D or Arrows to switch  |  ENTER to confirm >"
        nav_w = measure_text(nav, 14)
        draw_text(nav, SCREEN_WIDTH // 2 - nav_w // 2, panel_y + panel_h - 30, 14, Color(130, 130, 160, 180))

    def _draw_hold_to_start(self, t):
        # Panel
        panel_w = 800
        panel_h = 360
        panel_x = SCREEN_WIDTH // 2 - panel_w // 2
        panel_y = 220
        
        draw_rounded_panel(panel_x, panel_y, panel_w, panel_h, fade(Color(20, 25, 50, 255), 0.85), shadow_offset=8, roundness=0.15)
        draw_rounded_panel_outline(panel_x, panel_y, panel_w, panel_h, fade(WHITE, 0.08), segments=10, thickness=2)
        
        inst = "Both players must HOLD their key to start!"
        inst_w = measure_text(inst, 32)
        draw_text_shadow(inst, SCREEN_WIDTH // 2 - inst_w // 2, panel_y + 35, 32, Color(220, 220, 240, 255))
        
        bar_w = 300
        bar_h = 50
        
        # P1 section
        p1_center = panel_x + panel_w // 4
        draw_text_shadow("PLAYER 1", p1_center - measure_text("PLAYER 1", 28) // 2, panel_y + 80, 28, Color(0, 180, 255, 255))
        draw_text_shadow("Hold  W", p1_center - measure_text("Hold  W", 24) // 2, panel_y + 120, 24, LIGHTGRAY)
        
        bar_x = p1_center - bar_w // 2
        bar_y = panel_y + 160
        p1_ratio = self.p1_hold_time / self.HOLD_REQUIRED
        
        draw_rounded_panel(bar_x, bar_y, bar_w, bar_h, fade(BLACK, 0.5), shadow_offset=0, roundness=0.5)
        if p1_ratio > 0.01:
            fill_w = max(4, int((bar_w - 6) * p1_ratio))
            draw_rectangle_rounded(Rectangle(bar_x + 3, bar_y + 3, fill_w, bar_h - 6), 0.5, 10, Color(0, int(180 + 75 * p1_ratio), 255, 255))
            if fill_w > 8:
                draw_rectangle_rounded(Rectangle(bar_x + 6, bar_y + 5, fill_w - 6, (bar_h - 6) // 3), 0.5, 10, fade(WHITE, 0.3))
        
        if p1_ratio >= 1.0:
            rw = measure_text("READY!", 32)
            draw_text_shadow("READY!", p1_center - rw // 2, bar_y + bar_h + 25, 32, Color(0, 255, 100, 255))
        
        # Divider
        draw_rectangle(SCREEN_WIDTH // 2, panel_y + 70, 1, 180, fade(WHITE, 0.15))
        
        # P2 section
        p2_center = panel_x + 3 * panel_w // 4
        draw_text_shadow("PLAYER 2", p2_center - measure_text("PLAYER 2", 28) // 2, panel_y + 80, 28, Color(255, 80, 80, 255))
        draw_text_shadow("Hold  UP", p2_center - measure_text("Hold  UP", 24) // 2, panel_y + 120, 24, LIGHTGRAY)
        
        bar_x2 = p2_center - bar_w // 2
        p2_ratio = self.p2_hold_time / self.HOLD_REQUIRED
        
        draw_rounded_panel(bar_x2, bar_y, bar_w, bar_h, fade(BLACK, 0.5), shadow_offset=0, roundness=0.5)
        if p2_ratio > 0.01:
            fill_w2 = max(4, int((bar_w - 6) * p2_ratio))
            draw_rectangle_rounded(Rectangle(bar_x2 + 3, bar_y + 3, fill_w2, bar_h - 6), 0.5, 10, Color(255, int(80 + 175 * p2_ratio), int(80 * (1 - p2_ratio)), 255))
            if fill_w2 > 8:
                draw_rectangle_rounded(Rectangle(bar_x2 + 6, bar_y + 5, fill_w2 - 6, (bar_h - 6) // 3), 0.5, 10, fade(WHITE, 0.3))
        
        if p2_ratio >= 1.0:
            rw = measure_text("READY!", 32)
            draw_text_shadow("READY!", p2_center - rw // 2, bar_y + bar_h + 25, 32, Color(0, 255, 100, 255))
        
        # Back hint
        back = "Press ESC to go back"
        bw = measure_text(back, 18)
        draw_text(back, SCREEN_WIDTH // 2 - bw // 2, panel_y + panel_h - 35, 18, Color(130, 130, 160, 180))

    def _draw_how_to_play(self, t):
        panel_w = 900
        panel_h = 560
        panel_x = SCREEN_WIDTH // 2 - panel_w // 2
        panel_y = 100
        
        draw_rounded_panel(panel_x, panel_y, panel_w, panel_h, fade(Color(15, 20, 40, 255), 0.95), shadow_offset=8, roundness=0.1)
        draw_rounded_panel_outline(panel_x, panel_y, panel_w, panel_h, fade(WHITE, 0.15), segments=10, thickness=2)
        
        title = "HOW TO PLAY"
        draw_text_shadow(title, SCREEN_WIDTH // 2 - measure_text(title, 42) // 2, panel_y + 20, 42, Color(220, 220, 255, 255))
        
        # Scissor area
        content_y = panel_y + 80
        content_h = panel_h - 130
        begin_scissor_mode(panel_x, content_y, panel_w, content_h)
        
        # Base layout params inside scissor
        col_x = panel_x + 60
        y_offset = content_y + int(self.tutorial_scroll)
        spacing = 55
        
        # --- Single Column: Basics & Platforms ---
        draw_text_shadow("Controls & Platforms", col_x, y_offset, 32, Color(0, 200, 255, 255)); y_offset += spacing
        draw_text("- WASD or Arrows: Jump to the next platform.", col_x, y_offset, 22, WHITE); y_offset += spacing - 15
        draw_text("- Match the glowing direction on the platform.", col_x, y_offset, 22, WHITE); y_offset += spacing
        
        draw_text("- Double Arrows: Press both keys sequentially", col_x, y_offset, 22, YELLOW); y_offset += 26
        draw_text("  without making a mistake to gain a time bonus.", col_x, y_offset, 22, YELLOW); y_offset += spacing
        
        draw_text("- Red Arrows (Inverted): Press the REVERSE", col_x, y_offset, 22, Color(255, 80, 80, 255)); y_offset += 26
        draw_text("  direction of what is shown. Gives huge time bonus!", col_x, y_offset, 22, Color(255, 80, 80, 255)); y_offset += spacing
        
        # --- Single Column: Traps & Modes ---
        y_offset += 20
        draw_text_shadow("Modifiers & Events", col_x, y_offset, 32, Color(255, 150, 50, 255)); y_offset += spacing
        
        draw_text("- Dodge Traps: A large warning will appear!", col_x, y_offset, 22, WHITE); y_offset += 26
        draw_text("  Press the indicated key quickly to avoid penalties.", col_x, y_offset, 22, LIGHTGRAY); y_offset += spacing
        
        draw_text("- Darkness: Hides complex arrows, reducing them", col_x, y_offset, 22, Color(180, 100, 255, 255)); y_offset += 26
        draw_text("  to single arrows, but keeps their time bonus.", col_x, y_offset, 22, Color(180, 100, 255, 255)); y_offset += spacing
        
        draw_text("- Battle Tile (Multiplayer): First to land here", col_x, y_offset, 22, ORANGE); y_offset += 26
        draw_text("  triggers a chaotic rhythm-battle event!", col_x, y_offset, 22, ORANGE); y_offset += spacing
        
        draw_text("- Minigame Tile (Multiplayer): Dodge falling", col_x, y_offset, 22, GREEN); y_offset += 26
        draw_text("  projectiles and survive for crowns and time!", col_x, y_offset, 22, GREEN); y_offset += spacing
        
        end_scissor_mode()
        
        # Dynamic scroll boundary calculation
        self.max_scroll = max(0, y_offset - int(self.tutorial_scroll) - (content_y + content_h))
        
        # Scroll indicator line
        draw_rectangle(panel_x + panel_w - 20, content_y, 4, content_h, fade(WHITE, 0.1))
        if self.max_scroll > 0:
            handle_h = max(20, int(content_h * (content_h / (content_h + self.max_scroll))))
            handle_y = content_y + int((content_h - handle_h) * (-self.tutorial_scroll / self.max_scroll))
            draw_rectangle(panel_x + panel_w - 20, handle_y, 4, handle_h, fade(WHITE, 0.6))
        
        # Bottom hint
        back = "Scroll up/down | Press ESC or ENTER to return"
        bw = measure_text(back, 22)
        pulse = (math.sin(t * 3.0) + 1.0) / 2.0
        draw_text(back, SCREEN_WIDTH // 2 - bw // 2, panel_y + panel_h - 40, 22, Color(150, 150, 170, int(150 + 105 * pulse)))
