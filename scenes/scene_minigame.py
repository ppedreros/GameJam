# pyre-ignore-all-errors
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
        
        self.singleplayer = getattr(gameplay_scene, 'singleplayer', False)
        
        # Player 1 (Blue)
        self.p1_pos = Vector3(0.0, 1.0, 0.0) if self.singleplayer else Vector3(-5.0, 1.0, 0.0)
        self.p1_color = Color(0, 180, 255, 255)
        self.p1_score = p1_score
        self.p1_alive = True
        self.p1_lives = 3
        
        # Player 2 (Red)
        self.p2_pos = Vector3(5.0, 1.0, 0.0)
        self.p2_color = Color(255, 80, 80, 255)
        self.p2_score = p2_score
        self.p2_alive = not self.singleplayer
        self.p2_lives = 3
        
        self.player_speed = 12.0
        self.player_size = 1.0
        
        # 3 Bosses: 0=North, 1=East, 2=West (no South boss)
        # Each boss will move along its respective edge
        self.bosses = [
            {"pos": 0.0, "dir": 1.0, "side": "N", "timer": 0.0},
            {"pos": 0.0, "dir": 1.0, "side": "E", "timer": 0.8},
            {"pos": 0.0, "dir": -1.0, "side": "W", "timer": 1.6},
        ]
        
        self.projectiles = []
        self.drop_spheres = []
        self.holes = []
        # Individual boss spawn_timers are in the self.bosses dicts
        self.drop_timer = 3.0
        self.difficulty = 1.0
        
        self.game_over = False
        self.winner = None
        self.end_timer = 2.0
        self.survival_time = 30.0
        
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
                elif self.winner == 3:
                    self.gameplay_scene.p1_state.player.score += 1000
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
            self.drop_timer = random.uniform(2.0, 4.0) - (self.difficulty * 0.1)
            self.drop_timer = max(0.8, self.drop_timer)
            
            drop_x = random.uniform(-half_arena, half_arena)
            drop_z = random.uniform(-half_arena, half_arena)
            drop_size = random.uniform(6.0, 10.0)
            
            # Make the sphere completely invisible
            self.drop_spheres.append(DropSphere(
                pos=Vector3(drop_x, 15.0, drop_z),
                size=drop_size,
                color=Color(0, 0, 0, 0) # Invisible
            ))

        # Bosses Movement
        for boss in self.bosses:
            boss["pos"] += boss["dir"] * dt * (8.0 + self.difficulty * 2.0)
            if boss["pos"] > half_arena:
                boss["pos"] = half_arena
                boss["dir"] = -1.0
            elif boss["pos"] < -half_arena:
                boss["pos"] = -half_arena
                boss["dir"] = 1.0

        # Projectile Spawning (from Bosses aimed at players)
        self.difficulty += dt * 0.1
        
        # Select base targets for projectiles
        targets = []
        if self.p1_alive: targets.append(self.p1_pos)
        if self.p2_alive: targets.append(self.p2_pos)
        
        for boss in self.bosses:
            boss["timer"] -= dt
            if boss["timer"] <= 0:
                # Slower fire rate per boss (base 2.5 seconds instead of 1.0)
                boss["timer"] = max(0.5, 2.5 - (self.difficulty * 0.15))
                
                if targets:
                    target = random.choice(targets)
                    # Add some randomness to aim
                    target_x = target.x + random.uniform(-2.0, 2.0)
                    target_z = target.z + random.uniform(-2.0, 2.0)
                else:
                    target_x = 0.0
                    target_z = 0.0
                
                size = random.uniform(0.8, 2.5)
                # Even slower base speed: from 10.0-18.0 to 7.0-14.0
                speed = random.uniform(7.0, 14.0) + self.difficulty * 1.0
                
                # Determine boss world position
                if boss["side"] == "N":
                    boss_world_x = boss["pos"]
                    boss_world_z = self.arena_size / 2.0 + 3.0
                elif boss["side"] == "E":
                    boss_world_x = self.arena_size / 2.0 + 3.0
                    boss_world_z = boss["pos"]
                elif boss["side"] == "W":
                    boss_world_x = -self.arena_size / 2.0 - 3.0
                    boss_world_z = boss["pos"]

                dx = target_x - boss_world_x
                dz = target_z - boss_world_z
                length = math.sqrt(dx*dx + dz*dz)
                if length != 0:
                    vx = (dx / length) * speed
                    vz = (dz / length) * speed
                else:
                    vx, vz = 0.0, -speed
                    
                self.projectiles.append(Projectile(
                    pos=Vector3(boss_world_x, size/2.0 + 1.0, boss_world_z),
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
                    self.p1_lives -= 1
                    self.projectiles.remove(proj)
                    if self.p1_lives <= 0:
                        self.p1_alive = False
                    continue
                    
            # Collision Player 2
            if self.p2_alive:
                dist_x = proj.pos.x - self.p2_pos.x
                dist_z = proj.pos.z - self.p2_pos.z
                dist = math.sqrt(dist_x*dist_x + dist_z*dist_z)
                if dist < (proj.size / 2.0) + (self.player_size / 2.0):
                    self.p2_lives -= 1
                    self.projectiles.remove(proj)
                    if self.p2_lives <= 0:
                        self.p2_alive = False
                    continue

        # Drop Spheres Update -> Create Holes
        for ds in self.drop_spheres[:]:
            ds.pos.y -= ds.falling_speed * dt
            ds.warning_alpha = min(1.0, ds.warning_alpha + dt * 0.5)
            
            # Impact
            if ds.pos.y <= ds.size / 2.0:
                # Create a hole where it landed
                self.holes.append({"x": ds.pos.x, "z": ds.pos.z, "radius": ds.size / 2.0})
                self.drop_spheres.remove(ds)

        # Collision with holes (instant death if stepping inside)
        for hole in self.holes:
            if self.p1_alive:
                dist_x = self.p1_pos.x - hole["x"]
                dist_z = self.p1_pos.z - hole["z"]
                if math.sqrt(dist_x*dist_x + dist_z*dist_z) < hole["radius"] - (self.player_size / 2.0) + 0.2:
                    self.p1_alive = False
            
            if self.p2_alive:
                dist_x = self.p2_pos.x - hole["x"]
                dist_z = self.p2_pos.z - hole["z"]
                if math.sqrt(dist_x*dist_x + dist_z*dist_z) < hole["radius"] - (self.player_size / 2.0) + 0.2:
                    self.p2_alive = False

        # Bosses logic remains same

        # Check win condition (Survival Time)
        # Both players share the 30-second survival time now
        if not self.p1_alive and not self.p2_alive:
            self.game_over = True
            self.winner = 0 # No one survives
        else:
            self.survival_time -= dt
            if self.survival_time <= 0:
                self.game_over = True
                if self.singleplayer:
                    self.winner = 1 # P1 survives
                else:
                    if self.p1_alive and self.p2_alive:
                        self.winner = 3 # Both survive
                    elif self.p1_alive and not self.p2_alive:
                        self.winner = 1 # P1 survives
                    elif not self.p1_alive and self.p2_alive:
                        self.winner = 2 # P2 survives

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
            alpha = int(120 * ds.warning_alpha)
            # Warning circle
            draw_cylinder(Vector3(ds.pos.x, 0.05, ds.pos.z), ds.size/2.0, ds.size/2.0, 0.05, 32, Color(255, 100, 0, alpha))
            
        # Draw Holes (Red Zones)
        for hole in self.holes:
            # Fake hole effect
            draw_cylinder(Vector3(hole["x"], 0.08, hole["z"]), hole["radius"], hole["radius"], 0.08, 32, Color(150, 0, 0, 255))
            draw_cylinder_wires(Vector3(hole["x"], 0.08, hole["z"]), hole["radius"], hole["radius"], 0.08, 32, Color(255, 0, 0, 255))
            
        # Draw Players
        if self.p1_alive:
            draw_cube(self.p1_pos, self.player_size, self.player_size*2, self.player_size, self.p1_color)
            draw_cube_wires(self.p1_pos, self.player_size, self.player_size*2, self.player_size, WHITE)
            
        if self.p2_alive:
            draw_cube(self.p2_pos, self.player_size, self.player_size*2, self.player_size, self.p2_color)
            draw_cube_wires(self.p2_pos, self.player_size, self.player_size*2, self.player_size, WHITE)
            
        # Draw 4 Boss Enemies
        boss_size = 6.0
        eye_size = 1.0
        eye_offset_x = 1.5
        eye_offset_y = 1.0
        mouth_width = 3.0
        mouth_height = 0.5
        
        for boss in self.bosses:
            if boss["side"] == "N":
                boss_pos = Vector3(boss["pos"], 3.0, self.arena_size / 2.0 + 3.0)
                face_x = boss_pos.x
                face_z = boss_pos.z - (boss_size / 2.0) - 0.1
                left_eye_pos = Vector3(face_x + eye_offset_x, boss_pos.y + eye_offset_y, face_z)
                right_eye_pos = Vector3(face_x - eye_offset_x, boss_pos.y + eye_offset_y, face_z)
                left_eyebrow = Vector3(face_x + eye_offset_x, boss_pos.y + eye_offset_y + 0.8, face_z + 0.1)
                right_eyebrow = Vector3(face_x - eye_offset_x, boss_pos.y + eye_offset_y + 0.8, face_z + 0.1)
                mouth_pos = Vector3(face_x, boss_pos.y - 1.5, face_z)
                face_scale = Vector3(1, 1, 0.2)
                eyebrow_scale = Vector3(1.5, 0.3, 0.3)
                mouth_scale = Vector3(mouth_width, mouth_height, 0.2)
            elif boss["side"] == "S":
                boss_pos = Vector3(boss["pos"], 3.0, -self.arena_size / 2.0 - 3.0)
                face_x = boss_pos.x
                face_z = boss_pos.z + (boss_size / 2.0) + 0.1
                left_eye_pos = Vector3(face_x - eye_offset_x, boss_pos.y + eye_offset_y, face_z)
                right_eye_pos = Vector3(face_x + eye_offset_x, boss_pos.y + eye_offset_y, face_z)
                left_eyebrow = Vector3(face_x - eye_offset_x, boss_pos.y + eye_offset_y + 0.8, face_z - 0.1)
                right_eyebrow = Vector3(face_x + eye_offset_x, boss_pos.y + eye_offset_y + 0.8, face_z - 0.1)
                mouth_pos = Vector3(face_x, boss_pos.y - 1.5, face_z)
                face_scale = Vector3(1, 1, 0.2)
                eyebrow_scale = Vector3(1.5, 0.3, 0.3)
                mouth_scale = Vector3(mouth_width, mouth_height, 0.2)
            elif boss["side"] == "E":
                boss_pos = Vector3(self.arena_size / 2.0 + 3.0, 3.0, boss["pos"])
                face_x = boss_pos.x - (boss_size / 2.0) - 0.1
                face_z = boss_pos.z
                left_eye_pos = Vector3(face_x, boss_pos.y + eye_offset_y, face_z - eye_offset_x)
                right_eye_pos = Vector3(face_x, boss_pos.y + eye_offset_y, face_z + eye_offset_x)
                left_eyebrow = Vector3(face_x + 0.1, boss_pos.y + eye_offset_y + 0.8, face_z - eye_offset_x)
                right_eyebrow = Vector3(face_x + 0.1, boss_pos.y + eye_offset_y + 0.8, face_z + eye_offset_x)
                mouth_pos = Vector3(face_x, boss_pos.y - 1.5, face_z)
                face_scale = Vector3(0.2, 1, 1)
                eyebrow_scale = Vector3(0.3, 0.3, 1.5)
                mouth_scale = Vector3(0.2, mouth_height, mouth_width)
            elif boss["side"] == "W":
                boss_pos = Vector3(-self.arena_size / 2.0 - 3.0, 3.0, boss["pos"])
                face_x = boss_pos.x + (boss_size / 2.0) + 0.1
                face_z = boss_pos.z
                left_eye_pos = Vector3(face_x, boss_pos.y + eye_offset_y, face_z + eye_offset_x)
                right_eye_pos = Vector3(face_x, boss_pos.y + eye_offset_y, face_z - eye_offset_x)
                left_eyebrow = Vector3(face_x - 0.1, boss_pos.y + eye_offset_y + 0.8, face_z + eye_offset_x)
                right_eyebrow = Vector3(face_x - 0.1, boss_pos.y + eye_offset_y + 0.8, face_z - eye_offset_x)
                mouth_pos = Vector3(face_x, boss_pos.y - 1.5, face_z)
                face_scale = Vector3(0.2, 1, 1)
                eyebrow_scale = Vector3(0.3, 0.3, 1.5)
                mouth_scale = Vector3(0.2, mouth_height, mouth_width)

            # Body
            draw_cube(boss_pos, boss_size, boss_size, boss_size, RED)
            draw_cube_wires(boss_pos, boss_size, boss_size, boss_size, MAROON)
            
            # Left Eye
            draw_cube(left_eye_pos, face_scale.x * eye_size, face_scale.y * eye_size, face_scale.z * eye_size, BLACK)
            # Right Eye
            draw_cube(right_eye_pos, face_scale.x * eye_size, face_scale.y * eye_size, face_scale.z * eye_size, BLACK)
            
            # Angry eyebrows
            draw_cube(left_eyebrow, eyebrow_scale.x, eyebrow_scale.y, eyebrow_scale.z, BLACK)
            draw_cube(right_eyebrow, eyebrow_scale.x, eyebrow_scale.y, eyebrow_scale.z, BLACK)
            
            # Mouth
            draw_cube(mouth_pos, mouth_scale.x, mouth_scale.y, mouth_scale.z, BLACK)
            
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
            
        elif not self.game_over:
            # HUD
            if self.p1_alive:
                lives_txt = f"P1 LIVES: {self.p1_lives}"
                draw_text_shadow(lives_txt, 30, 30, 30, self.p1_color)
            else:
                draw_text_shadow("P1 DEAD", 30, 30, 30, GRAY)
                
            if not self.singleplayer:
                if self.p2_alive:
                    p2_lives_txt = f"P2 LIVES: {self.p2_lives}"
                    p2_w = measure_text(p2_lives_txt, 30)
                    draw_text_shadow(p2_lives_txt, SCREEN_WIDTH - p2_w - 30, 30, 30, self.p2_color)
                else:
                    dead_txt = "P2 DEAD"
                    dw = measure_text(dead_txt, 30)
                    draw_text_shadow(dead_txt, SCREEN_WIDTH - dw - 30, 30, 30, GRAY)
                
            time_txt = f"TIME: {max(0, math.ceil(self.survival_time))}"
            time_w = measure_text(time_txt, 40)
            draw_text_shadow(time_txt, SCREEN_WIDTH//2 - time_w//2, 30, 40, WHITE)
            
        if self.game_over:
            if self.winner == 1:
                txt = "PLAYER 1 SURVIVES! +1000"
                c = self.p1_color
            elif self.winner == 2:
                txt = "PLAYER 2 SURVIVES! +1000"
                c = self.p2_color
            elif self.winner == 3:
                txt = "BOTH SURVIVE! +1000 EACH"
                c = GOLD
            else:
                txt = "NO SURVIVORS!"
                c = GRAY
                
            ts = 60
            w = measure_text(txt, ts)
            
            # Panel
            panel_w = w + 80
            draw_rounded_panel(SCREEN_WIDTH//2 - panel_w//2, SCREEN_HEIGHT//2 - 60, panel_w, 120, fade(BLACK, 0.8))
            draw_text_shadow(txt, SCREEN_WIDTH//2 - w//2, SCREEN_HEIGHT//2 - ts//2, ts, c)
