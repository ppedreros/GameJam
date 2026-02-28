import math
import random
from pyray import *
from utils.constants import SCREEN_WIDTH, SCREEN_HEIGHT
from utils.draw_utils import draw_rounded_panel, draw_rounded_panel_outline, draw_text_shadow

class Projectile:
    def __init__(self, pos, velocity, size, color):
        self.pos = pos
        self.velocity = velocity
        self.size = size
        self.color = color

class DropSphere:
    def __init__(self, pos, size, color):
        self.pos = pos
        self.size = size
        self.color = color
        self.warning_alpha = 0.0
        self.falling_speed = 3.0

class MinigameScene:
    def __init__(self, game, gameplay_scene, p1_score, p2_score):
        self.game = game
        self.gameplay_scene = gameplay_scene # reference to resume later
        
        self.camera = Camera3D()
        self.camera.position = Vector3(0.0, 20.0, -15.0) # High angle
        self.camera.target = Vector3(0.0, 0.0, 0.0)
        self.camera.up = Vector3(0.0, 1.0, 0.0)
        self.camera.fovy = 45.0
        self.camera.projection = CAMERA_PERSPECTIVE
        
        self.arena_size = 30.0
        
        # Player 1 (Blue)
        self.p1_pos = Vector3(-5.0, 1.0, 0.0)
        self.p1_color = Color(0, 180, 255, 255)
        self.p1_score = p1_score
        self.p1_alive = True
        
        # Player 2 (Red)
        self.p2_pos = Vector3(5.0, 1.0, 0.0)
        self.p2_color = Color(255, 80, 80, 255)
        self.p2_score = p2_score
        self.p2_alive = True
        
        self.player_speed = 12.0
        self.player_size = 1.0
        
        self.projectiles = []
        self.drop_spheres = []
        self.spawn_timer = 0.0
        self.drop_timer = 3.0
        self.difficulty = 1.0
        
        self.game_over = False
        self.winner = None
        self.end_timer = 2.0
        
        # UI
        self.countdown = 3.0
        self.started = False

    def update(self, dt):
        if self.countdown > 0:
            self.countdown -= dt
            if self.countdown <= 0:
                self.started = True
            return

        if self.game_over:
            self.end_timer -= dt
            if self.end_timer <= 0:
                # Add 1000 points to winner
                if self.winner == 1:
                    self.gameplay_scene.p1_state.player.score += 1000
                elif self.winner == 2:
                    self.gameplay_scene.p2_state.player.score += 1000
                
                # We do not switch to gameover, we resume gameplay
                # Wait, the problem is they are on platform 10. We should resume them on platform 10 but reset jump state so they continue.
                self.game.change_scene(self.gameplay_scene)
            return

        # Player Movement
        half_arena = self.arena_size / 2.0 - self.player_size / 2.0
        
        # Player 1 (WASD) - Inverted Left/Right (A and D swapped logically)
        if self.p1_alive:
            dx1 = 0
            dz1 = 0
            if is_key_down(KEY_A): dx1 += 1  # Inverted
            if is_key_down(KEY_D): dx1 -= 1  # Inverted
            if is_key_down(KEY_W): dz1 += 1 
            if is_key_down(KEY_S): dz1 -= 1
            
            # Normalize vector
            if dx1 != 0 or dz1 != 0:
                length = math.sqrt(dx1*dx1 + dz1*dz1)
                dx1 /= length
                dz1 /= length
                
            self.p1_pos.x += dx1 * self.player_speed * dt
            self.p1_pos.z += dz1 * self.player_speed * dt
            
            # Clamp to arena
            self.p1_pos.x = max(-half_arena, min(half_arena, self.p1_pos.x))
            self.p1_pos.z = max(-half_arena, min(half_arena, self.p1_pos.z))
            
        # Player 2 (Arrows) - Inverted Left/Right
        if self.p2_alive:
            dx2 = 0
            dz2 = 0
            if is_key_down(KEY_LEFT): dx2 += 1  # Inverted
            if is_key_down(KEY_RIGHT): dx2 -= 1 # Inverted
            if is_key_down(KEY_UP): dz2 += 1
            if is_key_down(KEY_DOWN): dz2 -= 1
            
            if dx2 != 0 or dz2 != 0:
                length = math.sqrt(dx2*dx2 + dz2*dz2)
                dx2 /= length
                dz2 /= length
                
            self.p2_pos.x += dx2 * self.player_speed * dt
            self.p2_pos.z += dz2 * self.player_speed * dt
            
            # Clamp to arena
            self.p2_pos.x = max(-half_arena, min(half_arena, self.p2_pos.x))
            self.p2_pos.z = max(-half_arena, min(half_arena, self.p2_pos.z))

        # Drop Spheres Spawning
        self.drop_timer -= dt
        if self.drop_timer <= 0:
            self.drop_timer = random.uniform(2.5, 4.0) - (self.difficulty * 0.1)
            self.drop_timer = max(0.8, self.drop_timer)
            
            drop_x = random.uniform(-half_arena, half_arena)
            drop_z = random.uniform(-half_arena, half_arena)
            drop_size = random.uniform(6.0, 10.0)
            
            self.drop_spheres.append(DropSphere(
                pos=Vector3(drop_x, 15.0, drop_z),
                size=drop_size,
                color=Color(150, 0, 255, 255) # Purple danger
            ))

        # Projectile Spawning
        self.difficulty += dt * 0.1
        self.spawn_timer -= dt
        if self.spawn_timer <= 0:
            self.spawn_timer = max(0.2, 1.0 - (self.difficulty * 0.15))
            
            # Spawn from edges
            edge = random.randint(0, 3)
            size = random.uniform(0.8, 2.5)
            speed = random.uniform(10.0, 25.0) + self.difficulty * 2.0
            
            px, pz = 0, 0
            vx, vz = 0, 0
            
            spawn_dist = self.arena_size / 2.0 + 5.0
            
            if edge == 0: # Top
                px = random.uniform(-half_arena, half_arena)
                pz = spawn_dist
                vz = -speed
            elif edge == 1: # Bottom
                px = random.uniform(-half_arena, half_arena)
                pz = -spawn_dist
                vz = speed
            elif edge == 2: # Left
                px = -spawn_dist
                pz = random.uniform(-half_arena, half_arena)
                vx = speed
            elif edge == 3: # Right
                px = spawn_dist
                pz = random.uniform(-half_arena, half_arena)
                vx = -speed
                
            self.projectiles.append(Projectile(
                pos=Vector3(px, size/2.0, pz),
                velocity=Vector3(vx, 0.0, vz),
                size=size,
                color=Color(255, int(random.uniform(50, 200)), 0, 255) # Fiery colors
            ))

        # Projectile Update and Collision
        for proj in self.projectiles[:]:
            proj.pos.x += proj.velocity.x * dt
            proj.pos.z += proj.velocity.z * dt
            
            # Remove offscreen
            if abs(proj.pos.x) > self.arena_size + 10 or abs(proj.pos.z) > self.arena_size + 10:
                self.projectiles.remove(proj)
                continue
                
            # Collision Player 1
            if self.p1_alive:
                dist_x = proj.pos.x - self.p1_pos.x
                dist_z = proj.pos.z - self.p1_pos.z
                dist = math.sqrt(dist_x*dist_x + dist_z*dist_z)
                if dist < (proj.size / 2.0) + (self.player_size / 2.0):
                    self.p1_alive = False
                    
            # Collision Player 2
            if self.p2_alive:
                dist_x = proj.pos.x - self.p2_pos.x
                dist_z = proj.pos.z - self.p2_pos.z
                dist = math.sqrt(dist_x*dist_x + dist_z*dist_z)
                if dist < (proj.size / 2.0) + (self.player_size / 2.0):
                    self.p2_alive = False

        # Drop Spheres Update
        for ds in self.drop_spheres[:]:
            ds.pos.y -= ds.falling_speed * dt
            ds.warning_alpha = min(1.0, ds.warning_alpha + dt * 0.5)
            
            # Impact
            if ds.pos.y <= ds.size / 2.0:
                # Check collision immediately
                if self.p1_alive:
                    dist_x = ds.pos.x - self.p1_pos.x
                    dist_z = ds.pos.z - self.p1_pos.z
                    dist = math.sqrt(dist_x*dist_x + dist_z*dist_z)
                    if dist < (ds.size / 2.0) + (self.player_size / 2.0):
                        self.p1_alive = False
                        
                if self.p2_alive:
                    dist_x = ds.pos.x - self.p2_pos.x
                    dist_z = ds.pos.z - self.p2_pos.z
                    dist = math.sqrt(dist_x*dist_x + dist_z*dist_z)
                    if dist < (ds.size / 2.0) + (self.player_size / 2.0):
                        self.p2_alive = False
                        
                self.drop_spheres.remove(ds)

        # Check win condition
        if not self.p1_alive and not self.p2_alive:
            self.game_over = True
            self.winner = 0 # Draw
        elif not self.p1_alive and self.p2_alive:
            self.game_over = True
            self.winner = 2
        elif self.p1_alive and not self.p2_alive:
            self.game_over = True
            self.winner = 1

    def draw(self):
        clear_background(Color(20, 10, 30, 255))
        
        begin_mode_3d(self.camera)
        
        # Draw Arena Floor
        draw_cube(Vector3(0, -0.5, 0), self.arena_size, 1.0, self.arena_size, Color(40, 40, 60, 255))
        draw_cube_wires(Vector3(0, -0.5, 0), self.arena_size, 1.0, self.arena_size, Color(0, 255, 255, 100))
        
        # Grid
        for i in range(int(-self.arena_size/2), int(self.arena_size/2)+1, 2):
            draw_line_3d(Vector3(i, 0.01, -self.arena_size/2), Vector3(i, 0.01, self.arena_size/2), Color(255,255,255, 40))
            draw_line_3d(Vector3(-self.arena_size/2, 0.01, i), Vector3(self.arena_size/2, 0.01, i), Color(255,255,255, 40))
            
        # Draw Drop Warning Shadows
        for ds in self.drop_spheres:
            alpha = int(80 * ds.warning_alpha)
            # A cylinder can act as a warning circle on the ground
            draw_cylinder(Vector3(ds.pos.x, 0.05, ds.pos.z), ds.size/2.0, ds.size/2.0, 0.05, 32, Color(255, 0, 0, alpha))
            draw_sphere(ds.pos, ds.size/2.0, ds.color)
            draw_sphere_wires(ds.pos, ds.size/2.0, 10, 10, Color(255,255,255,100))
            
        # Draw Players
        if self.p1_alive:
            draw_cube(self.p1_pos, self.player_size, self.player_size*2, self.player_size, self.p1_color)
            draw_cube_wires(self.p1_pos, self.player_size, self.player_size*2, self.player_size, WHITE)
            
        if self.p2_alive:
            draw_cube(self.p2_pos, self.player_size, self.player_size*2, self.player_size, self.p2_color)
            draw_cube_wires(self.p2_pos, self.player_size, self.player_size*2, self.player_size, WHITE)
            
        # Draw Projectiles
        for proj in self.projectiles:
            draw_sphere(proj.pos, proj.size/2.0, proj.color)
            draw_sphere_wires(proj.pos, proj.size/2.0, 10, 10, WHITE)
            
        end_mode_3d()
        
        # UI overlays
        if self.countdown > 0:
            txt = f"{math.ceil(self.countdown)}"
            ts = 120
            w = measure_text(txt, ts)
            draw_text_shadow(txt, SCREEN_WIDTH//2 - w//2, SCREEN_HEIGHT//2 - ts//2, ts, YELLOW)
            
            sub = "SURVIVE FOR 1000 POINTS!"
            sw = measure_text(sub, 40)
            draw_text_shadow(sub, SCREEN_WIDTH//2 - sw//2, SCREEN_HEIGHT//2 + ts//2, 40, WHITE)
            
        if self.game_over:
            if self.winner == 1:
                txt = "PLAYER 1 SURVIVES! +1000"
                c = self.p1_color
            elif self.winner == 2:
                txt = "PLAYER 2 SURVIVES! +1000"
                c = self.p2_color
            else:
                txt = "NO SURVIVORS!"
                c = GRAY
                
            ts = 60
            w = measure_text(txt, ts)
            
            # Panel
            panel_w = w + 80
            draw_rounded_panel(SCREEN_WIDTH//2 - panel_w//2, SCREEN_HEIGHT//2 - 60, panel_w, 120, fade(BLACK, 0.8))
            draw_text_shadow(txt, SCREEN_WIDTH//2 - w//2, SCREEN_HEIGHT//2 - ts//2, ts, c)
