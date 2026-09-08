import pygame
import random
import pytweening as tween

class Particle:
    def __init__(self, x, y, color, size, life):
        self.x = x
        self.y = y
        self.vx = random.uniform(-2, 2)
        self.vy = random.uniform(-2, 2)
        self.color = color
        self.size = size
        self.life = life
        self.max_life = life
        
    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.life -= 1
        
    def draw(self, surface):
        if self.life > 0:
            # Fade out by interpolating alpha or just shrinking size
            current_size = max(0, int(self.size * tween.easeOutQuad(self.life / self.max_life)))
            if current_size > 0:
                pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), current_size)

class EffectManager:
    def __init__(self):
        self.particles = []
        self.shake_duration = 0
        self.shake_intensity = 0
        
    def add_particles(self, x, y, color, count=10, size=5, life=30):
        for _ in range(count):
            self.particles.append(Particle(x, y, color, size, life))
            
    def screen_shake(self, duration=15, intensity=5):
        self.shake_duration = duration
        self.shake_intensity = intensity
        
    def update(self):
        for p in self.particles[:]:
            p.update()
            if p.life <= 0:
                self.particles.remove(p)
                
        if self.shake_duration > 0:
            self.shake_duration -= 1
            
    def get_shake_offset(self):
        if self.shake_duration > 0:
            return (
                random.randint(-self.shake_intensity, self.shake_intensity),
                random.randint(-self.shake_intensity, self.shake_intensity)
            )
        return (0, 0)
        
    def draw(self, surface):
        for p in self.particles:
            p.draw(surface)
