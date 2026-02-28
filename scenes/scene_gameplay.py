import math
from raylibpy import *
from entities.player import Player3D
from entities.platform import Platform3D
from utils.constants import SCREEN_WIDTH, SCREEN_HEIGHT, DIR_UP, DIR_RIGHT, DIR_DOWN, DIR_LEFT
from utils.draw_utils import draw_arrow, get_direction_vector, draw_rounded_panel, draw_rounded_panel_outline, draw_text_shadow
from systems.input_handler import get_pressed_direction
import random

class GameplayScene:
    def __init__(self, game):
        self.game = game
        self.camera = Camera3D()
        self.camera.position = Vector3(0.0, 6.0, -6.0)
        self.camera.target = Vector3(0.0, 0.0, 0.0)
        self.camera.up = Vector3(0.0, 1.0, 0.0)
        self.camera.fovy = 45.0
        self.camera.projection = CAMERA_PERSPECTIVE
        
        self.player = Player3D()
        self.platforms = []
        self.platforms.append(Platform3D(0.0, 0.0, DIR_UP))
        
        for _ in range(20):
            self.generate_platform(self.platforms[-1])
            
        self.current_plat_index = 0
        self.game_over = False
        self.game_started = False
        self.MAX_TIME = 2.0
        self.time_left = self.MAX_TIME
        self.JUMP_DURATION = 0.2

    def generate_platform(self, last_plat):
        offset = get_direction_vector(last_plat.direction)
        x = last_plat.pos.x + offset.x
        z = last_plat.pos.z + offset.z
        
        possible_dirs = [DIR_UP, DIR_RIGHT, DIR_LEFT]
        if last_plat.direction == DIR_UP:
            possible_dirs = [DIR_UP, DIR_RIGHT, DIR_LEFT]
        elif last_plat.direction == DIR_RIGHT:
            possible_dirs = [DIR_UP, DIR_RIGHT, DIR_DOWN]
        elif last_plat.direction == DIR_LEFT:
            possible_dirs = [DIR_UP, DIR_DOWN, DIR_LEFT]
        elif last_plat.direction == DIR_DOWN:
            possible_dirs = [DIR_RIGHT, DIR_DOWN, DIR_LEFT]
            
        next_dir = random.choice(possible_dirs)
        self.platforms.append(Platform3D(x, z, next_dir))

    def update(self, dt):
        if self.game_over and not self.player.is_jumping:
            from scenes.scene_gameover import GameOverScene
            self.game.change_scene(GameOverScene(self.game, self.player.score))
            return

        if self.game_started and not self.player.is_jumping:
            self.time_left -= dt
            if self.time_left <= 0:
                self.game_over = True
                self.player.is_jumping = True
                self.player.jump_target_pos = Vector3(self.player.pos.x, -20.0, self.player.pos.z)
                self.player.jump_progress = 0.0

        current_plat = self.platforms[self.current_plat_index]

        if self.player.is_jumping:
            self.player.jump_progress += dt / self.JUMP_DURATION
            if self.player.jump_progress >= 1.0:
                self.player.is_jumping = False
                self.player.pos = self.player.jump_target_pos
                if self.player.pos.y < 0:
                    self.game_over = True
            else:
                t = self.player.jump_progress
                px = self.player.jump_start_pos.x + (self.player.jump_target_pos.x - self.player.jump_start_pos.x) * t
                pz = self.player.jump_start_pos.z + (self.player.jump_target_pos.z - self.player.jump_start_pos.z) * t
                
                arc_height = 2.0 if not self.game_over else 0.0
                py = self.player.jump_start_pos.y + (self.player.jump_target_pos.y - self.player.jump_start_pos.y) * t
                py += math.sin(t * math.pi) * arc_height
                
                self.player.pos = Vector3(px, py, pz)
        
        elif not self.game_over:
            pressed_dir = get_pressed_direction()
            
            if pressed_dir != -1:
                if not self.game_started:
                    self.game_started = True
                    
                self.player.is_jumping = True
                self.player.jump_start_pos = self.player.pos
                self.player.jump_progress = 0.0
                
                if pressed_dir == current_plat.direction:
                    self.current_plat_index += 1
                    next_plat = self.platforms[self.current_plat_index]
                    self.player.jump_target_pos = Vector3(next_plat.pos.x, 2.0, next_plat.pos.z)
                    
                    self.player.score += 1
                    
                    time_added = max(0.4, 1.5 - (self.player.score * 0.05))
                    self.time_left = min(self.MAX_TIME, self.time_left + time_added)
                    
                    if len(self.platforms) - self.current_plat_index < 10:
                        for _ in range(5):
                            self.generate_platform(self.platforms[-1])
                else:
                    wrong_offset = get_direction_vector(pressed_dir)
                    self.player.jump_target_pos = Vector3(
                        self.player.pos.x + wrong_offset.x, 
                        -10.0, 
                        self.player.pos.z + wrong_offset.z
                    )
                    self.game_over = True

        target_cam_pos = Vector3(
            self.player.pos.x - 6.0 * (math.sin(self.time_left) * 0.1 if self.game_started and not self.game_over else 0),
            self.player.pos.y + 6.0,
            self.player.pos.z - 6.0
        ) 
        
        self.camera.position.x += (target_cam_pos.x - self.camera.position.x) * 5.0 * dt
        self.camera.position.y += (target_cam_pos.y - self.camera.position.y) * 5.0 * dt
        self.camera.position.z += (target_cam_pos.z - self.camera.position.z) * 5.0 * dt
        
        self.camera.target.x = self.player.pos.x
        self.camera.target.y = self.player.pos.y - 1.0
        self.camera.target.z = self.player.pos.z

    def draw(self):
        clear_background(BLACK)
        draw_rectangle_gradient_v(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, Color(10, 15, 30, 255), Color(30, 45, 80, 255))

        with mode3d(self.camera):
            start_idx = max(0, self.current_plat_index - 3)
            end_idx = min(len(self.platforms), self.current_plat_index + 15)
            
            for i in range(start_idx, end_idx):
                plat = self.platforms[i]
                color = plat.color
                if i == self.current_plat_index:
                    color = LIME
                    
                draw_cube_v(plat.pos, plat.size, color)
                draw_cube_wires_v(plat.pos, plat.size, BLACK)
                
                if i >= self.current_plat_index:
                    draw_arrow(plat)

            draw_cube_v(self.player.pos, self.player.size, self.player.color)
            draw_cube_wires_v(self.player.pos, self.player.size, MAROON)

        if not self.game_over:
            
            # --- Top HUD ---
            # Score panel (Glassmorphism rounded rectangle)
            panel_width = 180
            panel_height = 90
            panel_x = 20
            panel_y = 20
            
            # Draw sleek panel
            draw_rounded_panel(panel_x, panel_y, panel_width, panel_height, fade(DARKBLUE, 0.4), shadow_offset=6, roundness=0.3)
            # Inner highlight for glass effect
            draw_rounded_panel_outline(panel_x, panel_y, panel_width, panel_height, fade(WHITE, 0.1), segments=10, thickness=2)
            
            draw_text_shadow("SCORE", panel_x + 25, panel_y + 15, 20, LIGHTGRAY)
            
            # Score text with subtle pulsating logic if we wanted (currently static gold)
            score_text = str(self.player.score)
            
            # Subtle pop effect when score increases
            scale_pop = 1.0 + max(0, 0.5 - (self.MAX_TIME - self.time_left)) if self.game_started else 1.0 # Quick cheap pop!
            font_size = int(40 * scale_pop)
            
            draw_text_shadow(score_text, panel_x + 25, panel_y + 40, font_size, GOLD)
            
            # --- Timer Bar ---
            if self.game_started:
                bar_w = 400
                bar_h = 24
                bar_x = SCREEN_WIDTH//2 - bar_w//2
                bar_y = 30
                
                # Draw sleek bar background
                draw_rounded_panel(bar_x, bar_y, bar_w, bar_h, fade(BLACK, 0.6), shadow_offset=4, roundness=0.5)
                # Inner bezel
                draw_rounded_panel_outline(bar_x, bar_y, bar_w, bar_h, fade(WHITE, 0.1), segments=10, thickness=2)
                
                # Calculate fill
                fill_ratio = max(0.0, self.time_left / self.MAX_TIME)
                
                # Color interpolation
                # Green to Red
                r = int(255 * (1 - fill_ratio))
                g = int(255 * fill_ratio)
                b = 50 # Add a tiny bit of blue for a nicer tone
                bar_color = Color(r, g, b, 255)
                
                # Pulse if low time
                if self.time_left < 0.5:
                    pulse_amt = (math.sin(get_time() * 20.0) + 1.0) / 2.0
                    bar_color = color_alpha(bar_color, 0.5 + 0.5 * pulse_amt)
                
                # Draw filled portion
                if fill_ratio > 0:
                    fill_rect = Rectangle(bar_x + 3, bar_y + 3, (bar_w - 6) * fill_ratio, bar_h - 6)
                    draw_rectangle_rounded(fill_rect, 0.5, 10, bar_color)
                    # Add a bright glow line on top of the fill for 3D bar effect
                    glow_rect = Rectangle(bar_x + 6, bar_y + 5, ((bar_w - 6) * fill_ratio) - 6, (bar_h - 6) // 3)
                    if glow_rect.width > 0:
                         draw_rectangle_rounded(glow_rect, 0.5, 10, fade(WHITE, 0.3))
                
                time_text = f"{self.time_left:.1f}s"
                time_text_len = measure_text(time_text, 18)
                draw_text_shadow(time_text, int(bar_x + bar_w/2 - time_text_len/2), int(bar_y + 3), 18, RAYWHITE)
                
            else:
                prompt = "Press UP arrow to start!"
                prompt_w = measure_text(prompt, 30)
                
                # Bobbing animation
                bob = math.sin(get_time() * 3.0) * 5.0
                prompt_y = int(SCREEN_HEIGHT//2 - 120 + bob)
                
                # Pulse glow
                pulse = (math.sin(get_time() * 5.0) + 1.0) / 2.0
                
                draw_rounded_panel(SCREEN_WIDTH//2 - prompt_w//2 - 30, prompt_y - 15, prompt_w + 60, 60, fade(BLACK, 0.6), shadow_offset=6, roundness=0.5)
                draw_rounded_panel_outline(SCREEN_WIDTH//2 - prompt_w//2 - 30, prompt_y - 15, prompt_w + 60, 60, fade(YELLOW, 0.3 + 0.5 * pulse), segments=10, thickness=2)
                
                draw_text_shadow(prompt, SCREEN_WIDTH//2 - prompt_w//2, prompt_y, 30, YELLOW)
                
            hint = "Match the white 3D ARROWS before time runs out!"
            hint_w = measure_text(hint, 20)
            
            draw_rounded_panel(SCREEN_WIDTH//2 - hint_w//2 - 30, SCREEN_HEIGHT - 60, hint_w + 60, 40, fade(BLACK, 0.5), shadow_offset=2, roundness=0.5)
            draw_text_shadow(hint, SCREEN_WIDTH//2 - hint_w//2, SCREEN_HEIGHT - 50, 20, RAYWHITE)
