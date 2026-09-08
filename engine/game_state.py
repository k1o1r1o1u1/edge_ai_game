import pygame
from entities.player import Player
from entities.boss import Boss
from engine.effects import EffectManager
from config.settings import *

class GameState:
    def __init__(self):
        self.player = Player()
        self.boss = Boss()
        self.effects = EffectManager()
        self.score = 0
        self.combo = 0
        self.font = pygame.font.SysFont(None, 36)
        self.title_font = pygame.font.SysFont(None, 72)
        self.game_over = False
        self.message = ""
        self.message_timer = 0
        
    def handle_command(self, command):
        if self.game_over:
            return
            
        if command == "PUNCH":
            self.player.set_state("PUNCH", COOLDOWN_ACTION)
            self.boss.take_damage(DMG_PUNCH)
            self.effects.add_particles(self.boss.rect.centerx, self.boss.rect.centery, COLOR_HIT, count=15, size=8)
            self.score += 100
            self.combo += 1
            self.set_message("PUNCH!")
            
        elif command == "SPECIAL":
            self.player.set_state("SPECIAL", COOLDOWN_ACTION * 2)
            self.boss.take_damage(DMG_SPECIAL)
            self.effects.screen_shake(duration=20, intensity=10)
            self.effects.add_particles(self.boss.rect.centerx, self.boss.rect.centery, COLOR_SPECIAL, count=40, size=15)
            self.score += 500
            self.combo += 2
            self.set_message("SPECIAL ATTACK!!!")
            
        elif command == "BLOCK":
            self.player.set_state("BLOCK", DURATION_BLOCK)
            self.effects.add_particles(self.player.rect.centerx, self.player.rect.top, COLOR_BLOCK, count=10, size=5)
            self.set_message("BLOCKING")
            
        elif command == "DODGE":
            self.player.set_state("DODGE", DURATION_DODGE)
            self.effects.add_particles(self.player.rect.centerx, self.player.rect.bottom, COLOR_DODGE, count=20, size=4)
            self.set_message("DODGED")
            
    def set_message(self, text):
        self.message = text
        self.message_timer = 60 # frames
            
    def update(self):
        if self.game_over:
            return
            
        self.player.update()
        self.effects.update()
        boss_attacked = self.boss.update()
        
        if boss_attacked:
            damage_taken = self.player.take_damage(DMG_BOSS_ATTACK)
            if damage_taken > 0:
                self.combo = 0 # reset combo if hit
                self.effects.screen_shake(duration=10, intensity=5)
                self.effects.add_particles(self.player.rect.centerx, self.player.rect.centery, COLOR_BOSS, count=20, size=8)
                
        if self.message_timer > 0:
            self.message_timer -= 1
        else:
            self.message = ""
            
        self.check_win_loss()
            
    def check_win_loss(self):
        if self.player.hp <= 0:
            self.game_over = True
            self.message = "YOU DIED"
        elif self.boss.hp <= 0:
            self.game_over = True
            self.message = "BOSS DEFEATED!"
            
    def draw(self, surface):
        surface.fill(COLOR_BG)
        
        shake_x, shake_y = self.effects.get_shake_offset()
        
        # Create a subsurface or just offset drawing
        draw_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        draw_surface.fill(COLOR_BG)
        
        self.player.draw(draw_surface)
        self.boss.draw(draw_surface)
        self.effects.draw(draw_surface)
        
        # Blit the shaken surface
        surface.blit(draw_surface, (shake_x, shake_y))
        
        # HUD remains unshaken
        score_text = self.font.render(f"Score: {self.score}", True, COLOR_TEXT)
        combo_text = self.font.render(f"Combo: x{self.combo}", True, COLOR_TEXT)
        
        surface.blit(score_text, (20, 20))
        if self.combo > 1:
            surface.blit(combo_text, (20, 50))
            
        # Message
        if self.message:
            font_to_use = self.title_font if self.game_over else self.font
            msg_text = font_to_use.render(self.message, True, COLOR_TEXT)
            surface.blit(msg_text, (SCREEN_WIDTH//2 - msg_text.get_width()//2, 100))
