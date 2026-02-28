import math
from pyray import *
from utils.constants import SCREEN_WIDTH, SCREEN_HEIGHT
from utils.draw_utils import draw_rounded_panel, draw_rounded_panel_outline, draw_text_shadow

class MenuScene:
    def __init__(self, game):
        self.game = game
        
        # Phase 0: Mode selection, Phase 1: Hold to start
        self.phase = 0
        self.selected_mode = 0  # 0 = 1 Player, 1 = 2 Players
        
        # Hold-to-start state
        self.p1_hold_time = 0.0
        self.p2_hold_time = 0.0
        self.HOLD_REQUIRED = 0.05

    def update(self, dt):
        if self.phase == 0:
            # Mode selection with any directional key
            if is_key_pressed(KEY_LEFT) or is_key_pressed(KEY_RIGHT) or is_key_pressed(KEY_A) or is_key_pressed(KEY_D):
                self.selected_mode = 1 - self.selected_mode
            
            if is_key_pressed(KEY_ENTER) or is_key_pressed(KEY_SPACE):
                if self.selected_mode == 0:
                    # Single player — go straight to gameplay
                    from scenes.scene_gameplay import GameplayScene
                    self.game.change_scene(GameplayScene(self.game, singleplayer=True))
                else:
                    self.phase = 1  # Go to hold-to-start
        
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
            
            # Both ready
            if self.p1_hold_time >= self.HOLD_REQUIRED and self.p2_hold_time >= self.HOLD_REQUIRED:
                from scenes.scene_gameplay import GameplayScene
                self.game.change_scene(GameplayScene(self.game, singleplayer=False))

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
        else:
            self._draw_hold_to_start(t)
        
        # Bottom hint
        hint = "Jump on the correct platform to score!"
        hint_w = measure_text(hint, 14)
        pulse = (math.sin(t * 3.0) + 1.0) / 2.0
        draw_text(hint, SCREEN_WIDTH // 2 - hint_w // 2, SCREEN_HEIGHT - 40, 14, Color(150, 150, 170, int(120 + 80 * pulse)))

    def _draw_mode_selection(self, t):
        # Panel
        panel_w = 520
        panel_h = 220
        panel_x = SCREEN_WIDTH // 2 - panel_w // 2
        panel_y = 210
        
        draw_rounded_panel(panel_x, panel_y, panel_w, panel_h, fade(Color(20, 25, 50, 255), 0.85), shadow_offset=8, roundness=0.15)
        draw_rounded_panel_outline(panel_x, panel_y, panel_w, panel_h, fade(WHITE, 0.08), segments=10, thickness=2)
        
        inst = "SELECT MODE"
        inst_w = measure_text(inst, 22)
        draw_text_shadow(inst, SCREEN_WIDTH // 2 - inst_w // 2, panel_y + 20, 22, Color(220, 220, 240, 255))
        
        # Two mode buttons
        btn_w = 200
        btn_h = 100
        gap = 40
        total = btn_w * 2 + gap
        start_x = SCREEN_WIDTH // 2 - total // 2
        btn_y = panel_y + 65
        
        for i, (label, sub_label, icon) in enumerate([
            ("1 PLAYER", "Solo Mode", "WASD"),
            ("2 PLAYERS", "Split Screen", "WASD + Arrows")
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
            lw = measure_text(label, 20)
            label_color = WHITE if selected else Color(150, 150, 170, 255)
            draw_text_shadow(label, bx + btn_w // 2 - lw // 2, btn_y + 20, 20, label_color)
            
            # Sub label
            sw = measure_text(sub_label, 14)
            draw_text(sub_label, bx + btn_w // 2 - sw // 2, btn_y + 48, 14, Color(120, 120, 150, 200))
            
            # Controls hint
            iw = measure_text(icon, 12)
            draw_text(icon, bx + btn_w // 2 - iw // 2, btn_y + 72, 12, Color(100, 100, 130, 180))
            
            # Selection arrow
            if selected:
                arrow = ">"
                aw = measure_text(arrow, 28)
                bob = math.sin(t * 5.0) * 3.0
                draw_text_shadow(arrow, int(bx - 20 + bob), btn_y + 35, 28, Color(0, 200, 255, 255))
        
        # Navigation hint
        nav = "< A/D or Arrows to switch  |  ENTER to confirm >"
        nav_w = measure_text(nav, 14)
        draw_text(nav, SCREEN_WIDTH // 2 - nav_w // 2, panel_y + panel_h - 30, 14, Color(130, 130, 160, 180))

    def _draw_hold_to_start(self, t):
        # Panel
        panel_w = 500
        panel_h = 240
        panel_x = SCREEN_WIDTH // 2 - panel_w // 2
        panel_y = 210
        
        draw_rounded_panel(panel_x, panel_y, panel_w, panel_h, fade(Color(20, 25, 50, 255), 0.85), shadow_offset=8, roundness=0.15)
        draw_rounded_panel_outline(panel_x, panel_y, panel_w, panel_h, fade(WHITE, 0.08), segments=10, thickness=2)
        
        inst = "Both players must HOLD their key to start!"
        inst_w = measure_text(inst, 18)
        draw_text_shadow(inst, SCREEN_WIDTH // 2 - inst_w // 2, panel_y + 20, 18, Color(220, 220, 240, 255))
        
        bar_w = 160
        bar_h = 30
        
        # P1 section
        p1_center = panel_x + panel_w // 4
        draw_text_shadow("PLAYER 1", p1_center - measure_text("PLAYER 1", 20) // 2, panel_y + 60, 20, Color(0, 180, 255, 255))
        draw_text_shadow("Hold  W", p1_center - measure_text("Hold  W", 16) // 2, panel_y + 90, 16, LIGHTGRAY)
        
        bar_x = p1_center - bar_w // 2
        bar_y = panel_y + 120
        p1_ratio = self.p1_hold_time / self.HOLD_REQUIRED
        
        draw_rounded_panel(bar_x, bar_y, bar_w, bar_h, fade(BLACK, 0.5), shadow_offset=0, roundness=0.5)
        if p1_ratio > 0.01:
            fill_w = max(4, int((bar_w - 6) * p1_ratio))
            draw_rectangle_rounded(Rectangle(bar_x + 3, bar_y + 3, fill_w, bar_h - 6), 0.5, 10, Color(0, int(180 + 75 * p1_ratio), 255, 255))
            if fill_w > 8:
                draw_rectangle_rounded(Rectangle(bar_x + 6, bar_y + 5, fill_w - 6, (bar_h - 6) // 3), 0.5, 10, fade(WHITE, 0.3))
        
        if p1_ratio >= 1.0:
            rw = measure_text("READY!", 18)
            draw_text_shadow("READY!", p1_center - rw // 2, bar_y + bar_h + 10, 18, Color(0, 255, 100, 255))
        
        # Divider
        draw_rectangle(SCREEN_WIDTH // 2, panel_y + 55, 1, 160, fade(WHITE, 0.15))
        
        # P2 section
        p2_center = panel_x + 3 * panel_w // 4
        draw_text_shadow("PLAYER 2", p2_center - measure_text("PLAYER 2", 20) // 2, panel_y + 60, 20, Color(255, 80, 80, 255))
        draw_text_shadow("Hold  UP", p2_center - measure_text("Hold  UP", 16) // 2, panel_y + 90, 16, LIGHTGRAY)
        
        bar_x2 = p2_center - bar_w // 2
        p2_ratio = self.p2_hold_time / self.HOLD_REQUIRED
        
        draw_rounded_panel(bar_x2, bar_y, bar_w, bar_h, fade(BLACK, 0.5), shadow_offset=0, roundness=0.5)
        if p2_ratio > 0.01:
            fill_w2 = max(4, int((bar_w - 6) * p2_ratio))
            draw_rectangle_rounded(Rectangle(bar_x2 + 3, bar_y + 3, fill_w2, bar_h - 6), 0.5, 10, Color(255, int(80 + 175 * p2_ratio), int(80 * (1 - p2_ratio)), 255))
            if fill_w2 > 8:
                draw_rectangle_rounded(Rectangle(bar_x2 + 6, bar_y + 5, fill_w2 - 6, (bar_h - 6) // 3), 0.5, 10, fade(WHITE, 0.3))
        
        if p2_ratio >= 1.0:
            rw = measure_text("READY!", 18)
            draw_text_shadow("READY!", p2_center - rw // 2, bar_y + bar_h + 10, 18, Color(0, 255, 100, 255))
        
        # Back hint
        back = "Press ESC to go back"
        bw = measure_text(back, 14)
        draw_text(back, SCREEN_WIDTH // 2 - bw // 2, panel_y + panel_h - 25, 14, Color(130, 130, 160, 180))
