import math
import random
from pyray import *

def _ensure_color(c):
    """Normalize a color value to a Color object (pyray colors can be tuples)."""
    if isinstance(c, tuple):
        return Color(c[0], c[1], c[2], c[3] if len(c) > 3 else 255)
    return c

class Particle:
    """A single particle with position, velocity, lifetime, color, and size."""
    def __init__(self, x, y, z, vx, vy, vz, lifetime, color, size=0.15):
        self.x = x
        self.y = y
        self.z = z
        self.vx = vx
        self.vy = vy
        self.vz = vz
        self.lifetime = lifetime
        self.max_lifetime = lifetime
        self.color = _ensure_color(color)
        self.size = size
        self.alive = True

    def update(self, dt):
        if not self.alive:
            return
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.z += self.vz * dt
        self.vy -= 9.8 * dt  # gravity
        self.lifetime -= dt
        if self.lifetime <= 0:
            self.alive = False

    def draw_3d(self):
        if not self.alive:
            return
        t = self.lifetime / self.max_lifetime
        alpha = int(255 * t)
        c = Color(self.color.r, self.color.g, self.color.b, alpha)
        s = self.size * t
        draw_cube(Vector3(self.x, self.y, self.z), s, s, s, c)


class ScorePopup:
    """A floating 2D '+N' text that rises and fades out."""
    def __init__(self, text, x, y, color):
        self.text = text
        self.x = x
        self.y = y
        self.color = _ensure_color(color)
        self.lifetime = 0.8
        self.max_lifetime = 0.8
        self.alive = True

    def update(self, dt):
        if not self.alive:
            return
        self.y -= 80 * dt  # float upward
        self.lifetime -= dt
        if self.lifetime <= 0:
            self.alive = False

    def draw_2d(self, offset_x=0):
        if not self.alive:
            return
        t = self.lifetime / self.max_lifetime
        alpha = int(255 * t)
        scale = 1.0 + (1.0 - t) * 0.5  # grows slightly as it fades
        font_size = int(24 * scale)
        c = Color(self.color.r, self.color.g, self.color.b, alpha)
        tw = measure_text(self.text, font_size)
        draw_text(self.text, int(self.x - tw // 2 + offset_x), int(self.y), font_size, c)


class ParticleSystem:
    """Manages 3D particles and 2D score popups."""
    def __init__(self):
        self.particles = []
        self.popups = []

    def emit_landing_burst(self, x, y, z, color, count=12):
        """Burst of particles when landing on a platform."""
        for _ in range(count):
            angle = random.uniform(0, math.pi * 2)
            speed = random.uniform(1.5, 4.0)
            vx = math.cos(angle) * speed
            vz = math.sin(angle) * speed
            vy = random.uniform(1.0, 3.5)
            lifetime = random.uniform(0.3, 0.7)
            size = random.uniform(0.08, 0.2)
            self.particles.append(Particle(x, y + 0.5, z, vx, vy, vz, lifetime, color, size))

    def emit_death_burst(self, x, y, z, color, count=25):
        """Big explosion on death."""
        for _ in range(count):
            vx = random.uniform(-5, 5)
            vy = random.uniform(2, 8)
            vz = random.uniform(-5, 5)
            lifetime = random.uniform(0.5, 1.2)
            size = random.uniform(0.1, 0.3)
            self.particles.append(Particle(x, y, z, vx, vy, vz, lifetime, color, size))

    def emit_trail(self, x, y, z, color):
        """Single particle for trail effect."""
        vx = random.uniform(-0.3, 0.3)
        vy = random.uniform(-0.1, 0.5)
        vz = random.uniform(-0.3, 0.3)
        lifetime = random.uniform(0.15, 0.35)
        size = random.uniform(0.05, 0.12)
        color = _ensure_color(color)
        c = Color(color.r, color.g, color.b, 180)
        self.particles.append(Particle(x, y - 0.3, z, vx, vy, vz, lifetime, c, size))

    def add_score_popup(self, text, screen_x, screen_y, color):
        self.popups.append(ScorePopup(text, screen_x, screen_y, color))

    def update(self, dt):
        for p in self.particles:
            p.update(dt)
        for p in self.popups:
            p.update(dt)
        self.particles = [p for p in self.particles if p.alive]
        self.popups = [p for p in self.popups if p.alive]

    def draw_3d(self):
        for p in self.particles:
            p.draw_3d()

    def draw_2d(self, offset_x=0):
        for p in self.popups:
            p.draw_2d(offset_x)
