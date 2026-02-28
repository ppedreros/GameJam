# pyre-ignore-all-errors
import math
from pyray import *
from utils.constants import SCREEN_WIDTH, SCREEN_HEIGHT
from utils.draw_utils import draw_rounded_panel, draw_rounded_panel_outline, draw_text_shadow
from utils.particles import ParticleSystem

class DuelMinigameScene:
    def __init__(self, game, gameplay_scene, p1_score, p2_score):
        self.game = game
        self.gameplay_scene = gameplay_scene
        
        self.camera = Camera3D()
        self.camera.position = Vector3(0.0, 5.0, 15.0) # Side view
        self.camera.target = Vector3(0.0, 2.0, 0.0)
        self.camera.up = Vector3(0.0, 1.0, 0.0)
        self.camera.fovy = 45.0
        self.camera.projection = CAMERA_PERSPECTIVE
        
        # P1
        self.p1_start_pos = Vector3(-4.0, 1.0, 0.0)
        self.p1_pos = Vector3(self.p1_start_pos.x, self.p1_start_pos.y, self.p1_start_pos.z)
        self.p1_color = Color(0, 180, 255, 255)
        self.p1_lives = 3
        self.p1_state = "IDLE"
        self.p1_timer = 0.0
        
        # P2
        self.p2_start_pos = Vector3(4.0, 1.0, 0.0)
        self.p2_pos = Vector3(self.p2_start_pos.x, self.p2_start_pos.y, self.p2_start_pos.z)
        self.p2_color = Color(255, 80, 80, 255)
        self.p2_lives = 3
        self.p2_state = "IDLE"
        self.p2_timer = 0.0
        
        self.player_size = 1.0
        self.move_speed = 8.0
        self.attack_range = 3.5
        
        self.countdown = 3.0
        self.game_over = False
        self.winner = None
        self.end_timer = 2.0
        self.time_left = 20.0 # Time limit for the duel
        
        self.particles = ParticleSystem()
        
    def check_hit(self, attacker_pos, defender_pos, defender_state):
        dist = abs(attacker_pos.x - defender_pos.x)
        # Check range and parry state
        if dist < self.attack_range:
            if defender_state == "PARRY":
                return "BLOCKED"
            else:
                return "HIT"
        return "MISS"
        
    def reset_positions(self):
        self.p1_pos = Vector3(self.p1_start_pos.x, self.p1_start_pos.y, self.p1_start_pos.z)
        self.p2_pos = Vector3(self.p2_start_pos.x, self.p2_start_pos.y, self.p2_start_pos.z)
        self.p1_state = "IDLE"
        self.p2_state = "IDLE"
        self.countdown = 1.0 # Short pause after hit
        
    def update(self, dt):
        self.particles.update(dt)
        
        if self.countdown > 0:
            self.countdown -= dt
            return
            
        if self.game_over:
            self.end_timer -= dt
            if self.end_timer <= 0:
                if self.winner == 1:
                    self.gameplay_scene.p1_state.player.score += 1000
                elif self.winner == 2:
                    self.gameplay_scene.p2_state.player.score += 1000
                self.game.change_scene(self.gameplay_scene)
            return

        # Time limit logic
        self.time_left -= dt
        if self.time_left <= 0:
            self.game_over = True
            self.winner = 0 # Draw
            self.time_left = 0
            return

        # P1 Logic
        if self.p1_state == "IDLE":
            # Movement
            if is_key_down(KEY_A) and self.p1_pos.x > -8.0:
                self.p1_pos.x -= self.move_speed * dt
            if is_key_down(KEY_D) and self.p1_pos.x < self.p2_pos.x - 1.5:
                self.p1_pos.x += self.move_speed * dt
            
            # Actions
            if is_key_pressed(KEY_E):
                self.p1_state = "ATTACK"
                self.p1_timer = 0.25 # 0.25s startup/active
                
            elif is_key_pressed(KEY_Q):
                self.p1_state = "PARRY"
                self.p1_timer = 0.4 # 0.4s active parry window
                
        elif self.p1_state == "ATTACK":
            self.p1_timer -= dt
            if self.p1_timer <= 0:
                # Check hit
                res = self.check_hit(self.p1_pos, self.p2_pos, self.p2_state)
                if res == "HIT":
                    self.p2_lives -= 1
                    self.particles.emit_death_burst(self.p2_pos.x, self.p2_pos.y, self.p2_pos.z, self.p2_color, 20)
                    if self.p2_lives <= 0:
                        self.game_over = True
                        self.winner = 1
                    else:
                        self.reset_positions()
                elif res == "BLOCKED":
                    # Emit spark on defender, but damage the attacker
                    self.particles.emit_landing_burst(self.p2_pos.x, self.p2_pos.y, self.p2_pos.z, WHITE, 10)
                    self.p1_lives -= 1
                    self.particles.emit_death_burst(self.p1_pos.x, self.p1_pos.y, self.p1_pos.z, self.p1_color, 20)
                    if self.p1_lives <= 0:
                        self.game_over = True
                        self.winner = 2
                    else:
                        self.reset_positions()
                        
                self.p1_state = "RECOVER"
                if res == "BLOCKED":
                    self.p1_timer = 0.6 # Punish for being parried
                else:
                    self.p1_timer = 0.3
                
        elif self.p1_state == "PARRY":
            self.p1_timer -= dt
            if self.p1_timer <= 0:
                self.p1_state = "RECOVER"
                self.p1_timer = 0.3
                
        elif self.p1_state == "RECOVER":
            self.p1_timer -= dt
            if self.p1_timer <= 0:
                self.p1_state = "IDLE"
                
        # P2 Logic
        if self.p2_state == "IDLE":
            # Movement
            if is_key_down(KEY_RIGHT) and self.p2_pos.x < 8.0:
                self.p2_pos.x += self.move_speed * dt
            if is_key_down(KEY_LEFT) and self.p2_pos.x > self.p1_pos.x + 1.5:
                self.p2_pos.x -= self.move_speed * dt
            
            # Actions
            if is_key_pressed(KEY_ENTER) or is_key_pressed(KEY_KP_ENTER):
                self.p2_state = "ATTACK"
                self.p2_timer = 0.25
                
            elif is_key_pressed(KEY_SPACE):
                self.p2_state = "PARRY"
                self.p2_timer = 0.4
                
        elif self.p2_state == "ATTACK":
            self.p2_timer -= dt
            if self.p2_timer <= 0:
                res = self.check_hit(self.p2_pos, self.p1_pos, self.p1_state)
                if res == "HIT":
                    self.p1_lives -= 1
                    self.particles.emit_death_burst(self.p1_pos.x, self.p1_pos.y, self.p1_pos.z, self.p1_color, 20)
                    if self.p1_lives <= 0:
                        self.game_over = True
                        self.winner = 2
                    else:
                        self.reset_positions()
                elif res == "BLOCKED":
                    self.particles.emit_landing_burst(self.p1_pos.x, self.p1_pos.y, self.p1_pos.z, WHITE, 10)
                    self.p2_lives -= 1
                    self.particles.emit_death_burst(self.p2_pos.x, self.p2_pos.y, self.p2_pos.z, self.p2_color, 20)
                    if self.p2_lives <= 0:
                        self.game_over = True
                        self.winner = 1
                    else:
                        self.reset_positions()
                        
                self.p2_state = "RECOVER"
                if res == "BLOCKED":
                    self.p2_timer = 0.6
                else:
                    self.p2_timer = 0.3
                
        elif self.p2_state == "PARRY":
            self.p2_timer -= dt
            if self.p2_timer <= 0:
                self.p2_state = "RECOVER"
                self.p2_timer = 0.3
                
        elif self.p2_state == "RECOVER":
            self.p2_timer -= dt
            if self.p2_timer <= 0:
                self.p2_state = "IDLE"
                
    def draw(self):
        clear_background(Color(10, 20, 10, 255)) # Dark green background
        
        begin_mode_3d(self.camera)
        
        # Floor
        draw_cube(Vector3(0, -0.5, 0), 20.0, 1.0, 5.0, Color(40, 60, 40, 255))
        draw_cube_wires(Vector3(0, -0.5, 0), 20.0, 1.0, 5.0, LIME)
        
        # Draw P1
        sw1 = math.sin(get_time()*5)*0.1 if self.p1_state == "IDLE" else 0.0
        draw_cube(Vector3(self.p1_pos.x, self.p1_pos.y+1.0+sw1, self.p1_pos.z), self.player_size, self.player_size*2, self.player_size, self.p1_color)
        draw_cube_wires(Vector3(self.p1_pos.x, self.p1_pos.y+1.0+sw1, self.p1_pos.z), self.player_size, self.player_size*2, self.player_size, WHITE)
        
        # P1 Attack / Parry visuals
        if self.p1_state == "ATTACK":
            draw_cube(Vector3(self.p1_pos.x + 1.2, self.p1_pos.y+1.0, self.p1_pos.z), 1.5, 0.2, 0.2, YELLOW)
        elif self.p1_state == "PARRY":
            draw_sphere(Vector3(self.p1_pos.x, self.p1_pos.y+1.0, self.p1_pos.z), 1.5, Color(0, 255, 255, 100))
            draw_sphere_wires(Vector3(self.p1_pos.x, self.p1_pos.y+1.0, self.p1_pos.z), 1.5, 8, 8, Color(0, 255, 255, 255))
            
        # Draw P2
        sw2 = math.sin(get_time()*5)*0.1 if self.p2_state == "IDLE" else 0.0
        draw_cube(Vector3(self.p2_pos.x, self.p2_pos.y+1.0+sw2, self.p2_pos.z), self.player_size, self.player_size*2, self.player_size, self.p2_color)
        draw_cube_wires(Vector3(self.p2_pos.x, self.p2_pos.y+1.0+sw2, self.p2_pos.z), self.player_size, self.player_size*2, self.player_size, WHITE)
        
        # P2 Attack / Parry visuals
        if self.p2_state == "ATTACK":
            draw_cube(Vector3(self.p2_pos.x - 1.2, self.p2_pos.y+1.0, self.p2_pos.z), 1.5, 0.2, 0.2, ORANGE)
        elif self.p2_state == "PARRY":
            draw_sphere(Vector3(self.p2_pos.x, self.p2_pos.y+1.0, self.p2_pos.z), 1.5, Color(255, 255, 0, 100))
            draw_sphere_wires(Vector3(self.p2_pos.x, self.p2_pos.y+1.0, self.p2_pos.z), 1.5, 8, 8, YELLOW)
            
        self.particles.draw_3d()
            
        end_mode_3d()
        
        # HUD
        lives_text_p1 = "LIVES: " + "O "*self.p1_lives
        draw_text_shadow(lives_text_p1, 30, 30, 30, self.p1_color)
        
        draw_text_shadow("E=ATK Q=PARRY", 30, 70, 20, GRAY)
        
        lives_text_p2 = "LIVES: " + "O "*self.p2_lives
        w2 = measure_text(lives_text_p2, 30)
        draw_text_shadow(lives_text_p2, SCREEN_WIDTH - w2 - 30, 30, 30, self.p2_color)
        
        ins2 = "ENTER=ATK SPACE=PARRY"
        wins2 = measure_text(ins2, 20)
        draw_text_shadow(ins2, SCREEN_WIDTH - wins2 - 30, 70, 20, GRAY)
        
        if self.countdown > 0 and not self.game_over:
            txt = f"{math.ceil(self.countdown)}"
            if self.countdown < 1.0: txt = "FIGHT!"
            ts = 120
            w = measure_text(txt, ts)
            draw_text_shadow(txt, SCREEN_WIDTH//2 - w//2, SCREEN_HEIGHT//2 - ts//2, ts, YELLOW)
        elif not self.game_over:
            # Draw Timer
            time_txt = f"TIME: {math.ceil(self.time_left)}"
            time_w = measure_text(time_txt, 40)
            draw_text_shadow(time_txt, SCREEN_WIDTH//2 - time_w//2, 30, 40, WHITE)
            
        if self.game_over:
            txt = "DUEL OVER!"
            if self.winner == 1:
                txt = "PLAYER 1 WINS +1000!"
                c = self.p1_color
            elif self.winner == 2:
                txt = "PLAYER 2 WINS +1000!"
                c = self.p2_color
                
            ts = 50
            w = measure_text(txt, ts)
            panel_w = w + 80
            draw_rounded_panel(SCREEN_WIDTH//2 - panel_w//2, SCREEN_HEIGHT//2 - 60, panel_w, 120, fade(BLACK, 0.8))
            draw_text_shadow(txt, SCREEN_WIDTH//2 - w//2, SCREEN_HEIGHT//2 - ts//2, ts, c)
