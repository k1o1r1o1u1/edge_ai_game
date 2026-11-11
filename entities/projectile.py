# entities/projectile.py
import pygame
import math
import random
from config.settings import *

class EnergyProjectile:
    """Flying energy shockwave / fist or mega beam projectile"""
    def __init__(self, x, y, target_x, damage, proj_type="PUNCH", is_max=False):
        self.x = float(x)
        self.y = float(y)
        self.target_x = float(target_x)
        self.damage = damage
        self.proj_type = proj_type  # "PUNCH" or "SPECIAL"
        self.is_max = is_max
        self.alive = True
        
        if proj_type == "PUNCH":
            self.speed = PROJECTILE_SPEED_PUNCH
            self.width = 44
            self.height = 32
            self.color = (0, 240, 255)
            self.core_color = (255, 255, 255)
        else: # SPECIAL
            self.speed = PROJECTILE_SPEED_SPECIAL
            self.width = 90 if is_max else 65
            self.height = 70 if is_max else 50
            self.color = (255, 215, 0) if is_max else (200, 80, 255)
            self.core_color = (255, 255, 255)
            
        self.rect = pygame.Rect(int(self.x), int(self.y - self.height // 2), self.width, self.height)
        self.trail_particles = []

    def update(self):
        self.x += self.speed
        self.rect.x = int(self.x)
        
        # Check if reached target
        if self.x + self.width >= self.target_x:
            self.alive = False
            return True  # Impacted
            
        return False

    def draw(self, surface):
        if not self.alive:
            return
            
        t = pygame.time.get_ticks() / 1000.0
        
        if self.proj_type == "PUNCH":
            # Sonic Energy Fist / Shockwave Crescent
            surf = pygame.Surface((self.width + 20, self.height + 20), pygame.SRCALPHA)
            center = (self.width // 2 + 10, self.height // 2 + 10)
            
            # Trailing glow
            pygame.draw.ellipse(surf, (*self.color, 140), (0, 4, self.width + 10, self.height + 12))
            # Glowing Crescent Head
            pygame.draw.arc(surf, self.core_color, (self.width // 2 - 10, 5, 26, self.height + 10), -math.pi/2, math.pi/2, 6)
            # Energy lines behind
            pygame.draw.line(surf, (0, 240, 255, 180), (10, center[1] - 8), (center[0], center[1] - 8), 3)
            pygame.draw.line(surf, (0, 240, 255, 180), (10, center[1] + 8), (center[0], center[1] + 8), 3)
            
            surface.blit(surf, (self.rect.x - 10, self.rect.y - 10))
            
        else: # SPECIAL
            # Massive pulsing plasma sphere / Hadouken
            w = self.width + 30
            h = self.height + 30
            surf = pygame.Surface((w, h), pygame.SRCALPHA)
            center = (w // 2, h // 2)
            
            # Multi-layer plasma pulse
            pulse = math.sin(t * 16.0) * 4
            radius = int((self.height // 2) + pulse)
            
            # Outer aura
            aura_col = (*self.color, 120 if self.is_max else 90)
            pygame.draw.circle(surf, aura_col, center, radius + 10)
            # Core
            pygame.draw.circle(surf, self.color, center, radius)
            pygame.draw.circle(surf, self.core_color, center, max(4, radius - 10))
            
            # Plasma spark ring
            spark_col = (255, 255, 200) if self.is_max else (255, 180, 255)
            for i in range(5):
                angle = t * 10 + i * (math.pi * 2 / 5)
                sx = int(center[0] + math.cos(angle) * (radius + 6))
                sy = int(center[1] + math.sin(angle) * (radius + 6))
                pygame.draw.circle(surf, spark_col, (sx, sy), 3)
                
            surface.blit(surf, (self.rect.x - 15, self.rect.y - 15))

