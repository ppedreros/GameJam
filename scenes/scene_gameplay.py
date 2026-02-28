import math
from pyray import *
from entities.player import Player3D
from entities.platform import Platform3D
from utils.constants import SCREEN_WIDTH, SCREEN_HEIGHT, DIR_UP, DIR_RIGHT, DIR_DOWN, DIR_LEFT
from utils.draw_utils import draw_arrow, get_direction_vector, draw_rounded_panel, draw_rounded_panel_outline, draw_text_shadow
from utils.particles import ParticleSystem
from systems.input_handler import get_p1_pressed_direction, get_p2_pressed_direction
import random

# Neon color palettes that cycle based on score milestones
NEON_PALETTES = [
    Color(80, 50, 150, 255),    # Base violet
    Color(0, 200, 180, 255),    # Teal
    Color(200, 50, 120, 255),   # Hot pink
    Color(50, 120, 255, 255),   # Electric blue
    Color(255, 160, 0, 255),    # Orange
    Color(120, 255, 50, 255),   # Neon green
]

class BackgroundStar:
    """Floating particle in the background for atmosphere."""
    def __init__(self, render_w, render_h):
        self.x = random.uniform(0, render_w)
        self.y = random.uniform(0, render_h)
        self.speed = random.uniform(8, 30)
        self.size = random.randint(1, 3)
        self.alpha = random.randint(60, 180)
        self.render_w = render_w
        self.render_h = render_h

    def update(self, dt):
        self.y += self.speed * dt
        if self.y > self.render_h:
            self.y = 0
            self.x = random.uniform(0, self.render_w)

    def draw(self):
        draw_rectangle(int(self.x), int(self.y), self.size, self.size, Color(255, 255, 255, self.alpha))


class PlayerGameState:
    def __init__(self, parent_scene, is_player1=True, render_width=None):
        self.parent_scene = parent_scene
        self.is_player1 = is_player1
        self.camera = Camera3D()
        self.camera.position = Vector3(0.0, 8.0, -6.0)
        self.camera.target = Vector3(0.0, 1.0, 0.0)
        self.camera.up = Vector3(0.0, 1.0, 0.0)
        self.camera.fovy = 45.0
        self.camera.projection = CAMERA_PERSPECTIVE
        
        self.player = Player3D()
        self.player.color = Color(0, 180, 255, 255) if is_player1 else Color(255, 80, 80, 255)
        
        self.platforms = []
        self.platforms.append(Platform3D(0.0, 0.0, (DIR_UP,)))
        self.triggered_modifier = None
        self.modifier_active = False  # Set externally by GameplayScene
        self.darkness_timer = 0.0    # local timer managed here
        self.battle_cooldown = 0     # platforms until next battle tile is allowed
        
        for _ in range(20):
            self.generate_platform(self.platforms[-1])
            
        self.current_plat_index = 0
        self.game_over = False
        self.game_started = False
        self.MAX_TIME = 10.0
        self.time_left = self.MAX_TIME
        self.JUMP_DURATION = 0.2
        self.just_landed_on_battle = False
        self.stun_timer = 0.0
        self.jump_was_advance = False  # True only for successful forward jumps
        
        # Render target — full screen for single player, half for split
        self.render_width = render_width if render_width else int(SCREEN_WIDTH / 2)
        self.render_target = load_render_texture(self.render_width, SCREEN_HEIGHT)
        self.darkness_render_target = load_render_texture(self.render_width, SCREEN_HEIGHT)
        
        # --- Professional polish state ---
        self.particles = ParticleSystem()
        
        # Combo / streak
        self.combo = 0
        self.best_combo = 0
        self.combo_display_scale = 1.0  # For bounce animation
        self.combo_timer = 0.0  # Time since last combo increment
        
        # Screen effects
        self.screen_flash_alpha = 0.0
        self.screen_shake_x = 0.0
        self.screen_shake_y = 0.0
        self.screen_shake_timer = 0.0
        
        # Player visual effects
        self.player_squash = 1.0  # 1.0 = normal, <1 = squashed, >1 = stretched
        self.player_spin = 0.0   # Rotation angle during jump
        self.just_landed = False
        self.was_jumping = False
        
        # Background
        self.stars = [BackgroundStar(self.render_width, SCREEN_HEIGHT) for _ in range(40)]
        
        # Score milestone tracking
        self.last_milestone = 0
        self.session_best = 0
        self.battle_cooldown = 0  # platforms until next battle tile is allowed

    def generate_platform(self, last_plat):
        # Use first direction for positional offset
        offset = get_direction_vector(last_plat.directions[0])
        x = last_plat.pos.x + offset.x
        z = last_plat.pos.z + offset.z
        
        last_primary = last_plat.directions[0]
        possible_dirs = [DIR_UP, DIR_RIGHT, DIR_LEFT]
        if last_primary == DIR_UP:
            possible_dirs = [DIR_UP, DIR_RIGHT, DIR_LEFT]
        elif last_primary == DIR_RIGHT:
            possible_dirs = [DIR_UP, DIR_RIGHT, DIR_DOWN]
        elif last_primary == DIR_LEFT:
            possible_dirs = [DIR_UP, DIR_DOWN, DIR_LEFT]
        elif last_primary == DIR_DOWN:
            possible_dirs = [DIR_RIGHT, DIR_DOWN, DIR_LEFT]
            
        next_dir = random.choice(possible_dirs)
        
        modifier = None
        is_inverted = False
        is_battle = False
        directions = (next_dir,)
        
        if not self.modifier_active:
            roll = random.random()
            if self.player.score > 2 and roll < 0.04:
                modifier = "screen_swap"
            elif self.player.score > 4 and roll < 0.08:
                modifier = "darkness"
            elif self.player.score > 6 and roll < 0.14 and self.battle_cooldown <= 0:
                is_battle = True
                self.battle_cooldown = 8  # need at least 8 normal platforms before next battle
            elif self.player.score > 5 and roll < 0.21:
                # Double-arrow: pick a second distinct direction compatible with next_dir
                other_dirs = [d for d in [DIR_UP, DIR_RIGHT, DIR_DOWN, DIR_LEFT] if d != next_dir]
                second_dir = random.choice(other_dirs)
                directions = tuple(sorted([next_dir, second_dir]))
            elif self.player.score > 3 and roll < 0.30:
                is_inverted = True
            
        new_plat = Platform3D(x, z, directions, modifier=modifier, is_inverted=is_inverted, is_battle=is_battle)
        # Color based on score milestone — but special tiles override this above in Platform3D
        if not is_battle:
            palette_idx = (self.player.score // 10) % len(NEON_PALETTES)
            new_plat.color = NEON_PALETTES[palette_idx]
        if self.battle_cooldown > 0:
            self.battle_cooldown -= 1
        self.platforms.append(new_plat)

    def trigger_screen_shake(self, duration=0.3):
        self.screen_shake_timer = duration

    def update_logic(self, dt):
        # Update particles
        self.particles.update(dt)
        
        # Update stars
        for star in self.stars:
            star.update(dt)
        
        # Screen effects decay
        if self.screen_flash_alpha > 0:
            self.screen_flash_alpha -= dt * 3.0
            if self.screen_flash_alpha < 0:
                self.screen_flash_alpha = 0
        
        if self.darkness_timer > 0:
            self.darkness_timer -= dt
        
        if self.screen_shake_timer > 0:
            self.screen_shake_timer -= dt
            intensity = self.screen_shake_timer * 8.0
            self.screen_shake_x = random.uniform(-intensity, intensity)
            self.screen_shake_y = random.uniform(-intensity, intensity)
        else:
            self.screen_shake_x = 0
            self.screen_shake_y = 0
        
        # Combo display bounce decay
        if self.combo_display_scale > 1.0:
            self.combo_display_scale -= dt * 4.0
            if self.combo_display_scale < 1.0:
                self.combo_display_scale = 1.0
        
        # Combo timer — lose combo if too slow
        if self.game_started and self.combo > 0:
            self.combo_timer += dt
            if self.combo_timer > 2.5:
                self.combo = 0
        
        # Detect landing
        self.just_landed = False
        if self.was_jumping and not self.player.is_jumping and not self.game_over:
            self.just_landed = True
        self.was_jumping = self.player.is_jumping
        
        # Squash/stretch logic
        if self.player.is_jumping:
            t = self.player.jump_progress
            # Stretch during rise, squash during fall
            self.player_squash = 1.0 + 0.4 * math.sin(t * math.pi)
            self.player_spin = t * 360.0  # Full spin during jump
        elif self.just_landed:
            self.player_squash = 0.6  # Squash on landing
            self.player_spin = 0.0
            # Landing particles
            if self.player.pos.y >= 0:
                palette_idx = (self.player.score // 10) % len(NEON_PALETTES)
                self.particles.emit_landing_burst(
                    self.player.pos.x, self.player.pos.y, self.player.pos.z,
                    NEON_PALETTES[palette_idx], count=10
                )
        else:
            # Recover squash back to normal
            if self.player_squash < 1.0:
                self.player_squash += dt * 6.0
                if self.player_squash > 1.0:
                    self.player_squash = 1.0
            self.player_spin = 0.0
        
        # Trail effect during jump
        if self.player.is_jumping and not self.game_over:
            self.particles.emit_trail(
                self.player.pos.x, self.player.pos.y, self.player.pos.z,
                self.player.color
            )
        
        if self.game_over and not self.player.is_jumping:
            return
            
        if self.stun_timer > 0:
            self.stun_timer -= dt
            if self.stun_timer < 0:
                self.stun_timer = 0.0

        if self.game_started and not self.player.is_jumping:
            self.time_left -= dt
            if self.time_left <= 0:
                self.game_over = True
                self.player.is_jumping = True
                self.player.jump_target_pos = Vector3(self.player.pos.x, -20.0, self.player.pos.z)
                self.player.jump_progress = 0.0
                self.trigger_screen_shake(0.5)
                self.particles.emit_death_burst(
                    self.player.pos.x, self.player.pos.y, self.player.pos.z,
                    self.player.color, count=30
                )

        current_plat = self.platforms[self.current_plat_index]

        if self.player.is_jumping:
            self.player.jump_progress += dt / self.JUMP_DURATION
            if self.player.jump_progress >= 1.0:
                self.player.is_jumping = False
                self.player.pos = self.player.jump_target_pos
                if self.player.pos.y < 0:
                    self.game_over = True
                else:
                    # Only trigger modifiers/battle on a real forward jump, not a penalty bounce
                    if self.jump_was_advance:
                        landed_plat = self.platforms[self.current_plat_index]
                        mod = getattr(landed_plat, 'modifier', None)
                        if mod is not None:
                            self.triggered_modifier = mod
                        if getattr(landed_plat, 'is_battle', False):
                            landed_plat.is_battle = False
                            self.just_landed_on_battle = True
                    self.jump_was_advance = False  # reset every landing
            else:
                t = self.player.jump_progress
                px = self.player.jump_start_pos.x + (self.player.jump_target_pos.x - self.player.jump_start_pos.x) * t
                pz = self.player.jump_start_pos.z + (self.player.jump_target_pos.z - self.player.jump_start_pos.z) * t
                
                arc_height = 2.0 if not self.game_over else 0.0
                py = self.player.jump_start_pos.y + (self.player.jump_target_pos.y - self.player.jump_start_pos.y) * t
                py += math.sin(t * math.pi) * arc_height
                
                self.player.pos = Vector3(px, py, pz)
        
        elif not self.game_over:
            from systems.input_handler import get_p1_pressed_directions, get_p2_pressed_directions, get_p1_pressed_direction, get_p2_pressed_direction, get_p1_held_directions, get_p2_held_directions
            
            # Read inputs normally based on the swapped identity
            if self.is_player1:
                p_directions = get_p1_pressed_directions()
                p_held = get_p1_held_directions()
                p_pressed = get_p1_pressed_direction()
            else:
                p_directions = get_p2_pressed_directions()
                p_held = get_p2_held_directions()
                p_pressed = get_p2_pressed_direction()
            
            # Use pressed direction to detect activity, use directions to map all simultaneous 
            if p_pressed != -1:
                if not self.game_started:
                    self.game_started = True
                    
                if self.stun_timer > 0:
                    # Ignore input while stunned
                    pass
                else:
                    req_dirs = current_plat.directions
                    is_inverted = getattr(current_plat, 'is_inverted', False)
                    is_multi = len(req_dirs) > 1
                    
                    # For multi-arrow tiles use held keys (is_key_down) so the player
                    # doesn't need to hit both keys on the exact same frame
                    active_dirs = p_held if is_multi else p_directions
                    
                    if is_inverted:
                        p_overlap = set(p_directions).intersection(set(req_dirs))
                        if p_overlap:
                            # Pressed a forbidden key
                            self.stun_timer = 2.0
                        else:
                            # Successful jump on inverted tile
                            self._execute_jump()
                    else:
                        # Standard logic
                        if active_dirs == req_dirs:
                            self._execute_jump()
                        else: 
                            # For multi-arrow tiles: no penalty while building up the combo
                            if not is_multi and (p_pressed not in req_dirs or len(p_directions) != len(req_dirs)):
                                self.player.is_jumping = True
                                self.player.jump_start_pos = self.player.pos
                                self.player.jump_progress = 0.0
                                
                                self.time_left -= 1.5
                                if self.time_left <= 0:
                                    self.time_left = 0
                                    wrong_offset = get_direction_vector(p_pressed)
                                    self.player.jump_target_pos = Vector3(
                                        self.player.pos.x + wrong_offset.x, 
                                        -10.0, 
                                        self.player.pos.z + wrong_offset.z
                                    )
                                    self.game_over = True
                                else:
                                    self.player.jump_target_pos = self.player.pos

        target_y = self.player.pos.y if (self.game_over and self.player.pos.y < 2.0) else 2.0

        target_cam_pos = Vector3(
            self.player.pos.x - 6.0 * (math.sin(self.time_left) * 0.1 if self.game_started and not self.game_over else 0),
            target_y + 6.0,
            self.player.pos.z - 6.0
        ) 
        
        target_look_y = target_y - 1.0
        
        if getattr(self, 'first_frame', True):
            self.camera.position = target_cam_pos
            self.camera.target.x = self.player.pos.x
            self.camera.target.y = target_look_y
            self.camera.target.z = self.player.pos.z
            self.first_frame = False
        else:
            self.camera.position.x += (target_cam_pos.x - self.camera.position.x) * 5.0 * dt
            self.camera.position.y += (target_cam_pos.y - self.camera.position.y) * 5.0 * dt
            self.camera.position.z += (target_cam_pos.z - self.camera.position.z) * 5.0 * dt
            
            self.camera.target.x = self.player.pos.x
            self.camera.target.y += (target_look_y - self.camera.target.y) * 5.0 * dt
            self.camera.target.z = self.player.pos.z

    def _execute_jump(self):
        self.player.is_jumping = True
        self.player.jump_start_pos = self.player.pos
        self.player.jump_progress = 0.0
        self.jump_was_advance = True  # mark as a real forward jump
        
        self.current_plat_index += 1
        next_plat = self.platforms[self.current_plat_index]
        self.player.jump_target_pos = Vector3(next_plat.pos.x, 2.0, next_plat.pos.z)
        
        # Check swap!
        if getattr(next_plat, 'is_swap', False):
            self.parent_scene.trigger_swap()
            next_plat.is_swap = False # clear it so they don't trigger it again if jumping in place
            
        self.player.score += 1
        
        time_added = max(0.3, 1.0 - (self.player.score * 0.03))
        self.time_left = min(self.MAX_TIME, self.time_left + time_added)
        
        if len(self.platforms) - self.current_plat_index < 10:
            for _ in range(5):
                self.generate_platform(self.platforms[-1])

    def draw_to_texture(self):
        begin_texture_mode(self.render_target)
        
        clear_background(BLACK)
        
        # Evolving background gradient based on score
        milestone = (self.player.score // 10) % len(NEON_PALETTES)
        bg_top = Color(
            10 + milestone * 5, 
            15 + milestone * 3, 
            30 + milestone * 8, 
            255
        )
        bg_bot = Color(
            30 + milestone * 8, 
            45 + milestone * 5, 
            80 + milestone * 10, 
            255
        )
        draw_rectangle_gradient_v(0, 0, self.render_width, SCREEN_HEIGHT, bg_top, bg_bot)
        
        # Draw starfield
        for star in self.stars:
            star.draw()

        begin_mode_3d(self.camera)
        
        # Grid floor for depth perception
        grid_y = -2.0
        for gx in range(-20, 21, 4):
            for gz in range(-20, 21, 4):
                wx = self.player.pos.x + gx
                wz = self.player.pos.z + gz
                draw_cube(Vector3(wx, grid_y, wz), 3.8, 0.05, 3.8, Color(40, 40, 60, 60))
        
        # Draw platforms
        start_idx = max(0, self.current_plat_index - 3)
        end_idx = min(len(self.platforms), self.current_plat_index + 15)
        
        t_now = get_time()
        
        for i in range(start_idx, end_idx):
            plat = self.platforms[i]
            dist_from_current = i - self.current_plat_index
            
            # Color base constante para todas las plataformas
            base_plat_color = Color(80, 50, 150, 255) # Base violeta
            if getattr(plat, 'is_battle', False):
                pulse_m = (math.sin(t_now * 10.0) + 1.0) / 2.0
                base_plat_color = Color(255, int(200 + 55 * pulse_m), 0, 255)  # Oro pulsante
            elif getattr(plat, 'modifier', None) == "screen_swap":
                pulse_m = (math.sin(t_now * 8.0) + 1.0) / 2.0
                base_plat_color = Color(0, 255, 255, int(150 + 105 * pulse_m))
            elif getattr(plat, 'modifier', None) == "darkness":
                pulse_m = (math.sin(t_now * 5.0) + 1.0) / 2.0
                base_plat_color = Color(255, 140, 0, int(180 + 75 * pulse_m)) # Naranja fuego
            
            if i < self.current_plat_index:
                # Past platforms: fade and sink
                fade_t = max(0.0, 1.0 - (self.current_plat_index - i) * 0.4)
                sink = (self.current_plat_index - i) * 0.3
                pos = Vector3(plat.pos.x, plat.pos.y - sink, plat.pos.z)
                c = Color(base_plat_color.r, base_plat_color.g, base_plat_color.b, int(255 * fade_t))
                draw_cube_v(pos, plat.size, c)
            elif i == self.current_plat_index:
                # Current platform: pulsing glow ring
                pulse = (math.sin(t_now * 6.0) + 1.0) / 2.0
                glow_size = Vector3(plat.size.x + 0.3 + pulse * 0.3, 0.1, plat.size.z + 0.3 + pulse * 0.3)
                if getattr(plat, 'is_battle', False):
                    face_color = base_plat_color
                    glow_color = Color(255, 220, 0, int(120 + 120 * pulse))
                elif getattr(plat, 'modifier', None) == "screen_swap":
                    face_color = base_plat_color
                    glow_color = Color(0, 220, 255, int(80 + 80 * pulse))
                elif getattr(plat, 'modifier', None) == "darkness":
                    face_color = base_plat_color
                    glow_color = Color(255, 100, 0, int(80 + 80 * pulse))
                else:
                    face_color = LIME
                    glow_color = Color(100, 255, 100, int(60 + 40 * pulse))
                draw_cube_v(Vector3(plat.pos.x, plat.pos.y - 0.5, plat.pos.z), glow_size, glow_color)
                draw_cube_v(plat.pos, plat.size, face_color)
                draw_cube_wires_v(plat.pos, plat.size, BLACK)
            else:
                # Future platforms: gentle bobbing
                bob = math.sin(t_now * 2.0 + i * 0.7) * 0.15
                pos = Vector3(plat.pos.x, plat.pos.y + bob, plat.pos.z)
                draw_cube_v(pos, plat.size, base_plat_color)
                if getattr(plat, 'is_battle', False):
                    # Glowing gold wire border for battle tiles
                    pulse_b = (math.sin(t_now * 10.0) + 1.0) / 2.0
                    border_size = Vector3(plat.size.x + 0.15 + pulse_b * 0.2, plat.size.y + 0.15, plat.size.z + 0.15 + pulse_b * 0.2)
                    draw_cube_wires_v(pos, border_size, Color(255, 220, 0, int(180 + 75 * pulse_b)))
                    draw_cube_wires_v(pos, plat.size, Color(255, 255, 255, 200))
                else:
                    draw_cube_wires_v(pos, plat.size, Color(0, 0, 0, 120))
            
            if i >= self.current_plat_index and not plat.is_battle:
                draw_arrow(plat)
        
        # Player shadow blob on ground
        if self.player.pos.y > 0:
            shadow_scale = max(0.3, 1.0 - self.player.pos.y * 0.15)
            draw_cube(
                Vector3(self.player.pos.x, 0.55, self.player.pos.z),
                0.8 * shadow_scale, 0.02, 0.8 * shadow_scale,
                Color(0, 0, 0, int(80 * shadow_scale))
            )

        # Draw player with squash/stretch
        sx = 1.0 / max(0.5, self.player_squash)
        sy = self.player_squash
        sz = 1.0 / max(0.5, self.player_squash)
        player_size = Vector3(
            self.player.size.x * sx,
            self.player.size.y * sy,
            self.player.size.z * sz
        )
        draw_cube_v(self.player.pos, player_size, self.player.color)
        draw_cube_wires_v(self.player.pos, player_size, Color(255, 255, 255, 80))
        
        # Draw 3D particles
        self.particles.draw_3d()

        end_mode_3d()
        
        # --- Darkness modifier overlay ---
        if self.darkness_timer > 0:
            FADE_TIME = 0.8
            if self.darkness_timer > 6.0 - FADE_TIME:
                alpha_ratio = (6.0 - self.darkness_timer) / FADE_TIME
            elif self.darkness_timer < FADE_TIME:
                alpha_ratio = self.darkness_timer / FADE_TIME
            else:
                alpha_ratio = 1.0
            
            # Soft base tint (not fully opaque - gives a smoky feel instead of hard black)
            base_alpha = int(190 * alpha_ratio)
            draw_rectangle(0, 0, self.render_width, SCREEN_HEIGHT, Color(5, 5, 18, base_alpha))
            
            # Vignette: dark gradients from each edge to create soft falloff
            vign_layers = 14
            for layer in range(vign_layers):
                progress = layer / vign_layers
                layer_alpha = int(alpha_ratio * 180 * (1.0 - progress) ** 2)
                thickness = int(self.render_width * 0.4 * (1.0 - progress))
                # Left edge
                draw_rectangle_gradient_h(0, 0, thickness, SCREEN_HEIGHT,
                    Color(0, 0, 12, layer_alpha), Color(0, 0, 12, 0))
                # Right edge
                draw_rectangle_gradient_h(self.render_width - thickness, 0, thickness, SCREEN_HEIGHT,
                    Color(0, 0, 12, 0), Color(0, 0, 12, layer_alpha))
                # Top edge
                draw_rectangle_gradient_v(0, 0, self.render_width, int(SCREEN_HEIGHT * 0.4 * (1.0 - progress)),
                    Color(0, 0, 12, layer_alpha), Color(0, 0, 12, 0))
                # Bottom edge
                h = int(SCREEN_HEIGHT * 0.4 * (1.0 - progress))
                draw_rectangle_gradient_v(0, SCREEN_HEIGHT - h, self.render_width, h,
                    Color(0, 0, 12, 0), Color(0, 0, 12, layer_alpha))
            
            # Second 3D pass in a dedicated render texture to avoid z-fighting (fresh depth buffer)
            begin_texture_mode(self.darkness_render_target)
            clear_background(Color(0, 0, 0, 0))  # transparent
            begin_mode_3d(self.camera)
            curr_plat = self.platforms[self.current_plat_index]
            pulse = (math.sin(t_now * 6.0) + 1.0) / 2.0
            glow_size = Vector3(curr_plat.size.x + 0.4 + pulse * 0.4, 0.12, curr_plat.size.z + 0.4 + pulse * 0.4)
            draw_cube_v(Vector3(curr_plat.pos.x, curr_plat.pos.y - 0.5, curr_plat.pos.z), glow_size, Color(100, 255, 100, int(80 + 60 * pulse)))
            draw_cube_v(curr_plat.pos, curr_plat.size, LIME)
            draw_cube_wires_v(curr_plat.pos, curr_plat.size, BLACK)
            draw_arrow(curr_plat)
            if self.current_plat_index + 1 < len(self.platforms):
                next_plat = self.platforms[self.current_plat_index + 1]
                bob = math.sin(t_now * 2.0) * 0.15
                npos = Vector3(next_plat.pos.x, next_plat.pos.y + bob, next_plat.pos.z)
                draw_cube_v(npos, next_plat.size, Color(80, 50, 150, 255))
                draw_cube_wires_v(npos, next_plat.size, Color(200, 200, 255, 160))
                draw_arrow(next_plat)
            sx = 1.0 / max(0.5, self.player_squash)
            sy = self.player_squash
            psize = Vector3(self.player.size.x * sx, self.player.size.y * sy, self.player.size.z * sx)
            draw_cube_v(self.player.pos, psize, self.player.color)
            draw_cube_wires_v(self.player.pos, psize, Color(255, 255, 255, 80))
            end_mode_3d()
            end_texture_mode()
            
            # 'end_texture_mode' exits ALL texture mode - must re-enter main render target
            # before compositing the darkness texture on top of it
            begin_texture_mode(self.render_target)
            drk_src = Rectangle(0, self.darkness_render_target.texture.height,
                                self.darkness_render_target.texture.width,
                                -self.darkness_render_target.texture.height)
            drk_dst = Rectangle(0, 0, self.render_width, SCREEN_HEIGHT)
            draw_texture_pro(self.darkness_render_target.texture, drk_src, drk_dst, Vector2(0, 0), 0.0, WHITE)

        # --- 2D Overlays (with screen shake offset) ---
        shake_x = int(self.screen_shake_x)
        shake_y = int(self.screen_shake_y)
        
        # Screen flash
        if self.screen_flash_alpha > 0:
            draw_rectangle(0, 0, self.render_width, SCREEN_HEIGHT, Color(255, 255, 255, int(self.screen_flash_alpha * 255)))
        
        # Speed lines at high combo
        if self.combo >= 5 and self.game_started and not self.game_over:
            intensity = min(1.0, self.combo / 15.0)
            for _ in range(int(intensity * 8)):
                lx = random.randint(0, self.render_width)
                ly = random.randint(0, SCREEN_HEIGHT)
                ll = random.randint(30, 80)
                draw_line(lx, ly, lx + random.randint(-5, 5), ly + ll, Color(255, 255, 255, int(40 * intensity)))
        
        # Draw score popups
        self.particles.draw_2d()

        if not self.game_over:
            # --- Top HUD ---
            panel_width = 160
            panel_height = 80
            panel_x = 20 + shake_x
            panel_y = 20 + shake_y
            
            draw_rounded_panel(panel_x, panel_y, panel_width, panel_height, fade(DARKBLUE, 0.5), shadow_offset=6, roundness=0.3)
            draw_rounded_panel_outline(panel_x, panel_y, panel_width, panel_height, fade(WHITE, 0.15), segments=10, thickness=2)
            
            draw_text_shadow("SCORE", panel_x + 20, panel_y + 10, 15, LIGHTGRAY)
            
            score_text = str(self.player.score)
            scale_pop = 1.0 + max(0, 0.5 - (self.MAX_TIME - self.time_left)) if self.game_started else 1.0 
            font_size = int(35 * scale_pop)
            draw_text_shadow(score_text, panel_x + 20, panel_y + 30, font_size, GOLD)
            
            # Player ID
            pid_text = "P1 (WASD)" if self.is_player1 else "P2 (ARROWS)"
            pid_color = Color(0, 180, 255, 255) if self.is_player1 else Color(255, 80, 80, 255)
            draw_text_shadow(pid_text, self.render_width - measure_text(pid_text, 20) - 20 + shake_x, 20 + shake_y, 20, pid_color)
            
            # --- Combo Counter ---
            if self.combo >= 2 and self.game_started:
                combo_text = f"x{self.combo}"
                combo_fs = int(30 * self.combo_display_scale)
                combo_w = measure_text(combo_text, combo_fs)
                combo_x = self.render_width // 2 - combo_w // 2 + shake_x
                combo_y = 70 + shake_y
                
                # Combo color intensifies
                combo_r = min(255, 150 + self.combo * 10)
                combo_g = max(50, 255 - self.combo * 15)
                combo_color = Color(combo_r, combo_g, 50, 255)
                
                draw_text_shadow(combo_text, combo_x, combo_y, combo_fs, combo_color)
            
            # --- Timer Bar ---
            if self.game_started:
                bar_w = 300
                bar_h = 24
                bar_x = self.render_width // 2 - bar_w // 2 + shake_x
                bar_y = 30 + shake_y
                
                draw_rounded_panel(bar_x, bar_y, bar_w, bar_h, fade(BLACK, 0.6), shadow_offset=4, roundness=0.5)
                draw_rounded_panel_outline(bar_x, bar_y, bar_w, bar_h, fade(WHITE, 0.1), segments=10, thickness=2)
                
                fill_ratio = max(0.0, self.time_left / self.MAX_TIME)
                
                r = int(255 * (1 - fill_ratio))
                g = int(255 * fill_ratio)
                b = 50
                bar_color = Color(r, g, b, 255)
                
                if self.time_left < 0.5:
                    pulse_amt = (math.sin(get_time() * 20.0) + 1.0) / 2.0
                    bar_color = color_alpha(bar_color, 0.5 + 0.5 * pulse_amt)
                
                if fill_ratio > 0:
                    fill_rect = Rectangle(bar_x + 3, bar_y + 3, (bar_w - 6) * fill_ratio, bar_h - 6)
                    draw_rectangle_rounded(fill_rect, 0.5, 10, bar_color)
                    glow_rect = Rectangle(bar_x + 6, bar_y + 5, ((bar_w - 6) * fill_ratio) - 6, (bar_h - 6) // 3)
                    if glow_rect.width > 0:
                        draw_rectangle_rounded(glow_rect, 0.5, 10, fade(WHITE, 0.3))
                
            else:
                prompt = "Press W to start!" if self.is_player1 else "Press UP to start!"
                prompt_w = measure_text(prompt, 20)
                
                bob = math.sin(get_time() * 3.0) * 5.0
                prompt_y = int(SCREEN_HEIGHT // 2 - 120 + bob)
                
                pulse = (math.sin(get_time() * 5.0) + 1.0) / 2.0
                
                draw_rounded_panel(self.render_width // 2 - prompt_w // 2 - 20, prompt_y - 10, prompt_w + 40, 40, fade(BLACK, 0.6), shadow_offset=6, roundness=0.5)
                draw_rounded_panel_outline(self.render_width // 2 - prompt_w // 2 - 20, prompt_y - 10, prompt_w + 40, 40, fade(YELLOW, 0.3 + 0.5 * pulse), segments=10, thickness=2)
                
                draw_text_shadow(prompt, self.render_width // 2 - prompt_w // 2, prompt_y, 20, YELLOW)

            # --- Stun Overlay ---
            if self.stun_timer > 0:
                overlay_alpha = min(0.5, self.stun_timer)
                draw_rectangle(0, 0, self.render_width, SCREEN_HEIGHT, fade(RED, overlay_alpha))
                
                stun_text = "STUNNED!"
                font_size = 50 + int(math.sin(self.stun_timer * 15.0) * 10)
                tw = measure_text(stun_text, font_size)
                draw_text_shadow(stun_text, self.render_width//2 - tw//2, SCREEN_HEIGHT//2 - 100, font_size, YELLOW, shadow_offset=4)
                
                sub_text = f"{self.stun_timer:.1f}s"
                tw2 = measure_text(sub_text, 30)
                draw_text_shadow(sub_text, self.render_width//2 - tw2//2, SCREEN_HEIGHT//2 - 40, 30, WHITE)
                
            # --- Swap Flash ---
            if getattr(self.parent_scene, 'show_swap_flash', 0) > 0:
                alpha = min(1.0, self.parent_scene.show_swap_flash)
                draw_rectangle(0, 0, self.render_width, SCREEN_HEIGHT, fade(WHITE, alpha * 0.5))
                
        end_texture_mode()

class GameplayScene:
    def __init__(self, game, singleplayer=False):
        self.game = game
        self.show_swap_flash = 0.0
        self.singleplayer = singleplayer
        
        self.active_modifier = None
        self.active_modifier_timer = 0.0
        self.modifier_transition = 0.0   # 0.0 = normal, 1.0 = fully swapped
        self.modifier_target = 0.0       # target to lerp towards
        
        if singleplayer:
            self.p1_state = PlayerGameState(self, is_player1=True, render_width=SCREEN_WIDTH)
            self.p2_state = None
        else:
            self.p1_state = PlayerGameState(self, is_player1=True)
            self.p2_state = PlayerGameState(self, is_player1=False)

    def trigger_swap(self):
        self.show_swap_flash = 1.0
        
        # Swap identities
        self.p1_state.is_player1, self.p2_state.is_player1 = self.p2_state.is_player1, self.p1_state.is_player1
        # Swap colors
        self.p1_state.player.color, self.p2_state.player.color = self.p2_state.player.color, self.p1_state.player.color
        # Swap scores
        self.p1_state.player.score, self.p2_state.player.score = self.p2_state.player.score, self.p1_state.player.score
        # Swap time bars
        self.p1_state.time_left, self.p2_state.time_left = self.p2_state.time_left, self.p1_state.time_left
        # Swap stun status
        self.p1_state.stun_timer, self.p2_state.stun_timer = self.p2_state.stun_timer, self.p1_state.stun_timer

    def update(self, dt):
        if self.show_swap_flash > 0:
            self.show_swap_flash -= dt * 2.0
            
        if self.p1_state.just_landed_on_battle or self.p2_state.just_landed_on_battle:
            self.p1_state.just_landed_on_battle = False
            self.p2_state.just_landed_on_battle = False
            from scenes.scene_battle import BattleScene
            self.game.change_scene(BattleScene(self.game, self))
            return
            
        self.p1_state.update_logic(dt)
        if self.p2_state:
            self.p2_state.update_logic(dt)

        # --- Modifier processing ---
        if self.active_modifier_timer > 0:
            self.active_modifier_timer -= dt
            if self.active_modifier_timer <= 0:
                self.modifier_target = 0.0  # screen_swap lerps back
                
        p1_mod = getattr(self.p1_state, 'triggered_modifier', None)
        p2_mod = getattr(self.p2_state, 'triggered_modifier', None) if self.p2_state else None
        
        if p1_mod or p2_mod:
            triggered = p1_mod or p2_mod
            if triggered == "minigame" and not self.singleplayer:
                # Trigger minigame switch
                from scenes.scene_minigame import MinigameScene
                minigame = MinigameScene(
                    self.game, self, 
                    self.p1_state.player.score, 
                    self.p2_state.player.score
                )
                self.game.change_scene(minigame)
                self.p1_state.triggered_modifier = None
                self.p2_state.triggered_modifier = None
                return # Skip rest of update this frame
            else:
                self.active_modifier = triggered
                self.active_modifier_timer = 6.0
                if triggered == "screen_swap":
                    self.modifier_target = 1.0
                self.p1_state.triggered_modifier = None
                if self.p2_state:
                    self.p2_state.triggered_modifier = None
        
        # Sync darkness_timer to both states
        darkness_t = self.active_modifier_timer if self.active_modifier == "darkness" else 0.0
        self.p1_state.darkness_timer = darkness_t
        if self.p2_state:
            self.p2_state.darkness_timer = darkness_t
        
        # Sync modifier_active flag so generation is gated
        modifier_is_active = self.active_modifier_timer > 0
        self.p1_state.modifier_active = modifier_is_active
        if self.p2_state:
            self.p2_state.modifier_active = modifier_is_active
        
        # Smooth screen_swap lerp
        SWAP_SPEED = 3.5
        self.modifier_transition += (self.modifier_target - self.modifier_transition) * SWAP_SPEED * dt

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
        self.p1_state.draw_to_texture()
        
        clear_background(BLACK)
        
        if self.singleplayer:
            # Full screen: slide-lerp the mirror effect via x offset
            t = self.modifier_transition
            source_w = self.p1_state.render_target.texture.width
            source_h = self.p1_state.render_target.texture.height
            source_rec = Rectangle(source_w * t, source_h, source_w * (1.0 - 2.0 * t), -source_h)
            dest = Rectangle(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT)
            draw_texture_pro(self.p1_state.render_target.texture, source_rec, dest, Vector2(0, 0), 0.0, WHITE)
        else:
            self.p2_state.draw_to_texture()
            
            half_w = self.p1_state.render_width
            source_rec = Rectangle(0, self.p1_state.render_target.texture.height, self.p1_state.render_target.texture.width, -self.p1_state.render_target.texture.height)
            
            t = self.modifier_transition
            # Lerp x positions: p1 slides from 0→half_w, p2 slides from half_w→0
            p1_x = t * half_w
            p2_x = half_w + t * (-half_w)
            p1_dest = Rectangle(p1_x, 0, half_w, SCREEN_HEIGHT)
            p2_dest = Rectangle(p2_x, 0, half_w, SCREEN_HEIGHT)
                
            draw_texture_pro(self.p1_state.render_target.texture, source_rec, p1_dest, Vector2(0, 0), 0.0, WHITE)
            draw_texture_pro(self.p2_state.render_target.texture, source_rec, p2_dest, Vector2(0, 0), 0.0, WHITE)
            
            # Animated separator
            t = get_time()
            for y_seg in range(0, SCREEN_HEIGHT, 4):
                ratio = y_seg / SCREEN_HEIGHT
                pulse = (math.sin(t * 3.0 + ratio * 10.0) + 1.0) / 2.0
                r = int(pulse * 255)
                g = int((1 - pulse) * 255)
                b = 255
                draw_rectangle(half_w - 2, y_seg, 4, 4, Color(r, g, b, 200))
            draw_rectangle(half_w - 1, 0, 2, SCREEN_HEIGHT, Color(255, 255, 255, 100))
        
        # ─── Countdown warning before modifier expires ───────────────────
        WARN_TIME = 3.0
        if 0 < self.active_modifier_timer <= WARN_TIME and self.active_modifier is not None:
            warn_t = get_time()
            # Flash speed increases as time runs out
            flash_speed = 4.0 + (WARN_TIME - self.active_modifier_timer) * 6.0
            pulse_warn = (math.sin(warn_t * flash_speed) + 1.0) / 2.0
            border_alpha = int(100 + 155 * pulse_warn)
            border_thick = 8
            warn_color = Color(255, 80, 0, border_alpha)
            # Border around full screen
            draw_rectangle(0, 0, SCREEN_WIDTH, border_thick, warn_color)
            draw_rectangle(0, SCREEN_HEIGHT - border_thick, SCREEN_WIDTH, border_thick, warn_color)
            draw_rectangle(0, 0, border_thick, SCREEN_HEIGHT, warn_color)
            draw_rectangle(SCREEN_WIDTH - border_thick, 0, border_thick, SCREEN_HEIGHT, warn_color)
            # Countdown text
            secs_left = math.ceil(self.active_modifier_timer)
            countdown_txt = f"¡{secs_left}!"
            txt_size = 60
            txt_w = measure_text(countdown_txt, txt_size)
            txt_alpha = int(180 + 75 * pulse_warn)
            draw_text(countdown_txt, SCREEN_WIDTH // 2 - txt_w // 2, 20, txt_size, Color(255, 200, 0, txt_alpha))

