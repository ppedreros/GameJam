import math
from pyray import *
from entities.player import Player3D
from entities.platform import Platform3D
from utils.constants import SCREEN_WIDTH, SCREEN_HEIGHT, DIR_UP, DIR_RIGHT, DIR_DOWN, DIR_LEFT
from utils.draw_utils import draw_arrow, get_direction_vector, draw_rounded_panel, draw_rounded_panel_outline, draw_text_shadow
from systems.input_handler import get_p1_pressed_direction, get_p2_pressed_direction
import random

class PlayerGameState:
    def __init__(self, is_player1=True):
        self.is_player1 = is_player1
        self.camera = Camera3D()
        self.camera.position = Vector3(0.0, 6.0, -6.0)
        self.camera.target = Vector3(0.0, 0.0, 0.0)
        self.camera.up = Vector3(0.0, 1.0, 0.0)
        self.camera.fovy = 45.0
        self.camera.projection = CAMERA_PERSPECTIVE
        
        self.player = Player3D()
        self.player.color = BLUE if is_player1 else RED
        
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
        
        # We render each player to a separate half-screen texture
        # SCREEN_WIDTH is 1200, so each gets 600x600
        self.render_width = int(SCREEN_WIDTH / 2)
        self.render_target = load_render_texture(self.render_width, SCREEN_HEIGHT)

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

    def update_logic(self, dt):
        if self.game_over and not self.player.is_jumping:
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
            pressed_dir = get_p1_pressed_direction() if self.is_player1 else get_p2_pressed_direction()
            
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

    def draw_to_texture(self):
        begin_texture_mode(self.render_target)
        
        clear_background(BLACK)
        draw_rectangle_gradient_v(0, 0, self.render_width, SCREEN_HEIGHT, Color(10, 15, 30, 255), Color(30, 45, 80, 255))

        begin_mode_3d(self.camera)
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

        end_mode_3d()

        if not self.game_over:
            
            # --- Top HUD ---
            # Score panel (Glassmorphism rounded rectangle)
            panel_width = 160
            panel_height = 80
            panel_x = 20
            panel_y = 20
            
            # Draw sleek panel
            draw_rounded_panel(panel_x, panel_y, panel_width, panel_height, fade(DARKBLUE, 0.4), shadow_offset=6, roundness=0.3)
            # Inner highlight for glass effect
            draw_rounded_panel_outline(panel_x, panel_y, panel_width, panel_height, fade(WHITE, 0.1), segments=10, thickness=2)
            
            draw_text_shadow("SCORE", panel_x + 20, panel_y + 10, 15, LIGHTGRAY)
            
            # Score text with subtle pulsating logic
            score_text = str(self.player.score)
            
            scale_pop = 1.0 + max(0, 0.5 - (self.MAX_TIME - self.time_left)) if self.game_started else 1.0 
            font_size = int(35 * scale_pop)
            
            draw_text_shadow(score_text, panel_x + 20, panel_y + 30, font_size, GOLD)
            
            # Player ID
            pid_text = "P1 (WASD)" if self.is_player1 else "P2 (ARROWS)"
            draw_text_shadow(pid_text, self.render_width - measure_text(pid_text, 20) - 20, 20, 20, WHITE if self.is_player1 else RED)
            
            # --- Timer Bar ---
            if self.game_started:
                bar_w = 300
                bar_h = 24
                bar_x = self.render_width//2 - bar_w//2
                bar_y = 30
                
                # Draw sleek bar background
                draw_rounded_panel(bar_x, bar_y, bar_w, bar_h, fade(BLACK, 0.6), shadow_offset=4, roundness=0.5)
                # Inner bezel
                draw_rounded_panel_outline(bar_x, bar_y, bar_w, bar_h, fade(WHITE, 0.1), segments=10, thickness=2)
                
                # Calculate fill
                fill_ratio = max(0.0, self.time_left / self.MAX_TIME)
                
                # Color interpolation Green to Red
                r = int(255 * (1 - fill_ratio))
                g = int(255 * fill_ratio)
                b = 50 
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
                
            else:
                prompt = "Press W to start!" if self.is_player1 else "Press UP to start!"
                prompt_w = measure_text(prompt, 20)
                
                # Bobbing animation
                bob = math.sin(get_time() * 3.0) * 5.0
                prompt_y = int(SCREEN_HEIGHT//2 - 120 + bob)
                
                # Pulse glow
                pulse = (math.sin(get_time() * 5.0) + 1.0) / 2.0
                
                draw_rounded_panel(self.render_width//2 - prompt_w//2 - 20, prompt_y - 10, prompt_w + 40, 40, fade(BLACK, 0.6), shadow_offset=6, roundness=0.5)
                draw_rounded_panel_outline(self.render_width//2 - prompt_w//2 - 20, prompt_y - 10, prompt_w + 40, 40, fade(YELLOW, 0.3 + 0.5 * pulse), segments=10, thickness=2)
                
                draw_text_shadow(prompt, self.render_width//2 - prompt_w//2, prompt_y, 20, YELLOW)
                
        end_texture_mode()


class GameplayScene:
    def __init__(self, game):
        self.game = game
        self.p1_state = PlayerGameState(is_player1=True)
        self.p2_state = PlayerGameState(is_player1=False)

    def update(self, dt):
        self.p1_state.update_logic(dt)
        self.p2_state.update_logic(dt)

        # Check win condition
        p1_dead = self.p1_state.game_over and not self.p1_state.player.is_jumping
        p2_dead = self.p2_state.game_over and not self.p2_state.player.is_jumping
        
        if p1_dead or p2_dead:
            from scenes.scene_gameover import GameOverScene
            
            winner = "Draw"
            if p1_dead and not p2_dead:
                winner = "Player 2"
            elif p2_dead and not p1_dead:
                winner = "Player 1"
                
            self.game.change_scene(GameOverScene(self.game, winner, self.p1_state.player.score, self.p2_state.player.score))

    def draw(self):
        # Draw each player's view into their respective textures
        self.p1_state.draw_to_texture()
        self.p2_state.draw_to_texture()
        
        # Now render the two textures side by side to the main screen window
        clear_background(BLACK)
        
        # raylib RenderTexture2D draws flipped vertically, so we MUST flip the source rectangle Y
        half_w = self.p1_state.render_width
        source_rec = Rectangle(0, self.p1_state.render_target.texture.height, self.p1_state.render_target.texture.width, -self.p1_state.render_target.texture.height)
        
        # Draw P1 on left
        p1_dest = Rectangle(0, 0, half_w, SCREEN_HEIGHT)
        draw_texture_pro(self.p1_state.render_target.texture, source_rec, p1_dest, Vector2(0,0), 0.0, WHITE)
        
        # Draw P2 on right
        p2_dest = Rectangle(half_w, 0, half_w, SCREEN_HEIGHT)
        draw_texture_pro(self.p2_state.render_target.texture, source_rec, p2_dest, Vector2(0,0), 0.0, WHITE)
        
        # Draw a beautiful separator line in the middle
        draw_rectangle_gradient_v(half_w - 2, 0, 4, SCREEN_HEIGHT, fade(Color(0, 255, 255, 255), 0.8), fade(Color(255, 0, 255, 255), 0.8))
        draw_rectangle(half_w - 1, 0, 2, SCREEN_HEIGHT, WHITE)
