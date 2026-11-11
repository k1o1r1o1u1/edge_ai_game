# entities/player.py
import pygame
import time
import math
from config.settings import *

class Player:
    def __init__(self):
        self.hp = PLAYER_MAX_HP
        self.max_hp = PLAYER_MAX_HP
        self.display_hp = float(PLAYER_MAX_HP)
        self.lag_hp = float(PLAYER_MAX_HP)
        
        # Special Attack Charge System
        self.special_charge = 0.0
        self.max_charge = SPECIAL_MAX_CHARGE
        
        self.state = "IDLE"  # IDLE, PUNCH, BLOCK, DODGE, SPECIAL
        self.state_end_time = 0
        self.hit_flash_end = 0
        
        # Position and dimensions (960x600 screen)
        self.base_x = 180
        self.base_y = 300
        self.width = 90
        self.height = 160
        self.rect = pygame.Rect(self.base_x, self.base_y, self.width, self.height)
        
        self.color = COLOR_PLAYER
        self.original_color = COLOR_PLAYER
        self.anim_offset_x = 0
        self.anim_offset_y = 0

    def add_charge(self, amount):
        old_charge = self.special_charge
        self.special_charge = min(self.max_charge, self.special_charge + amount)
        return old_charge < SPECIAL_MIN_REQUIRED and self.special_charge >= SPECIAL_MIN_REQUIRED

    def can_use_special(self):
        return self.special_charge >= SPECIAL_MIN_REQUIRED

    def consume_special_charge(self):
        """Consumes the full 100% charge to release the devastating ultimate special"""
        self.special_charge = 0.0
        return DMG_SPECIAL

    def set_state(self, new_state, duration_ms):
        self.state = new_state
        self.state_end_time = time.time() * 1000 + duration_ms
        
        if new_state == "BLOCK":
            self.color = COLOR_BLOCK
            self.anim_offset_x = -8
        elif new_state == "DODGE":
            self.color = COLOR_DODGE
            self.anim_offset_x = -55
        elif new_state == "SPECIAL":
            self.color = COLOR_SPECIAL
            self.anim_offset_x = 20
        elif new_state == "PUNCH":
            self.color = (255, 255, 255)
            self.anim_offset_x = 22

    def take_damage(self, amount):
        if self.state == "DODGE":
            self.add_charge(CHARGE_PER_DODGE)
            return 0, "DODGED"
            
        actual_damage = amount
        action_note = "HIT"
        if self.state == "BLOCK":
            actual_damage = max(1, amount // 4)  # Block absorbs 75%
            self.add_charge(CHARGE_PER_PERFECT_BLOCK)
            action_note = "BLOCKED"
            
        self.hp = max(0, self.hp - actual_damage)
        if actual_damage > 0:
            self.hit_flash_end = time.time() * 1000 + DURATION_HIT_FLASH
            
        return actual_damage, action_note

    def update(self):
        current_time = time.time() * 1000
        
        # Smooth HP bar animations
        self.display_hp += (self.hp - self.display_hp) * 0.2
        if self.lag_hp > self.hp:
            self.lag_hp -= max(0.4, (self.lag_hp - self.hp) * 0.06)
        else:
            self.lag_hp = float(self.hp)

        # Revert state to IDLE if duration expired
        if self.state != "IDLE" and current_time >= self.state_end_time:
            self.state = "IDLE"
            self.color = self.original_color
            self.anim_offset_x = 0
            self.anim_offset_y = 0
            
        # Revert color if hit flash is over
        if current_time >= self.hit_flash_end and self.state == "IDLE":
            self.color = self.original_color

        # Subtle breathing idle bounce
        if self.state == "IDLE":
            self.anim_offset_y = int(math.sin(time.time() * 4.0) * 3)

        self.rect.x = self.base_x + self.anim_offset_x
        self.rect.y = self.base_y + self.anim_offset_y

    def _draw_hex_shield(self, surface):
        shield_w = 60
        shield_h = self.height + 40
        shield_x = self.rect.right + 10
        shield_y = self.rect.y - 20
        
        t = time.time()
        pulse = (math.sin(t * 12.0) + 1.0) * 0.5
        
        surf = pygame.Surface((shield_w + 30, shield_h + 20), pygame.SRCALPHA)
        
        pts = [
            (5, 10),
            (shield_w - 5, 25),
            (shield_w + 10, shield_h // 2),
            (shield_w - 5, shield_h - 15),
            (5, shield_h),
            (15, shield_h // 2)
        ]
        
        aura_alpha = int(60 + 40 * pulse)
        pygame.draw.polygon(surf, (*COLOR_BLOCK, aura_alpha), pts)
        pygame.draw.polygon(surf, (255, 240, 150, 230), pts, width=3)
        
        for cy in range(35, shield_h - 20, 30):
            center = (shield_w // 2 + 5, cy)
            r = 12
            hex_pts = []
            for i in range(6):
                angle = i * (math.pi / 3)
                hx = center[0] + r * math.cos(angle)
                hy = center[1] + r * math.sin(angle)
                hex_pts.append((hx, hy))
            pygame.draw.polygon(surf, (255, 255, 200, 160), hex_pts, width=1)
            
        surface.blit(surf, (shield_x, shield_y))

    def draw(self, surface):
        current_color = self.color
        current_time = time.time() * 1000
        
        if current_time < self.hit_flash_end:
            current_color = COLOR_HIT

        # Shadow beneath player
        shadow_rect = pygame.Rect(self.rect.centerx - 45, self.base_y + self.height - 5, 90, 16)
        shadow_surface = pygame.Surface((90, 16), pygame.SRCALPHA)
        pygame.draw.ellipse(shadow_surface, (0, 0, 0, 100), (0, 0, 90, 16))
        surface.blit(shadow_surface, shadow_rect.topleft)

        # Intense pulsing Golden Aura when Special is 100% full!
        if self.special_charge >= 100:
            pulse = math.sin(time.time() * 10.0) * 8
            aura_radius = int(self.width + 18 + pulse)
            aura_surf = pygame.Surface((aura_radius * 2, aura_radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(aura_surf, (255, 215, 0, 95), (aura_radius, aura_radius), aura_radius)
            pygame.draw.circle(aura_surf, (255, 255, 255, 120), (aura_radius, aura_radius), max(10, aura_radius - 15))
            surface.blit(aura_surf, (self.rect.centerx - aura_radius, self.rect.centery - aura_radius))

        # Draw Character Body
        pygame.draw.rect(surface, current_color, self.rect, border_radius=8)
        pygame.draw.rect(surface, (255, 255, 255, 180), self.rect, width=2, border_radius=8)
        
        # Fighter Visor
        visor_rect = pygame.Rect(self.rect.right - 28, self.rect.y + 28, 20, 10)
        pygame.draw.rect(surface, (0, 240, 255), visor_rect, border_radius=3)

        # Attack launch muzzle flair
        if self.state == "PUNCH":
            fist_muzzle = pygame.Rect(self.rect.right - 5, self.rect.centery - 16, 25, 32)
            pygame.draw.ellipse(surface, (0, 240, 255), fist_muzzle)
            pygame.draw.ellipse(surface, (255, 255, 255), (fist_muzzle.x + 4, fist_muzzle.y + 4, 16, 24))
        elif self.state == "SPECIAL":
            special_muzzle = pygame.Rect(self.rect.right - 5, self.rect.centery - 35, 50, 70)
            pygame.draw.ellipse(surface, COLOR_SPECIAL_CHARGE_FULL, special_muzzle)
            pygame.draw.ellipse(surface, (255, 255, 255), (special_muzzle.x + 8, special_muzzle.y + 8, 34, 54))
        elif self.state == "BLOCK":
            self._draw_hex_shield(surface)
        elif self.state == "DODGE":
            ghost_rect = pygame.Rect(self.rect.x + 35, self.rect.y, self.width, self.height)
            ghost_surf = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            pygame.draw.rect(ghost_surf, (*COLOR_DODGE, 80), (0, 0, self.width, self.height), border_radius=8)
            surface.blit(ghost_surf, ghost_rect.topleft)
