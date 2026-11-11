# engine/keyboard_controller.py
import pygame

class KeyboardController:
    def __init__(self, command_parser, toggle_fullscreen_callback=None):
        self.command_parser = command_parser
        self.toggle_fullscreen_callback = toggle_fullscreen_callback
        
    def process_events(self, events):
        game_state = self.command_parser.game_state
        
        for event in events:
            if event.type == pygame.KEYDOWN:
                # 1. When game is over (Victory or Defeat), literally ANY key continues!
                if game_state.game_over:
                    # Let numbers switch difficulty, any other key restarts/continues
                    if event.key == pygame.K_1:
                        game_state.set_difficulty("EASY")
                    elif event.key == pygame.K_2:
                        game_state.set_difficulty("MEDIUM")
                    elif event.key == pygame.K_3:
                        game_state.set_difficulty("HARD")
                    elif event.key == pygame.K_TAB:
                        game_state.cycle_difficulty()
                    elif event.key in [pygame.K_F11, pygame.K_f]:
                        if self.toggle_fullscreen_callback:
                            self.toggle_fullscreen_callback()
                    else:
                        game_state.restart()
                    return

                # 2. Pause / Resume (SPACE, ESC, or any attack)
                if event.key in [pygame.K_SPACE, pygame.K_ESCAPE]:
                    game_state.toggle_pause()
                    return
                elif game_state.paused:
                    game_state.toggle_pause()
                    return
                    
                # 3. Fullscreen Toggle (F11 or F)
                if event.key in [pygame.K_F11, pygame.K_f]:
                    if self.toggle_fullscreen_callback:
                        self.toggle_fullscreen_callback()
                    return
                        
                # 4. Combat actions
                if event.key == pygame.K_p:
                    self.command_parser.process_command("PUNCH")
                elif event.key == pygame.K_b:
                    self.command_parser.process_command("BLOCK")
                elif event.key == pygame.K_d:
                    self.command_parser.process_command("DODGE")
                elif event.key == pygame.K_s:
                    self.command_parser.process_command("SPECIAL")
                    
                # 5. Difficulty Level Selection
                elif event.key == pygame.K_TAB:
                    game_state.cycle_difficulty()
                elif event.key == pygame.K_1:
                    game_state.set_difficulty("EASY")
                elif event.key == pygame.K_2:
                    game_state.set_difficulty("MEDIUM")
                elif event.key == pygame.K_3:
                    game_state.set_difficulty("HARD")
                    
                # 6. Audio & Volume Controls
                elif event.key == pygame.K_m:
                    game_state.sounds.toggle_bgm()
                    state_label = "MUTED" if not game_state.sounds.bgm_playing else "UNMUTED"
                    game_state.set_banner("BGM " + state_label, "", (180, 200, 255), duration=25)
                elif event.key == pygame.K_UP:
                    game_state.sounds.adjust_volume(+0.1)
                    pct = int(game_state.sounds.sfx_volume * 100)
                    game_state.set_banner(f"VOLUME: {pct}%", "", (180, 200, 255), duration=20)
                elif event.key == pygame.K_DOWN:
                    game_state.sounds.adjust_volume(-0.1)
                    pct = int(game_state.sounds.sfx_volume * 100)
                    game_state.set_banner(f"VOLUME: {pct}%", "", (180, 200, 255), duration=20)
