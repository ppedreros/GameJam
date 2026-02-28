import math
from raylibpy import *
from entities.player import Player3D
from entities.platform import Platform3D
from utils.constants import SCREEN_WIDTH, SCREEN_HEIGHT, DIR_UP, DIR_RIGHT, DIR_DOWN, DIR_LEFT
from utils.draw_utils import draw_arrow, get_direction_vector
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
            panel_width = 220
            panel_height = 80
            panel_x = 20
            panel_y = 20
            
            draw_rectangle(panel_x+2, panel_y+2, panel_width, panel_height, Color(0,0,0,100))
            draw_rectangle(panel_x, panel_y, panel_width, panel_height, fade(BLACK, 0.7))
            
            draw_text("SCORE", panel_x + 20, panel_y + 15, 20, LIGHTGRAY)
            
            score_text = str(self.player.score)
            draw_text(score_text, panel_x + 20, panel_y + 40, 30, WHITE)
            
            if self.game_started:
                bar_bg_rect = Rectangle(SCREEN_WIDTH//2 - 200, 30, 400, 24)
                
                draw_rectangle(int(bar_bg_rect.x+2), int(bar_bg_rect.y+2), int(bar_bg_rect.width), int(bar_bg_rect.height), Color(0,0,0,100))
                draw_rectangle(int(bar_bg_rect.x), int(bar_bg_rect.y), int(bar_bg_rect.width), int(bar_bg_rect.height), fade(DARKGRAY, 0.8))
                
                fill_ratio = max(0.0, self.time_left / self.MAX_TIME)
                bar_fill_rect = Rectangle(bar_bg_rect.x + 2, bar_bg_rect.y + 2, (bar_bg_rect.width - 4) * fill_ratio, bar_bg_rect.height - 4)
                
                bar_color = GREEN
                if self.time_left < 1.0: bar_color = ORANGE
                if self.time_left < 0.5: bar_color = RED
                
                if fill_ratio > 0:
                    draw_rectangle(int(bar_fill_rect.x), int(bar_fill_rect.y), int(bar_fill_rect.width), int(bar_fill_rect.height), bar_color)
                
                time_text = f"{self.time_left:.1f}s"
                time_text_len = measure_text(time_text, 18)
                draw_text(time_text, int(bar_bg_rect.x + bar_bg_rect.width/2 - time_text_len/2), int(bar_bg_rect.y + 3), 18, WHITE)
                
            else:
                prompt = "Press UP arrow to start!"
                prompt_w = measure_text(prompt, 30)
                
                draw_rectangle(SCREEN_WIDTH//2 - prompt_w//2 - 20, SCREEN_HEIGHT//2 - 120, prompt_w + 40, 60, fade(BLACK, 0.6))
                draw_text(prompt, SCREEN_WIDTH//2 - prompt_w//2, SCREEN_HEIGHT//2 - 105, 30, YELLOW)
                
            hint = "Match the white 3D ARROWS using your keyboard!"
            hint_w = measure_text(hint, 20)
            
            draw_rectangle(SCREEN_WIDTH//2 - hint_w//2 - 20, SCREEN_HEIGHT - 60, hint_w + 40, 40, fade(BLACK, 0.5))
            draw_text(hint, SCREEN_WIDTH//2 - hint_w//2, SCREEN_HEIGHT - 50, 20, RAYWHITE)
