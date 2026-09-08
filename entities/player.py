import pygame
import time
from config.settings import *

class Player:
    def __init__(self):
        self.hp = PLAYER_MAX_HP
        self.max_hp = PLAYER_MAX_HP
        self.state = "IDLE"  # IDLE, PUNCH, BLOCK, DODGE, SPECIAL
        self.state_end_time = 0
        self.hit_flash_end = 0
        
        # Position and size
        self.rect = pygame.Rect(150, 300, 80, 150)
        self.color = COLOR_PLAYER
        self.original_color = COLOR_PLAYER
        
    def set_state(self, new_state, duration_ms):
        self.state = new_state
        self.state_end_time = time.time() * 1000 + duration_ms
        
        if new_state == "BLOCK":
            self.color = COLOR_BLOCK
        elif new_state == "DODGE":
            self.color = COLOR_DODGE
        elif new_state == "SPECIAL":
            self.color = COLOR_SPECIAL
        elif new_state == "PUNCH":
            self.color = COLOR_TEXT
            
    def take_damage(self, amount):
        if self.state == "DODGE":
            return 0  # Fully evaded
            
        actual_damage = amount
        if self.state == "BLOCK":
            actual_damage = max(0, amount // 4)  # Block blocks 75% damage
            
        self.hp -= actual_damage
        if self.hp < 0:
            self.hp = 0
            
        if actual_damage > 0:
            self.hit_flash_end = time.time() * 1000 + DURATION_HIT_FLASH
            
        return actual_damage
            
    def update(self):
        current_time = time.time() * 1000
        
        # Revert state to IDLE if duration expired
        if self.state != "IDLE" and current_time >= self.state_end_time:
            self.state = "IDLE"
            self.color = self.original_color
            
        # Revert color if hit flash is over (and not in another state)
        if current_time >= self.hit_flash_end and self.state == "IDLE":
            self.color = self.original_color
            
    def draw(self, surface):
        current_color = self.color
        current_time = time.time() * 1000
        
        # Hit flash overrides other colors
        if current_time < self.hit_flash_end:
            current_color = COLOR_HIT
            
        pygame.draw.rect(surface, current_color, self.rect)
        
        # Simple attack animation extension
        if self.state in ["PUNCH", "SPECIAL"]:
            attack_rect = pygame.Rect(self.rect.right, self.rect.centery - 20, 60, 40)
            pygame.draw.rect(surface, current_color, attack_rect)
            
        # Draw Health Bar
        bar_width = 200
        bar_height = 20
        hp_ratio = self.hp / self.max_hp
        
        pygame.draw.rect(surface, COLOR_HEALTH_BG, (50, 50, bar_width, bar_height))
        if self.hp > 0:
            pygame.draw.rect(surface, COLOR_HEALTH_FG, (50, 50, int(bar_width * hp_ratio), bar_height))
            
        # Draw state text above player
        if self.state != "IDLE":
            font = pygame.font.SysFont(None, 36)
            text = font.render(self.state, True, current_color)
            surface.blit(text, (self.rect.centerx - text.get_width()//2, self.rect.top - 40))
