import pygame
import time
import random
from config.settings import *

class Boss:
    def __init__(self):
        self.hp = BOSS_MAX_HP
        self.max_hp = BOSS_MAX_HP
        self.state = "IDLE"  # IDLE, PREPARE, ATTACK
        self.state_end_time = 0
        self.hit_flash_end = 0
        self.last_attack_time = time.time() * 1000
        
        # Position and size
        self.rect = pygame.Rect(SCREEN_WIDTH - 250, 200, 150, 250)
        self.color = COLOR_BOSS
        self.original_color = COLOR_BOSS
        
    def take_damage(self, amount):
        self.hp -= amount
        if self.hp < 0:
            self.hp = 0
            
        self.hit_flash_end = time.time() * 1000 + DURATION_HIT_FLASH
        
    def update(self):
        current_time = time.time() * 1000
        
        # Attack logic
        if self.state == "IDLE":
            if current_time - self.last_attack_time > COOLDOWN_BOSS_ATTACK:
                # Add some randomness to boss attacks (between 1x and 2x cooldown)
                if random.random() < 0.05:
                    self.state = "PREPARE"
                    self.state_end_time = current_time + 1000  # 1 second warning
                    self.color = (255, 100, 100) # Brighten to show preparation
                    
        elif self.state == "PREPARE":
            if current_time >= self.state_end_time:
                self.state = "ATTACK"
                self.state_end_time = current_time + 500 # Attack animation duration
                self.last_attack_time = current_time
                self.color = (255, 0, 0)
                return True # Signal that attack fired
                
        elif self.state == "ATTACK":
            if current_time >= self.state_end_time:
                self.state = "IDLE"
                self.color = self.original_color
                
        # Revert color if hit flash is over
        if current_time >= self.hit_flash_end and self.state == "IDLE":
            self.color = self.original_color
            
        return False
        
    def draw(self, surface):
        current_color = self.color
        current_time = time.time() * 1000
        
        # Hit flash overrides other colors
        if current_time < self.hit_flash_end:
            current_color = COLOR_HIT
            
        pygame.draw.rect(surface, current_color, self.rect)
        
        # Draw eyes (just for a bit of polish)
        pygame.draw.rect(surface, (0,0,0), (self.rect.x + 30, self.rect.y + 50, 20, 20))
        pygame.draw.rect(surface, (0,0,0), (self.rect.x + 80, self.rect.y + 50, 20, 20))
        
        if self.state == "PREPARE":
            pygame.draw.rect(surface, (255,255,0), (self.rect.x + 30, self.rect.y + 50, 20, 20))
            pygame.draw.rect(surface, (255,255,0), (self.rect.x + 80, self.rect.y + 50, 20, 20))
            font = pygame.font.SysFont(None, 48)
            text = font.render("!", True, (255, 50, 50))
            surface.blit(text, (self.rect.centerx - text.get_width()//2, self.rect.top - 40))
            
        elif self.state == "ATTACK":
            # Simple attack effect spanning from boss to player area
            attack_rect = pygame.Rect(100, self.rect.centery - 30, self.rect.left - 100, 60)
            pygame.draw.rect(surface, (255, 100, 100), attack_rect)
            
        # Draw Health Bar
        bar_width = 300
        bar_height = 20
        hp_ratio = self.hp / self.max_hp
        
        pygame.draw.rect(surface, COLOR_HEALTH_BG, (SCREEN_WIDTH - bar_width - 50, 50, bar_width, bar_height))
        if self.hp > 0:
            pygame.draw.rect(surface, COLOR_HEALTH_BOSS, (SCREEN_WIDTH - bar_width - 50, 50, int(bar_width * hp_ratio), bar_height))
