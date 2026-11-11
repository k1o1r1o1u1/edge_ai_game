# engine/effects.py
import pygame
import random
import pytweening as tween

class Particle:
    def __init__(self, x, y, color, size, life, vx=None, vy=None, shape="circle"):
        self.x = x
        self.y = y
        self.vx = vx if vx is not None else random.uniform(-3.5, 3.5)
        self.vy = vy if vy is not None else random.uniform(-3.5, 3.5)
        self.color = color
        self.size = size
        self.life = life
        self.max_life = life
        self.shape = shape
        
    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vx *= 0.95
        self.vy *= 0.95
        self.life -= 1
        
    def draw(self, surface):
        if self.life > 0:
            progress = max(0.0, min(1.0, self.life / self.max_life))
            current_size = max(1, int(self.size * tween.easeOutQuad(progress)))
            if self.shape == "spark":
                # Draw elongated spark line
                end_x = int(self.x + self.vx * 3)
                end_y = int(self.y + self.vy * 3)
                pygame.draw.line(surface, self.color, (int(self.x), int(self.y)), (end_x, end_y), max(1, current_size // 2))
            else:
                pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), current_size)

class FloatingText:
    def __init__(self, x, y, text, color, font, size=24, life=45):
        self.x = x
        self.y = y
        self.text = text
        self.color = color
        self.font = font
        self.life = life
        self.max_life = life
        self.vy = -1.6
        
    def update(self):
        self.y += self.vy
        self.vy *= 0.96
        self.life -= 1
        
    def draw(self, surface):
        if self.life > 0:
            rendered = self.font.render(self.text, True, self.color)
            # Simple shadow for crisp readability
            shadow = self.font.render(self.text, True, (0, 0, 0))
            surface.blit(shadow, (int(self.x) + 2, int(self.y) + 2))
            surface.blit(rendered, (int(self.x), int(self.y)))

class EffectManager:
    def __init__(self):
        self.particles = []
        self.floating_texts = []
        self.shake_duration = 0
        self.shake_intensity = 0
        self.flash_alpha = 0
        self.flash_color = (255, 255, 255)
        
    def add_particles(self, x, y, color, count=12, size=5, life=25, shape="circle"):
        for _ in range(count):
            self.particles.append(Particle(x, y, color, size, life, shape=shape))
            
    def add_floating_text(self, x, y, text, color, font):
        self.floating_texts.append(FloatingText(x, y, text, color, font))
        
    def screen_shake(self, duration=15, intensity=6):
        self.shake_duration = duration
        self.shake_intensity = intensity

    def trigger_flash(self, color=(255, 255, 255), alpha=160):
        self.flash_color = color
        self.flash_alpha = alpha
        
    def update(self):
        for p in self.particles[:]:
            p.update()
            if p.life <= 0:
                self.particles.remove(p)
                
        for ft in self.floating_texts[:]:
            ft.update()
            if ft.life <= 0:
                self.floating_texts.remove(ft)
                
        if self.shake_duration > 0:
            self.shake_duration -= 1
            
        if self.flash_alpha > 0:
            self.flash_alpha = max(0, self.flash_alpha - 20)
            
    def get_shake_offset(self):
        if self.shake_duration > 0:
            intensity = int(self.shake_intensity * (self.shake_duration / 15.0))
            intensity = max(1, intensity)
            return (
                random.randint(-intensity, intensity),
                random.randint(-intensity, intensity)
            )
        return (0, 0)
        
    def draw(self, surface):
        for p in self.particles:
            p.draw(surface)
        for ft in self.floating_texts:
            ft.draw(surface)
        if self.flash_alpha > 0:
            flash_surface = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
            flash_surface.fill((*self.flash_color, self.flash_alpha))
            surface.blit(flash_surface, (0, 0))
