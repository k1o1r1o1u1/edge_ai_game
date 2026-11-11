# engine/game_state.py
import pygame
import time
import math
from entities.player import Player
from entities.boss import Boss
from entities.projectile import EnergyProjectile
from engine.effects import EffectManager
from engine.sound_effects import SoundManager
from config.settings import *

class GameState:
    def __init__(self):
        self.difficulty = DEFAULT_DIFFICULTY  # "EASY", "MEDIUM", "HARD"
        self.player = Player()
        self.boss = Boss(self.difficulty)
        self.effects = EffectManager()
        self.sounds = SoundManager()
        self.projectiles = []
        
        self.score = 0
        self.combo = 0
        self.highest_combo = 0
        self.game_over = False
        self.victory = False
        self.paused = False
        self.sound_played_gameover = False
        
        self.sounds.start_bgm()
        
        # Action banners / notifications
        self.banner_text = ""
        self.banner_subtext = ""
        self.banner_timer = 0
        self.banner_color = COLOR_TEXT
        
        # Load fonts safely
        pygame.font.init()
        self.font_small = pygame.font.SysFont("consolas, menlo, monaco, courier", 18, bold=True)
        self.font_main = pygame.font.SysFont("arial, trebuchetms, helvetica", 24, bold=True)
        self.font_large = pygame.font.SysFont("impact, arial black, sans-serif", 40)
        self.font_huge = pygame.font.SysFont("impact, arial black, sans-serif", 68)

    def toggle_pause(self):
        if self.game_over:
            return
        self.paused = not self.paused
        if self.paused:
            self.sounds.stop_bgm()
        else:
            self.sounds.start_bgm()

    def set_difficulty(self, diff):
        if diff in DIFFICULTY_SETTINGS and self.difficulty != diff:
            self.difficulty = diff
            self.restart()
            diff_color = DIFFICULTY_SETTINGS[diff]["color"]
            self.set_banner(f"DIFFICULTY: {diff}", "Boss HP, speed & defense adjusted", diff_color, duration=45)

    def cycle_difficulty(self):
        diffs = ["EASY", "MEDIUM", "HARD"]
        cur_idx = diffs.index(self.difficulty)
        next_diff = diffs[(cur_idx + 1) % len(diffs)]
        self.set_difficulty(next_diff)

    def restart(self):
        self.player = Player()
        self.boss = Boss(self.difficulty)
        self.effects = EffectManager()
        self.projectiles = []
        self.score = 0
        self.combo = 0
        self.highest_combo = 0
        self.game_over = False
        self.victory = False
        self.paused = False
        self.sound_played_gameover = False
        self.sounds.start_bgm()
        diff_color = DIFFICULTY_SETTINGS[self.difficulty]["color"]
        self.set_banner("ROUND 1", f"DIFFICULTY: {self.difficulty}", diff_color, duration=40)

    def set_banner(self, text, subtext="", color=COLOR_TEXT, duration=45):
        self.banner_text = text
        self.banner_subtext = subtext
        self.banner_color = color
        self.banner_timer = duration

    def handle_command(self, command):
        if self.game_over:
            self.restart()
            return
            
        if self.paused:
            self.paused = False
            self.sounds.start_bgm()
            return
            
        if command == "PUNCH":
            self.player.set_state("PUNCH", COOLDOWN_ACTION)
            self.sounds.play("punch_launch")
            
            proj_y = self.player.rect.centery - 4
            target_x = self.boss.rect.left + 20
            self.projectiles.append(EnergyProjectile(self.player.rect.right, proj_y, target_x, DMG_PUNCH, "PUNCH"))
            self.effects.add_particles(self.player.rect.right, proj_y, (0, 240, 255), count=10, size=5, shape="spark")
            
        elif command == "SPECIAL":
            if not self.player.can_use_special():
                need_charge = int(100 - self.player.special_charge)
                self.set_banner("REQUIRES 100% CHARGE!", f"Need {need_charge}% more meter", (255, 100, 100), duration=25)
                self.effects.add_floating_text(self.player.rect.centerx, self.player.rect.top - 20, f"{int(self.player.special_charge)}% / 100%", (255, 120, 120), self.font_main)
                return

            damage = self.player.consume_special_charge()
            self.player.set_state("SPECIAL", COOLDOWN_ACTION * 2)
            self.sounds.play("special_launch")
            
            proj_y = self.player.rect.centery
            target_x = self.boss.rect.left + 20
            self.projectiles.append(EnergyProjectile(self.player.rect.right, proj_y, target_x, damage, "SPECIAL", is_max=True))
            
            self.set_banner("MAX SUPER BLAST UNLEASHED!", "120 CATASTROPHIC DAMAGE!", COLOR_SPECIAL_CHARGE_FULL, duration=45)
            self.effects.add_particles(self.player.rect.right, proj_y, COLOR_SPECIAL_CHARGE_FULL, count=30, size=9)

        elif command == "BLOCK":
            self.player.set_state("BLOCK", DURATION_BLOCK)
            self.sounds.play("shield_up")
            self.effects.add_particles(self.player.rect.right + 25, self.player.rect.centery, COLOR_BLOCK, count=16, size=6)
            self.set_banner("ENERGY SHIELD UP", "Blocks 75% Damage & Charges Meter", COLOR_BLOCK, duration=25)
            
        elif command == "DODGE":
            self.player.set_state("DODGE", DURATION_DODGE)
            self.sounds.play("dodge")
            self.effects.add_particles(self.player.rect.centerx, self.player.rect.centery, COLOR_DODGE, count=14, size=5)
            self.set_banner("EVASIVE SLIP", "Invulnerable + Charges Meter", COLOR_DODGE, duration=25)

    def _on_projectile_impact(self, proj):
        # Boss assesses defense (can dodge or block)
        is_special = (proj.proj_type == "SPECIAL")
        defense_result = self.boss.assess_defense(is_special=is_special)
        actual_dmg = self.boss.take_damage(proj.damage, defense_result=defense_result)
        
        if defense_result == "DODGED":
            self.sounds.play("dodge")
            self.effects.add_floating_text(self.boss.rect.centerx, self.boss.rect.top - 30, "BOSS EVADED!", COLOR_DODGE, self.font_main)
            self.set_banner("BOSS DODGED!", "No damage dealt", COLOR_DODGE, duration=25)
            return
            
        elif defense_result == "BLOCKED":
            self.sounds.play("shield_absorb")
            self.effects.screen_shake(duration=8, intensity=4)
            self.effects.add_particles(self.boss.rect.left, proj.y, (255, 100, 100), count=18, size=6, shape="spark")
            self.effects.add_floating_text(self.boss.rect.left, proj.y - 30, f"BLOCKED! (-{actual_dmg})", (255, 120, 120), self.font_main)
            self.set_banner("BOSS BLOCKED!", f"Damage mitigated to {actual_dmg}", (255, 120, 120), duration=25)
            
            # Successful connecting punch charges special meter
            charged_up = self.player.add_charge(CHARGE_PER_PUNCH // 2)
            if charged_up:
                self.sounds.play("special_ready")
                self.set_banner("100% SPECIAL READY!", "PRESS 'S' TO UNLEASH", COLOR_SPECIAL_CHARGE_FULL, duration=45)
            return

        # Direct Hit!
        if proj.proj_type == "PUNCH":
            self.sounds.play("punch_impact")
            self.effects.screen_shake(duration=10, intensity=5)
            self.effects.add_particles(self.boss.rect.left + 30, proj.y, COLOR_HIT, count=18, size=6, shape="spark")
            self.effects.add_floating_text(self.boss.rect.left + 20, proj.y - 30, f"-{actual_dmg}", (255, 255, 255), self.font_large)
            
            charged_up = self.player.add_charge(CHARGE_PER_PUNCH)
            if charged_up:
                self.sounds.play("special_ready")
                self.set_banner("100% SPECIAL READY!", "PRESS 'S' TO UNLEASH", COLOR_SPECIAL_CHARGE_FULL, duration=45)
                
            self.combo += 1
            self.highest_combo = max(self.highest_combo, self.combo)
            combo_mult = min(5, 1 + self.combo // 3)
            self.score += 100 * combo_mult
            
        else: # SPECIAL
            self.sounds.play("special_impact")
            self.effects.screen_shake(duration=28, intensity=18)
            self.effects.trigger_flash(color=(255, 230, 100), alpha=200)
            self.effects.add_particles(self.boss.rect.centerx, self.boss.rect.centery, COLOR_SPECIAL_CHARGE_FULL, count=60, size=15, shape="spark")
            self.effects.add_floating_text(self.boss.rect.centerx, self.boss.rect.top - 40, f"ULTIMATE {actual_dmg}!!", COLOR_SPECIAL_CHARGE_FULL, self.font_huge)
            
            self.combo += 3
            self.highest_combo = max(self.highest_combo, self.combo)
            self.score += 500 + actual_dmg * 15

    def update(self):
        if self.paused or self.game_over:
            return
            
        self.player.update()
        attack_info = self.boss.update()
        self.effects.update()
        
        # Update energy projectiles
        for proj in self.projectiles[:]:
            impacted = proj.update()
            if impacted:
                self._on_projectile_impact(proj)
                self.projectiles.remove(proj)
            elif not proj.alive or proj.x > SCREEN_WIDTH:
                self.projectiles.remove(proj)
        
        # Check boss telegraph sound
        if self.boss.state == "PREPARE" and not hasattr(self, "_played_telegraph"):
            self.sounds.play("boss_telegraph")
            self._played_telegraph = True
        elif self.boss.state != "PREPARE" and hasattr(self, "_played_telegraph"):
            del self._played_telegraph

        # Process boss attack hitting player
        if attack_info:
            damage_taken, action_result = self.player.take_damage(attack_info["damage"])
            if action_result == "DODGED":
                self.sounds.play("dodge")
                self.effects.add_floating_text(self.player.rect.centerx, self.player.rect.top - 30, "EVADED! +25% CHARGE", COLOR_DODGE, self.font_main)
                self.set_banner("CLEAN EVASION!", "+25% Charge Gained", COLOR_DODGE, duration=30)
                if self.player.special_charge >= 100:
                    self.sounds.play("special_ready")
            elif action_result == "BLOCKED":
                self.sounds.play("shield_absorb")
                self.effects.screen_shake(duration=10, intensity=5)
                self.effects.add_particles(self.player.rect.right + 25, self.player.rect.centery, COLOR_BLOCK, count=24, size=7, shape="spark")
                self.effects.add_floating_text(self.player.rect.centerx, self.player.rect.top - 30, f"SHIELD ABSORB! (-{damage_taken})", COLOR_BLOCK, self.font_main)
                self.set_banner("SHIELD ABSORB!", f"Damage mitigated to {damage_taken}", COLOR_BLOCK, duration=30)
                if self.player.special_charge >= 100:
                    self.sounds.play("special_ready")
            else:
                self.combo = 0
                self.sounds.play("boss_hit")
                self.effects.screen_shake(duration=16, intensity=10)
                self.effects.trigger_flash(color=(255, 40, 40), alpha=140)
                self.effects.add_particles(self.player.rect.centerx, self.player.rect.centery, COLOR_BOSS, count=25, size=8)
                self.effects.add_floating_text(self.player.rect.centerx, self.player.rect.top - 30, f"-{damage_taken}", (255, 60, 60), self.font_large)

        if self.banner_timer > 0:
            self.banner_timer -= 1
            
        self.check_win_loss()

    def check_win_loss(self):
        if self.game_over:
            return
            
        if self.player.hp <= 0:
            self.game_over = True
            self.victory = False
            self.sounds.stop_bgm()
            if not self.sound_played_gameover:
                self.sounds.play("defeat")
                self.sound_played_gameover = True
        elif self.boss.hp <= 0:
            self.game_over = True
            self.victory = True
            self.sounds.stop_bgm()
            if not self.sound_played_gameover:
                self.sounds.play("victory")
                self.sound_played_gameover = True

    def draw(self, surface):
        self._draw_arena(surface)
        
        shake_x, shake_y = self.effects.get_shake_offset() if not self.paused else (0, 0)
        entity_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        
        self.player.draw(entity_surface)
        self.boss.draw(entity_surface)
        
        for proj in self.projectiles:
            proj.draw(entity_surface)
            
        self.effects.draw(entity_surface)
        
        surface.blit(entity_surface, (shake_x, shake_y))
        
        self._draw_hud(surface)
        self._draw_banners(surface)
        
        if self.paused:
            self._draw_pause(surface)
        elif self.game_over:
            self._draw_game_over(surface)

    def _draw_arena(self, surface):
        surface.fill(COLOR_BG_DARK)
        
        for y in range(0, 420, 20):
            factor = y / 420.0
            col = (
                int(COLOR_BG_DARK[0] * (1 - factor) + COLOR_BG_GRADIENT[0] * factor),
                int(COLOR_BG_DARK[1] * (1 - factor) + COLOR_BG_GRADIENT[1] * factor),
                int(COLOR_BG_DARK[2] * (1 - factor) + COLOR_BG_GRADIENT[2] * factor)
            )
            pygame.draw.rect(surface, col, (0, y, SCREEN_WIDTH, 20))
            
        floor_rect = pygame.Rect(0, 430, SCREEN_WIDTH, SCREEN_HEIGHT - 430)
        pygame.draw.rect(surface, COLOR_ARENA_FLOOR, floor_rect)
        pygame.draw.line(surface, COLOR_ARENA_LINE, (0, 430), (SCREEN_WIDTH, 430), 3)
        
        for x in range(0, SCREEN_WIDTH + 80, 80):
            start_x = x
            end_x = int(x + (x - SCREEN_WIDTH // 2) * 0.4)
            pygame.draw.line(surface, (35, 45, 75), (start_x, 430), (end_x, SCREEN_HEIGHT), 1)

    def _draw_hud(self, surface):
        bar_w = 320
        bar_h = 24
        
        # --- PLAYER HUD (Top Left) ---
        p_tag = self.font_main.render("PLAYER 1", True, COLOR_TEXT)
        surface.blit(p_tag, (40, 20))
        
        p_bar_rect = pygame.Rect(40, 52, bar_w, bar_h)
        pygame.draw.rect(surface, COLOR_HEALTH_BG, p_bar_rect, border_radius=4)
        
        lag_w = int(bar_w * (self.player.lag_hp / self.player.max_hp))
        pygame.draw.rect(surface, COLOR_HEALTH_DAMAGE_LAG, (40, 52, lag_w, bar_h), border_radius=4)
        
        hp_w = int(bar_w * (self.player.display_hp / self.player.max_hp))
        if hp_w > 0:
            pygame.draw.rect(surface, COLOR_HEALTH_PLAYER, (40, 52, hp_w, bar_h), border_radius=4)
        pygame.draw.rect(surface, COLOR_HEALTH_BORDER, p_bar_rect, width=2, border_radius=4)
        
        p_hp_str = f"{int(self.player.hp)} / {self.player.max_hp}"
        p_hp_txt = self.font_small.render(p_hp_str, True, (255, 255, 255))
        surface.blit(p_hp_txt, (50, 55))
        
        # --- SPECIAL CHARGE METER (100% full required) ---
        special_bar_w = 260
        special_bar_h = 14
        s_rect = pygame.Rect(40, 82, special_bar_w, special_bar_h)
        pygame.draw.rect(surface, COLOR_SPECIAL_BAR_BG, s_rect, border_radius=3)
        
        charge_pct = self.player.special_charge / 100.0
        cur_charge_w = int(special_bar_w * charge_pct)
        
        if charge_pct >= 1.0:
            pulse = (math.sin(time.time() * 12.0) + 1) * 0.5
            s_color = (int(220 + 35 * pulse), int(180 + 75 * pulse), int(20 + 50 * pulse))
            charge_status = "ULTIMATE READY (100%)!"
        else:
            s_color = COLOR_SPECIAL_CHARGE_LOW
            charge_status = f"{int(self.player.special_charge)}% / 100%"
            
        if cur_charge_w > 0:
            pygame.draw.rect(surface, s_color, (40, 82, cur_charge_w, special_bar_h), border_radius=3)
        pygame.draw.rect(surface, (100, 100, 150), s_rect, width=1, border_radius=3)
        
        s_label = self.font_small.render(f"SPECIAL: {charge_status}", True, s_color)
        surface.blit(s_label, (40, 100))

        # --- BOSS HUD (Top Right) ---
        b_x = SCREEN_WIDTH - 40 - bar_w
        b_tag = self.font_main.render("CYBER OVERLORD", True, COLOR_BOSS)
        surface.blit(b_tag, (SCREEN_WIDTH - 40 - b_tag.get_width(), 20))
        
        b_bar_rect = pygame.Rect(b_x, 52, bar_w, bar_h)
        pygame.draw.rect(surface, COLOR_HEALTH_BG, b_bar_rect, border_radius=4)
        
        b_lag_w = int(bar_w * (self.boss.lag_hp / self.boss.max_hp))
        pygame.draw.rect(surface, COLOR_HEALTH_DAMAGE_LAG, (b_x + bar_w - b_lag_w, 52, b_lag_w, bar_h), border_radius=4)
        
        b_hp_w = int(bar_w * (self.boss.display_hp / self.boss.max_hp))
        if b_hp_w > 0:
            pygame.draw.rect(surface, COLOR_HEALTH_BOSS, (b_x + bar_w - b_hp_w, 52, b_hp_w, bar_h), border_radius=4)
        pygame.draw.rect(surface, COLOR_HEALTH_BORDER, b_bar_rect, width=2, border_radius=4)
        
        b_hp_str = f"{int(self.boss.hp)} / {self.boss.max_hp}"
        b_hp_txt = self.font_small.render(b_hp_str, True, (255, 255, 255))
        surface.blit(b_hp_txt, (SCREEN_WIDTH - 50 - b_hp_txt.get_width(), 55))
        
        diff_col = DIFFICULTY_SETTINGS[self.difficulty]["color"]
        diff_badge = self.font_small.render(f"[{self.difficulty} MODE]", True, diff_col)
        surface.blit(diff_badge, (SCREEN_WIDTH - 40 - bar_w, 24))
        
        if self.boss.state == "PREPARE":
            pulse_warn = (math.sin(time.time() * 15.0) + 1) * 0.5
            warn_col = (255, int(150 * pulse_warn), 0)
            warn_txt = self.font_small.render(f"WARNING: {self.boss.attack_type} ATTACK INCOMING!", True, warn_col)
            surface.blit(warn_txt, (SCREEN_WIDTH - 40 - warn_txt.get_width(), 82))

        # --- CENTER TOP: SCORE & COMBO ---
        score_val = self.font_large.render(f"{self.score:06d}", True, COLOR_TEXT)
        surface.blit(score_val, (SCREEN_WIDTH // 2 - score_val.get_width() // 2, 25))
        
        if self.combo > 1:
            combo_str = f"{self.combo} COMBO!"
            combo_col = COLOR_SPECIAL_CHARGE_FULL if self.combo >= 5 else COLOR_ACCENT
            combo_txt = self.font_main.render(combo_str, True, combo_col)
            surface.blit(combo_txt, (SCREEN_WIDTH // 2 - combo_txt.get_width() // 2, 70))

        # --- BOTTOM BAR: FULL CONTROLS & SHORTCUTS (Two distinct rows) ---
        combat_str = "[P] PUNCH   [B] SHIELD   [D] DODGE   [S] SPECIAL (100% Full Req)"
        combat_txt = self.font_small.render(combat_str, True, (230, 240, 255))
        surface.blit(combat_txt, (SCREEN_WIDTH // 2 - combat_txt.get_width() // 2, SCREEN_HEIGHT - 48))

        system_str = "[TAB/1,2,3] DIFFICULTY   |   [SPACE/ESC] PAUSE   |   [F11] FULLSCREEN   |   [M] BGM   [UP/DN] VOL"
        system_txt = self.font_small.render(system_str, True, (130, 145, 175))
        surface.blit(system_txt, (SCREEN_WIDTH // 2 - system_txt.get_width() // 2, SCREEN_HEIGHT - 24))

    def _draw_pause(self, surface):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((10, 12, 22, 190))
        surface.blit(overlay, (0, 0))
        
        pause_txt = self.font_huge.render("GAME PAUSED", True, COLOR_TEXT)
        surface.blit(pause_txt, (SCREEN_WIDTH // 2 - pause_txt.get_width() // 2, 200))
        
        pulse = (math.sin(time.time() * 5.0) + 1) * 0.5
        sub_col = (int(180 + 75 * pulse), int(220 + 35 * pulse), 255)
        resume_txt = self.font_main.render("Press SPACE, ESC, or Any Attack to Resume", True, sub_col)
        surface.blit(resume_txt, (SCREEN_WIDTH // 2 - resume_txt.get_width() // 2, 280))
        
        help_card = [
            f"Current Difficulty: {self.difficulty}  (Press 1=Easy, 2=Medium, 3=Hard)",
            "Press [F11] or [F] to Toggle Fullscreen",
            "Press [M] to Mute/Unmute BGM   |   Press [UP/DOWN] for Volume"
        ]
        for idx, line in enumerate(help_card):
            card_txt = self.font_small.render(line, True, COLOR_TEXT_DIM)
            surface.blit(card_txt, (SCREEN_WIDTH // 2 - card_txt.get_width() // 2, 340 + idx * 28))

    def _draw_banners(self, surface):
        if self.banner_timer > 0 and self.banner_text and not self.game_over:
            banner_surf = pygame.Surface((SCREEN_WIDTH, 70), pygame.SRCALPHA)
            banner_surf.fill((0, 0, 0, 130))
            surface.blit(banner_surf, (0, 135))
            
            title = self.font_large.render(self.banner_text, True, self.banner_color)
            surface.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 140))
            if self.banner_subtext:
                sub = self.font_small.render(self.banner_subtext, True, COLOR_TEXT)
                surface.blit(sub, (SCREEN_WIDTH // 2 - sub.get_width() // 2, 178))

    def _draw_game_over(self, surface):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((10, 10, 20, 210))
        surface.blit(overlay, (0, 0))
        
        if self.victory:
            res_txt = self.font_huge.render("VICTORY!", True, COLOR_SPECIAL_CHARGE_FULL)
            desc_txt = self.font_main.render(f"CYBER OVERLORD WAS CRUSHED ON {self.difficulty} MODE!", True, COLOR_TEXT)
        else:
            res_txt = self.font_huge.render("DEFEAT", True, COLOR_BOSS)
            desc_txt = self.font_main.render("SYSTEM CRITICAL. YOU WERE OVERWHELMED.", True, COLOR_TEXT)
            
        surface.blit(res_txt, (SCREEN_WIDTH // 2 - res_txt.get_width() // 2, 170))
        surface.blit(desc_txt, (SCREEN_WIDTH // 2 - desc_txt.get_width() // 2, 255))
        
        stats_score = self.font_main.render(f"FINAL SCORE: {self.score}   |   HIGHEST COMBO: x{self.highest_combo}", True, COLOR_ACCENT)
        surface.blit(stats_score, (SCREEN_WIDTH // 2 - stats_score.get_width() // 2, 310))
        
        pulse = (math.sin(time.time() * 6.0) + 1) * 0.5
        prompt_col = (int(200 + 55 * pulse), int(200 + 55 * pulse), int(200 + 55 * pulse))
        prompt_txt = self.font_large.render("PRESS ANY KEY TO CONTINUE", True, prompt_col)
        surface.blit(prompt_txt, (SCREEN_WIDTH // 2 - prompt_txt.get_width() // 2, 380))
        
        diff_prompt = self.font_small.render(f"Change Difficulty: Press [1] Easy, [2] Medium, [3] Hard", True, (160, 180, 210))
        surface.blit(diff_prompt, (SCREEN_WIDTH // 2 - diff_prompt.get_width() // 2, 440))
