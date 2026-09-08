import pygame

class KeyboardController:
    def __init__(self, command_parser):
        self.command_parser = command_parser
        
    def process_events(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:
                    self.command_parser.process_command("PUNCH")
                elif event.key == pygame.K_b:
                    self.command_parser.process_command("BLOCK")
                elif event.key == pygame.K_d:
                    self.command_parser.process_command("DODGE")
                elif event.key == pygame.K_s:
                    self.command_parser.process_command("SPECIAL")
