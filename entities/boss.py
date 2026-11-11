# entities/boss.py
import pygame
import time
import random
import math
from config.settings import *

class Boss:
    def __init__(self, difficulty="MEDIUM"):
        self.difficulty = difficulty
        self.config = DIFFICULTY_SETTINGS.get(difficulty, DIFFICULTY_SETTINGS["MEDIUM"])
        
        self.hp = self.config["boss_max_hp"]
        self.max_hp = self.config["boss_max_hp"]
        self.display_hp = float(self.max_hp)
        self.lag_hp = float(self.max_hp)
        
        self.state = "IDLE"  # IDLE, PREPARE, ATTACK, RECOVER, BLOCK, DODGE
        self.attack_type = "NORMAL"  # NORMAL, HEAVY
        self.state_end_time = 0
        self.hit_flash_end = 0
        self.last_attack_time = time.time() * 1000
        
        # Position and size on 960x600 screen
        self.base_x = SCREEN_WIDTH - 280
        self.base_y = 220
        self.width = 160
        self.height = 240
        self.rect = pygame.Rect(self.base_x, self.base_y, self.width, self.height)
        
        self.color = COLOR_BOSS
        self.original_color = COLOR_BOSS
        self.anim_offset_x = 0
        self.anim_offset_y = 0

    def set_difficulty(self, difficulty):
        self.difficulty = difficulty
        self.config = DIFFICULTY_SETTINGS.get(difficulty, DIFFICULTY_SETTINGS["MEDIUM"])
        self.max_hp = self.config["boss_max_hp"]
        self.hp = self.max_hp
        self.display_hp = float(self.max_hp)
        self.lag_hp = float(self.max_hp)

    def assess_defense(self, is_special=False):
        """Called when a projectile is about to hit the boss. Boss decides whether to dodge or block!"""
        # Boss cannot defend if already attacking or recovering
        if self.state in ["PREPARE", "ATTACK", "RECOVER"]:
            return "HIT"

        # Specials are unblockable by normal shield, but boss might barely dodge on hard
        dodge_chance = self.config["boss_dodge_chance"] if not is_special else (self.config["boss_dodge_chance"] * 0.4)
        block_chance = self.config["boss_block_chance"] if not is_special else 0.0

        roll = random.random()
        if roll < dodge_chance:
            self.state = "DODGE"
            self.state_end_time = time.time() * 1000 + 600
            self.anim_offset_x = 55  # Evades backwards
            return "DODGED"
        elif roll < (dodge_chance + block_chance):
            self.state = "BLOCK"
            self.state_end_time = time.time() * 1000 + 750
            self.anim_offset_x = -15 # Braces forward
            return "BLOCKED"
        return "HIT"

    def take_damage(self, amount, defense_result="HIT"):
        actual_damage = amount
        if defense_result == "DODGED":
            return 0
        elif defense_result == "BLOCKED":
            actual_damage = max(1, amount // 4)  # Boss block mitigates 75%

        self.hp = max(0, self.hp - actual_damage)
        self.hit_flash_end = time.time() * 1000 + DURATION_HIT_FLASH
        self.anim_offset_x = 25  # Knockback visual
        return actual_damage

    def update(self):
        current_time = time.time() * 1000
        
        # Smooth HP bar animations
        self.display_hp += (self.hp - self.display_hp) * 0.2
        if self.lag_hp > self.hp:
            self.lag_hp -= max(0.5, (self.lag_hp - self.hp) * 0.05)
        else:
            self.lag_hp = float(self.hp)
            
        # Decay knockback
        self.anim_offset_x *= 0.85
        
        attack_fired = None
        
        if self.state == "IDLE":
            self.anim_offset_y = int(math.sin(time.time() * 3.0) * 5)
            # Enrage: boss attacks faster when low on health
            cooldown_mod = 0.70 if self.hp < (self.max_hp * 0.4) else 1.0
            
            if current_time - self.last_attack_time > (self.config["cooldown_boss_attack"] * cooldown_mod):
                if random.random() < self.config["heavy_chance"]:
                    self.attack_type = "HEAVY"
                    prep_duration = self.config["prep_heavy_ms"]
                else:
                    self.attack_type = "NORMAL"
                    prep_duration = self.config["prep_normal_ms"]
                    
                self.state = "PREPARE"
                self.state_end_time = current_time + prep_duration
                self.color = (255, 120, 80) if self.attack_type == "NORMAL" else (255, 50, 220)
                
        elif self.state == "PREPARE":
            self.anim_offset_x = random.randint(-4, 4)
            if current_time >= self.state_end_time:
                self.state = "ATTACK"
                self.state_end_time = current_time + 400
                self.last_attack_time = current_time
                self.color = (255, 20, 20)
                dmg = self.config["boss_dmg_heavy"] if self.attack_type == "HEAVY" else self.config["boss_dmg_normal"]
                attack_fired = {"damage": dmg, "type": self.attack_type}
                
        elif self.state == "ATTACK":
            if current_time >= self.state_end_time:
                self.state = "RECOVER"
                self.state_end_time = current_time + 450
                self.color = self.original_color
                
        elif self.state in ["RECOVER", "BLOCK", "DODGE"]:
            if current_time >= self.state_end_time:
                self.state = "IDLE"
                self.color = self.original_color
                
        if current_time >= self.hit_flash_end and self.state == "IDLE":
            self.color = self.original_color
            
        self.rect.x = int(self.base_x + self.anim_offset_x)
        self.rect.y = int(self.base_y + self.anim_offset_y)
        
        return attack_fired

    def draw(self, surface):
        current_color = self.color
        current_time = time.time() * 1000
        
        if current_time < self.hit_flash_end:
            current_color = COLOR_HIT

        # Shadow
        shadow_rect = pygame.Rect(self.rect.centerx - 70, self.base_y + self.height - 5, 140, 20)
        shadow_surface = pygame.Surface((140, 20), pygame.SRCALPHA)
        pygame.draw.ellipse(shadow_surface, (0, 0, 0, 120), (0, 0, 140, 20))
        surface.blit(shadow_surface, shadow_rect.topleft)

        # Boss Body with rounded corners & double stroke
        pygame.draw.rect(surface, current_color, self.rect, border_radius=12)
        pygame.draw.rect(surface, (255, 140, 160), self.rect, width=3, border_radius=12)
        
        # Cyber Horns
        horn_left = [(self.rect.left + 20, self.rect.top), (self.rect.left + 35, self.rect.top - 25), (self.rect.left + 50, self.rect.top)]
        horn_right = [(self.rect.right - 50, self.rect.top), (self.rect.right - 35, self.rect.top - 25), (self.rect.right - 20, self.rect.top)]
        pygame.draw.polygon(surface, (180, 20, 50), horn_left)
        pygame.draw.polygon(surface, (180, 20, 50), horn_right)

        # Boss Eyes
        eye_color = (255, 255, 0) if self.state == "PREPARE" else (20, 20, 30)
        if self.state == "ATTACK":
            eye_color = (255, 255, 255)
            
        pygame.draw.circle(surface, eye_color, (self.rect.x + 45, self.rect.y + 60), 12)
        pygame.draw.circle(surface, eye_color, (self.rect.x + 115, self.rect.y + 60), 12)
        
        # Boss Core reactor on chest
        core_color = (255, 50, 50) if self.hp > 200 else (255, 200, 0)
        pygame.draw.circle(surface, core_color, (self.rect.centerx, self.rect.centery + 15), 18)
        pygame.draw.circle(surface, (255, 255, 255), (self.rect.centerx, self.rect.centery + 15), 8)

        # Boss Defense Visuals (Block Shield / Dodge Trail)
        if self.state == "BLOCK":
            shield_surf = pygame.Surface((40, self.height + 20), pygame.SRCALPHA)
            pygame.draw.rect(shield_surf, (255, 80, 80, 190), (0, 0, 35, self.height + 20), border_radius=6)
            pygame.draw.rect(shield_surf, (255, 255, 255, 230), (0, 0, 35, self.height + 20), width=2, border_radius=6)
            surface.blit(shield_surf, (self.rect.left - 42, self.rect.y - 10))
        elif self.state == "DODGE":
            ghost_surf = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            pygame.draw.rect(ghost_surf, (255, 60, 90, 80), (0, 0, self.width, self.height), border_radius=12)
            surface.blit(ghost_surf, (self.rect.left - 45, self.rect.y))

        # Attack VFX
        if self.state == "ATTACK":
            strike_color = (255, 50, 50) if self.attack_type == "NORMAL" else (255, 80, 250)
            attack_rect = pygame.Rect(180, self.rect.centery - 25, self.rect.left - 180, 65)
            laser_surf = pygame.Surface((attack_rect.width, attack_rect.height), pygame.SRCALPHA)
            laser_surf.fill((*strike_color, 210))
            pygame.draw.rect(laser_surf, (255, 255, 255, 240), (0, 18, attack_rect.width, 28))
            surface.blit(laser_surf, attack_rect.topleft)
            
        elif self.state == "PREPARE":
            pulse = int((time.time() * 20) % 15)
            pygame.draw.circle(surface, (255, 220, 0), (self.rect.centerx, self.rect.top - 30), 20 + pulse, width=2)
