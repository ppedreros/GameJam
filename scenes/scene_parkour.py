# pyre-ignore-all-errors
import math
import random
from pyray import *
from utils.constants import SCREEN_WIDTH, SCREEN_HEIGHT

GOLD = Color(255, 203, 0, 255)
CYAN = Color(0, 228, 255, 255)
WHITE = Color(255, 255, 255, 255)
RED = Color(230, 41, 55, 255)
BLACK = Color(0, 0, 0, 255)
GRAY = Color(130, 130, 130, 255)
YELLOW = Color(253, 249, 0, 255)
from utils.draw_utils import draw_rounded_panel, draw_rounded_panel_outline, draw_text_shadow
from utils.particles import ParticleSystem

class ParkourPlayer:
    def __init__(self, start_pos, color):
        self.pos = start_pos
        self.vel = Vector3(0.0, 0.0, 0.0)
        self.color = color
        self.size = 1.0
        self.speed = 10.0
        self.jump_force = 15.0
        self.gravity = 25.0
        
        self.is_grounded = False
        self.alive = True
        
        self.double_jump_timer = 0.0
        self.can_double_jump = False
        self.has_double_jumped = False

class ParkourScene:
    def __init__(self, game, gameplay_scene, p1_score, p2_score):
        self.game = game
        self.gameplay_scene = gameplay_scene
        self.singleplayer = getattr(gameplay_scene, 'singleplayer', False)
        
        self.camera_p1 = Camera3D()
        self.camera_p1.position = Vector3(0.0, 10.0, 15.0)
        self.camera_p1.target = Vector3(0.0, 5.0, 0.0)
        self.camera_p1.up = Vector3(0.0, 1.0, 0.0)
        self.camera_p1.fovy = 60.0
        self.camera_p1.projection = CAMERA_PERSPECTIVE
        
        self.camera_p2 = Camera3D()
        self.camera_p2.position = Vector3(0.0, 10.0, 15.0)
        self.camera_p2.target = Vector3(0.0, 5.0, 0.0)
        self.camera_p2.up = Vector3(0.0, 1.0, 0.0)
        self.camera_p2.fovy = 60.0
        self.camera_p2.projection = CAMERA_PERSPECTIVE
        
        self.rt_p1 = load_render_texture(SCREEN_WIDTH // 2 if not self.singleplayer else SCREEN_WIDTH, SCREEN_HEIGHT)
        if not self.singleplayer:
            self.rt_p2 = load_render_texture(SCREEN_WIDTH // 2, SCREEN_HEIGHT)
        
        # Players
        self.p1 = ParkourPlayer(Vector3(-2.0, 1.0, 0.0), Color(0, 180, 255, 255))
        if not self.singleplayer:
            self.p2 = ParkourPlayer(Vector3(2.0, 1.0, 0.0), Color(255, 80, 80, 255))
        else:
            self.p2 = None
            self.p1.pos = Vector3(0.0, 1.0, 0.0)
            
        self.particles = ParticleSystem()
        
        self.platforms = [] # list of dicts {"pos": Vector3, "size": Vector3, "color": Color}
        self.powerups = []  # list of dicts {"pos": Vector3, "active": bool}
        
        self.goal_z = 80.0 # Distance to reach
        
        self.generate_level()
        
        self.countdown = 3.0
        self.game_over = False
        self.winner = None
        self.end_timer = 2.0
        
        # Death plane
        self.death_y = -5.0
        
    def generate_level(self):
        # Base platform
        self.platforms.append({
            "pos": Vector3(0.0, 0.0, 0.0),
            "size": Vector3(10.0, 1.0, 10.0),
            "color": Color(40, 40, 60, 255)
        })
        
        current_y = 0.0
        current_x = 0.0
        current_z = 5.0
        
        # Generate platforms forward (Z-axis)
        while current_z < self.goal_z:
            plat_size = Vector3(random.uniform(3.0, 5.0), 1.0, random.uniform(3.0, 5.0))
            
            # small horizontal/vertical offset
            cx = current_x + random.uniform(-4.0, 4.0)
            cy = current_y + random.uniform(-1.0, 1.5)
            
            # keep within bounds
            cx = max(-8.0, min(8.0, cx))
            cy = max(-2.0, min(8.0, cy))
            
            self.platforms.append({
                "pos": Vector3(cx, cy, current_z),
                "size": plat_size,
                "color": Color(50, int(random.uniform(50, 150)), 200, 255)
            })
            
            # 15% chance to spawn a double jump powerup
            if random.random() < 0.15:
                self.powerups.append({
                    "pos": Vector3(cx, cy + 2.0, current_z),
                    "active": True
                })
                
            current_z += random.uniform(5.5, 8.5)
            current_x = cx
            current_y = cy
            
        # Goal platform
        self.goal_pos = Vector3(0.0, current_y, current_z)
        self.platforms.append({
            "pos": self.goal_pos,
            "size": Vector3(10.0, 1.0, 8.0),
            "color": GOLD
        })
        self.goal_z = current_z

    def update_player(self, p, dt, is_p1):
        if not p.alive or self.game_over:
            return
            
        # Input
        dx = 0
        dz = 0
        jump_pressed = False
        
        if is_p1:
            # Inverted controls
            if is_key_down(KEY_A): dx += 1
            if is_key_down(KEY_D): dx -= 1
            if is_key_down(KEY_W): dz += 1
            if is_key_down(KEY_S): dz -= 1
            if is_key_pressed(KEY_Q): jump_pressed = True
        else:
            # Inverted controls
            if is_key_down(KEY_LEFT): dx += 1
            if is_key_down(KEY_RIGHT): dx -= 1
            if is_key_down(KEY_UP): dz += 1
            if is_key_down(KEY_DOWN): dz -= 1
            if is_key_pressed(KEY_SPACE): jump_pressed = True
            
        # Normalize
        if dx != 0 or dz != 0:
            length = math.sqrt(dx*dx + dz*dz)
            dx /= length
            dz /= length
            
        # Movement XZ
        p.vel.x = dx * p.speed
        p.vel.z = dz * p.speed
        
        # Gravity
        p.vel.y -= p.gravity * dt
        
        # Jump / Double Jump
        if jump_pressed:
            if p.is_grounded:
                p.vel.y = p.jump_force
                p.is_grounded = False
                p.has_double_jumped = False
                self.particles.emit_landing_burst(p.pos.x, p.pos.y - p.size/2, p.pos.z, WHITE, 5)
            elif p.can_double_jump and not p.has_double_jumped:
                p.vel.y = p.jump_force * 0.9 # Slightly weaker double jump
                p.has_double_jumped = True
                self.particles.emit_landing_burst(p.pos.x, p.pos.y - p.size/2, p.pos.z, Color(0, 255, 255, 255), 10)
                
        # Move
        new_pos = Vector3(p.pos.x + p.vel.x * dt, p.pos.y + p.vel.y * dt, p.pos.z + p.vel.z * dt)
        
        # Collision with platforms (simple AABB, prioritizing landing on top)
        p.is_grounded = False
        for plat in self.platforms:
            px, py, pz = plat["pos"].x, plat["pos"].y, plat["pos"].z
            sx, sy, sz = plat["size"].x, plat["size"].y, plat["size"].z
            
            # Update AABB collision slightly to be more forgiving
            # Player is checking if center point is within plat XZ radius
            if (abs(new_pos.x - px) < (sx/2 + p.size/2 + 0.2) and 
                abs(new_pos.z - pz) < (sz/2 + p.size/2 + 0.2)):
                
                # Check Y collision (falling onto it)
                # Ensure the player was above it, or close enough to snap
                if p.pos.y >= py and new_pos.y - p.size/2 <= py + sy/2:
                    new_pos.y = py + sy/2 + p.size/2
                    p.vel.y = 0
                    p.is_grounded = True
                    p.has_double_jumped = False
                    
        p.pos = new_pos
        
        # Bounds check
        if p.pos.y < self.death_y:
            p.alive = False
            self.particles.emit_death_burst(p.pos.x, p.pos.y, p.pos.z, p.color, 20)
            
        # Powerup logic
        if p.double_jump_timer > 0:
            p.double_jump_timer -= dt
            if p.double_jump_timer <= 0:
                p.can_double_jump = False
                
        for pw in self.powerups:
            if pw["active"]:
                dist_sq = (p.pos.x - pw["pos"].x)**2 + (p.pos.y - pw["pos"].y)**2 + (p.pos.z - pw["pos"].z)**2
                if dist_sq < 2.5: # Collision pickup
                    pw["active"] = False
                    p.can_double_jump = True
                    p.double_jump_timer = 2.0
                    p.has_double_jumped = False
                    self.particles.emit_landing_burst(pw["pos"].x, pw["pos"].y, pw["pos"].z, Color(0, 255, 255, 255), 15)
                    
        # Check Goal
        if p.pos.z >= self.goal_pos.z - 4.0:
            # Reached goal
            self.game_over = True
            self.winner = 1 if is_p1 else 2
            
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
            
        self.update_player(self.p1, dt, True)
        if self.p2:
            self.update_player(self.p2, dt, False)
            
        # Check if both dead
        if not self.p1.alive and (self.singleplayer or not self.p2.alive):
            self.game_over = True
            self.winner = 0 # No one wins
            
        # Camera logic
        # Player 1 Camera
        target_cam_z_p1 = self.p1.pos.z - 8.0
        self.camera_p1.position.z += (target_cam_z_p1 - self.camera_p1.position.z) * 5.0 * dt
        self.camera_p1.target.z += (self.p1.pos.z + 5.0 - self.camera_p1.target.z) * 5.0 * dt
        self.camera_p1.position.y += (self.p1.pos.y + 6.0 - self.camera_p1.position.y) * 5.0 * dt
        self.camera_p1.target.y += (self.p1.pos.y + 1.0 - self.camera_p1.target.y) * 5.0 * dt
        
        # Player 2 Camera
        if self.p2:
            target_cam_z_p2 = self.p2.pos.z - 8.0
            self.camera_p2.position.z += (target_cam_z_p2 - self.camera_p2.position.z) * 5.0 * dt
            self.camera_p2.target.z += (self.p2.pos.z + 5.0 - self.camera_p2.target.z) * 5.0 * dt
            self.camera_p2.position.y += (self.p2.pos.y + 6.0 - self.camera_p2.position.y) * 5.0 * dt
            self.camera_p2.target.y += (self.p2.pos.y + 1.0 - self.camera_p2.target.y) * 5.0 * dt
        
        # Static death plane
        self.death_y = -10.0

    def draw_3d_scene(self, camera):
        begin_mode_3d(camera)
        
        # Draw death plane
        draw_cube(Vector3(0, self.death_y, camera.target.z), 100.0, 0.1, 100.0, Color(255, 0, 0, 80))
        draw_cube_wires(Vector3(0, self.death_y, camera.target.z), 100.0, 0.1, 100.0, RED)
        
        # Draw Platforms
        for plat in self.platforms:
            draw_cube(plat["pos"], plat["size"].x, plat["size"].y, plat["size"].z, plat["color"])
            draw_cube_wires(plat["pos"], plat["size"].x, plat["size"].y, plat["size"].z, Color(0, 0, 0, 100))
            
        # Draw Goal beacon
        beacon_height = 100.0
        draw_cylinder(Vector3(self.goal_pos.x, self.goal_pos.y + beacon_height/2, self.goal_pos.z), 1.0, 1.0, beacon_height, 16, Color(255, 215, 0, 100))
            
        # Draw Powerups
        time_b = get_time() * 3.0
        for pw in self.powerups:
            if pw["active"]:
                bob = math.sin(time_b + pw["pos"].x) * 0.3
                draw_cube(Vector3(pw["pos"].x, pw["pos"].y + bob, pw["pos"].z), 0.6, 0.6, 0.6, CYAN)
                draw_cube_wires(Vector3(pw["pos"].x, pw["pos"].y + bob, pw["pos"].z), 0.7, 0.7, 0.7, WHITE)
                
        # Draw Players
        if self.p1.alive:
            draw_cube(self.p1.pos, self.p1.size, self.p1.size, self.p1.size, self.p1.color)
            draw_cube_wires(self.p1.pos, self.p1.size, self.p1.size, self.p1.size, WHITE)
            if self.p1.can_double_jump:
                draw_cube_wires(self.p1.pos, self.p1.size*1.2, self.p1.size*1.2, self.p1.size*1.2, CYAN)
            
        if self.p2 and self.p2.alive:
            draw_cube(self.p2.pos, self.p2.size, self.p2.size, self.p2.size, self.p2.color)
            draw_cube_wires(self.p2.pos, self.p2.size, self.p2.size, self.p2.size, WHITE)
            if self.p2.can_double_jump:
                draw_cube_wires(self.p2.pos, self.p2.size*1.2, self.p2.size*1.2, self.p2.size*1.2, CYAN)
                
        self.particles.draw_3d()
        
        end_mode_3d()

    def draw(self):
        # Draw P1 Texture
        begin_texture_mode(self.rt_p1)
        clear_background(Color(20, 10, 40, 255))
        draw_rectangle_gradient_v(0, 0, self.rt_p1.texture.width, self.rt_p1.texture.height, Color(10, 0, 30, 255), Color(40, 20, 60, 255))
        self.draw_3d_scene(self.camera_p1)
        end_texture_mode()
        
        # Draw P2 Texture
        if self.p2:
            begin_texture_mode(self.rt_p2)
            clear_background(Color(20, 10, 40, 255))
            draw_rectangle_gradient_v(0, 0, self.rt_p2.texture.width, self.rt_p2.texture.height, Color(10, 0, 30, 255), Color(40, 20, 60, 255))
            self.draw_3d_scene(self.camera_p2)
            end_texture_mode()
            
        # Draw to Screen
        clear_background(BLACK)
        
        if self.singleplayer:
            src = Rectangle(0, self.rt_p1.texture.height, self.rt_p1.texture.width, -self.rt_p1.texture.height)
            dst = Rectangle(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT)
            draw_texture_pro(self.rt_p1.texture, src, dst, Vector2(0,0), 0.0, WHITE)
        else:
            w = self.rt_p1.texture.width
            h = self.rt_p1.texture.height
            
            src_p1 = Rectangle(0, h, w, -h)
            dst_p1 = Rectangle(0, 0, w, SCREEN_HEIGHT)
            draw_texture_pro(self.rt_p1.texture, src_p1, dst_p1, Vector2(0,0), 0.0, WHITE)
            
            src_p2 = Rectangle(0, self.rt_p2.texture.height, self.rt_p2.texture.width, -self.rt_p2.texture.height)
            dst_p2 = Rectangle(SCREEN_WIDTH//2, 0, self.rt_p2.texture.width, SCREEN_HEIGHT)
            draw_texture_pro(self.rt_p2.texture, src_p2, dst_p2, Vector2(0,0), 0.0, WHITE)
            
            # Separator
            draw_rectangle(SCREEN_WIDTH//2 - 2, 0, 4, SCREEN_HEIGHT, Color(255, 255, 255, 120))
        
        # HUD
        if self.countdown > 0 and not self.game_over:
            txt = f"{math.ceil(self.countdown)}"
            if self.countdown < 1.0: txt = "CLIMB!"
            ts = 120
            w = measure_text(txt, ts)
            draw_text_shadow(txt, SCREEN_WIDTH//2 - w//2, SCREEN_HEIGHT//2 - ts//2, ts, YELLOW)
            
        if self.p1.can_double_jump:
            draw_text_shadow(f"P1 DOUBLE JUMP: {self.p1.double_jump_timer:.1f}s", 20, 20, 20, CYAN)
            
        if self.p2 and self.p2.can_double_jump:
            txt = f"P2 DOUBLE JUMP: {self.p2.double_jump_timer:.1f}s"
            draw_text_shadow(txt, SCREEN_WIDTH - measure_text(txt, 20) - 20, 20, 20, CYAN)
            
        # Draw progress
        if self.p1.alive:
            h1 = f"P1: {int(max(0, self.p1.pos.z))}m / {int(self.goal_z)}m"
            draw_text_shadow(h1, 20, 50, 25, self.p1.color)
        if self.p2 and self.p2.alive:
            h2 = f"P2: {int(max(0, self.p2.pos.z))}m / {int(self.goal_z)}m"
            draw_text_shadow(h2, SCREEN_WIDTH - measure_text(h2, 25) - 20, 50, 25, self.p2.color)
            
        if self.game_over:
            txt = "NOBODY SURVIVED!"
            c = GRAY
            if self.winner == 1:
                txt = "PLAYER 1 WINS +1000!"
                c = self.p1.color
            elif self.winner == 2:
                txt = "PLAYER 2 WINS +1000!"
                c = self.p2.color
                
            ts = 50
            w = measure_text(txt, ts)
            panel_w = w + 80
            draw_rounded_panel(SCREEN_WIDTH//2 - panel_w//2, SCREEN_HEIGHT//2 - 60, panel_w, 120, fade(BLACK, 0.8))
            draw_text_shadow(txt, SCREEN_WIDTH//2 - w//2, SCREEN_HEIGHT//2 - ts//2, ts, c) 
