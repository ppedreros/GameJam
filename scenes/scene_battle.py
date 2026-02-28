import math
import random
from pyray import *
from utils.constants import SCREEN_WIDTH, SCREEN_HEIGHT, DIR_UP, DIR_RIGHT, DIR_DOWN, DIR_LEFT
from utils.draw_utils import draw_rounded_panel, draw_rounded_panel_outline, draw_text_shadow
from systems.input_handler import get_p1_pressed_direction, get_p2_pressed_direction, get_p1_pressed_directions, get_p2_pressed_directions, get_p1_held_directions, get_p2_held_directions

class BattleScene:
    def __init__(self, game, gameplay_scene):
        self.game = game
        self.gameplay_scene = gameplay_scene
        
        self.p1_score = 0
        self.p2_score = 0
        self.winning_score = 3
        
        self.singleplayer = getattr(gameplay_scene, 'singleplayer', True)
        self.reaction_timer = 0.0
        
        self.state = "GET_READY"
        self.state_timer = 1.0
        
        self.current_arrows = ()
        self.arrow_timer = 0.0
        
        # Last point anim
        self.point_msg = ""
        self.point_msg_color = WHITE
        self.point_msg_timer = 0.0
        
        self.winner = 0

    def get_arrow_text(self, dir_val):
        if dir_val == DIR_UP: return "UP"
        if dir_val == DIR_RIGHT: return "RIGHT"
        if dir_val == DIR_DOWN: return "DOWN"
        if dir_val == DIR_LEFT: return "LEFT"
        return "?"
        
    def get_arrow_color(self, dir_val):
        if dir_val == DIR_UP: return LIME
        if dir_val == DIR_RIGHT: return ORANGE
        if dir_val == DIR_DOWN: return RED
        if dir_val == DIR_LEFT: return SKYBLUE
        return WHITE
        
    MAGENTA = Color(255, 0, 255, 255)
    CYAN = Color(0, 255, 255, 255)

    def update(self, dt):
        if self.state == "GET_READY":
            self.state_timer -= dt
            if self.state_timer <= 0:
                self.state = "WAITING_ARROW"
                self.arrow_timer = random.uniform(0.25, 2.0)
                
        elif self.state == "WAITING_ARROW":
            self.arrow_timer -= dt
            if self.arrow_timer <= 0:
                self.state = "SHOWING_ARROW"
                
                # In singleplayer, time to react decreases as game speeds up
                if self.singleplayer:
                    speed_factor = self.gameplay_scene.p1_state.player.score * 0.02
                    self.reaction_timer = max(1.2, 2.5 - speed_factor)
                
                # 30% chance for a double arrow combo!
                if random.random() < 0.3:
                    dirs = [DIR_UP, DIR_RIGHT, DIR_DOWN, DIR_LEFT]
                    random.shuffle(dirs)
                    self.current_arrows = tuple(sorted([dirs[0], dirs[1]]))
                else:
                    self.current_arrows = (random.choice([DIR_UP, DIR_RIGHT, DIR_DOWN, DIR_LEFT]),)
                
        elif self.state == "SHOWING_ARROW":
            is_multi = len(self.current_arrows) > 1
            
            p1_dirs = get_p1_held_directions() if is_multi else get_p1_pressed_directions()
            
            if self.singleplayer:
                self.reaction_timer -= dt
                p1_win = False
                p1_fail = False
                
                if p1_dirs:
                    if p1_dirs == self.current_arrows:
                        p1_win = True
                    else:
                        p1_fail = True
                        
                if p1_win:
                    self.p1_score += 1
                    self.point_msg = "NICE!"
                    self.point_msg_color = LIME
                    self.handle_point_scored()
                elif self.reaction_timer <= 0 or p1_fail:
                    self.p2_score += 1
                    self.point_msg = "TOO SLOW!" if not p1_fail else "MISS!"
                    self.point_msg_color = RED
                    self.handle_point_scored()
            
            else:
                p2_dirs = get_p2_held_directions() if is_multi else get_p2_pressed_directions()
                
                p1_win = False
                p2_win = False
                
                if p1_dirs and p1_dirs == self.current_arrows:
                    p1_win = True
                
                if p2_dirs:
                    if p2_dirs == self.current_arrows:
                        p2_win = True
                    
                if p1_win:
                    self.p1_score += 1
                    self.point_msg = "P1 +1!"
                    self.point_msg_color = BLUE
                    self.handle_point_scored()
                elif p2_win:
                    self.p2_score += 1
                    self.point_msg = "P2 +1!"
                    self.point_msg_color = RED
                    self.handle_point_scored()
                
        elif self.state == "POINT_SCORED":
            self.point_msg_timer -= dt
            if self.point_msg_timer <= 0:
                if self.p1_score >= self.winning_score:
                    self.winner = 1
                    self.state = "FINISHED"
                    self.state_timer = 1.0
                elif self.p2_score >= self.winning_score:
                    self.winner = 2
                    self.state = "FINISHED"
                    self.state_timer = 1.0
                else:
                    self.state = "WAITING_ARROW"
                    self.arrow_timer = random.uniform(0.2, 1.0)
                    
        elif self.state == "FINISHED":
            self.state_timer -= dt
            if self.state_timer <= 0:
                self.apply_rewards_and_exit()
                
    def handle_point_scored(self):
        self.state = "POINT_SCORED"
        self.point_msg_timer = 0.5
        self.current_arrows = ()
        
    def apply_rewards_and_exit(self):
        gs = self.gameplay_scene
        if self.winner == 1:
            # P1 wins
            gs.p1_state.player.crowns += 1
            gs.p1_state.time_left = min(gs.p1_state.MAX_TIME, gs.p1_state.time_left + 2.0)
            if gs.p2_state:
                gs.p2_state.player.score = max(0, gs.p2_state.player.score - 1)
        elif self.winner == 2:
            # P2 wins (multiplayer only)
            if gs.p2_state:
                gs.p2_state.player.crowns += 1
                gs.p2_state.time_left = min(gs.p2_state.MAX_TIME, gs.p2_state.time_left + 2.0)
            gs.p1_state.player.score = max(0, gs.p1_state.player.score - 1)
            
            
        self.game.change_scene(self.gameplay_scene)

    def draw(self):
        clear_background(Color(20, 10, 30, 255))
        
        # Grid background
        t = get_time()
        for i in range(0, SCREEN_WIDTH, 80):
            draw_line(i, 0, int(i + math.sin(t*2)*25), SCREEN_HEIGHT, fade(self.MAGENTA, 0.35))
        for i in range(0, SCREEN_HEIGHT, 80):
            draw_line(0, i, SCREEN_WIDTH, int(i + math.cos(t*2)*25), fade(self.CYAN, 0.35))
            
        draw_text_shadow("BATTLE START!", SCREEN_WIDTH//2 - measure_text("BATTLE START!", 60)//2, 50, 60, GOLD)
        
        # Scores
        # P1 card
        draw_rounded_panel(80, 90, 230, 110, Color(0, 30, 120, 240), shadow_offset=8, roundness=0.2)
        draw_rounded_panel_outline(80, 90, 230, 110, Color(0, 150, 255, 255), segments=12, thickness=4)
        draw_text_shadow("P1  WASD", 110, 102, 22, Color(0, 200, 255, 255), shadow_offset=3)
        score_txt = f"{self.p1_score}  /  {self.winning_score}"
        draw_text_shadow(score_txt, 145, 135, 44, GOLD, shadow_offset=3)
        
        # P2 / Time card
        draw_rounded_panel(SCREEN_WIDTH - 310, 90, 230, 110, Color(120, 10, 10, 240), shadow_offset=8, roundness=0.2)
        draw_rounded_panel_outline(SCREEN_WIDTH - 310, 90, 230, 110, Color(255, 80, 80, 255), segments=12, thickness=4)
        
        p2_title = "TIME LIMIT" if self.singleplayer else "P2  ARROWS"
        draw_text_shadow(p2_title, SCREEN_WIDTH - 290, 102, 22, Color(255, 120, 120, 255), shadow_offset=3)
        score_txt2 = f"{self.p2_score}  /  {self.winning_score}"
        draw_text_shadow(score_txt2, SCREEN_WIDTH - 270, 135, 44, GOLD, shadow_offset=3)
        
        # Main display logic
        center_x = SCREEN_WIDTH // 2
        center_y = SCREEN_HEIGHT // 2
        
        if self.state == "GET_READY":
            text = "READY?"
            draw_text_shadow(text, center_x - measure_text(text, 80)//2, center_y - 40, 80, WHITE)
            
        elif self.state == "WAITING_ARROW":
             # Little loading/waiting anim
             r = int(50 + math.sin(t * 15) * 10)
             draw_circle(center_x, center_y, r, fade(YELLOW, 0.5))
             
        elif self.state == "SHOWING_ARROW":
             num_arrows = len(self.current_arrows)
             spacing = 200
             start_x = center_x - (spacing * (num_arrows - 1)) / 2
             
             for i, arrow_val in enumerate(self.current_arrows):
                 arrow_str = self.get_arrow_text(arrow_val)
                 arrow_col = self.get_arrow_color(arrow_val)
                 
                 # Pop effect
                 scale = 1.0 + math.sin(t * 20) * 0.12
                 font_size = int(110 * scale)
                 
                 ax = int(start_x + i * spacing)
                 
                 # Card: dark opaque background with thick colored border
                 draw_rounded_panel(ax - 130, center_y - 130, 260, 260, Color(10, 5, 25, 245), shadow_offset=14, roundness=0.25)
                 draw_rounded_panel_outline(ax - 130, center_y - 130, 260, 260, arrow_col, segments=12, thickness=8)
                 # Inner glow line
                 glow_pulse = (math.sin(t * 15) + 1.0) / 2.0
                 draw_rounded_panel_outline(ax - 122, center_y - 122, 244, 244,
                     Color(arrow_col[0], arrow_col[1], arrow_col[2], int(60 + 80 * glow_pulse)), segments=12, thickness=4)
                 
                 # Arrow text with shadow for contrast
                 draw_text_shadow(arrow_str,
                     ax - measure_text(arrow_str, font_size)//2,
                     center_y - font_size//2,
                     font_size, WHITE, shadow_color=Color(arrow_col[0]//2, arrow_col[1]//2, arrow_col[2]//2, 220), shadow_offset=5)
                 
             if self.singleplayer:
                 # Draw shrinking timer bar below arrows
                 max_t = max(1.2, 2.5 - (self.gameplay_scene.p1_state.player.score * 0.02))
                 bar_w = 400
                 fill_w = int(bar_w * (self.reaction_timer / max_t))
                 bar_x = center_x - bar_w // 2
                 bar_y = center_y + 180
                 draw_rectangle(bar_x, bar_y, bar_w, 20, fade(DARKGRAY, 0.8))
                 draw_rectangle(bar_x, bar_y, fill_w, 20, LIME if self.reaction_timer > max_t*0.4 else RED)
                 draw_rectangle_lines(bar_x, bar_y, bar_w, 20, WHITE)
             
        elif self.state == "POINT_SCORED":
             scale = 1.0 + (0.5 - self.point_msg_timer) * 2.0
             font_size = int(80 * scale)
             draw_text_shadow(self.point_msg, center_x - measure_text(self.point_msg, font_size)//2, center_y - font_size//2, font_size, self.point_msg_color)
             
        elif self.state == "FINISHED":
             win_str = f"PLAYER {self.winner} WINS THE BATTLE!" if not self.singleplayer else ("YOU SURVIVED!" if self.winner == 1 else "TIME WINS!")
             draw_text_shadow(win_str, center_x - measure_text(win_str, 60)//2, center_y - 60, 60, GOLD)
             
             sub_str = "Steals 2 seconds!" if not self.singleplayer else ("+1.5 seconds!" if self.winner == 1 else "-2.0 seconds!")
             draw_text_shadow(sub_str, center_x - measure_text(sub_str, 40)//2, center_y + 20, 40, ORANGE)
