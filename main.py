import pygame
import sys
import argparse

from config.settings import *
from engine.game_state import GameState
from engine.command_parser import CommandParser
from engine.keyboard_controller import KeyboardController

def main():
    parser = argparse.ArgumentParser(description="Edge AI Fighting Game")
    parser.add_argument("--simulation", action="store_true", help="Run with keyboard controls instead of serial")
    args = parser.parse_args()

    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Edge AI Fighting Game")
    clock = pygame.time.Clock()
    
    game_state = GameState()
    command_parser = CommandParser(game_state)
    keyboard_controller = KeyboardController(command_parser)
    
    serial_controller = None
    if not args.simulation:
        try:
            from engine.serial_controller import SerialController
            serial_controller = SerialController(command_parser)
            serial_controller.start()
            print(f"Started Serial Mode on {SERIAL_PORT} at {BAUD_RATE} baud.")
        except ImportError:
            print("Serial controller not implemented yet. Running in simulation mode.")
            args.simulation = True
        except Exception as e:
            print(f"Failed to start serial: {e}")
            print("Running in simulation mode.")
            args.simulation = True
            
    if args.simulation:
        print("Running in Simulation Mode.")
        print("Controls: P=PUNCH, B=BLOCK, D=DODGE, S=SPECIAL")

    running = True
    while running:
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                running = False
                
        # Always allow keyboard controls as a fallback
        keyboard_controller.process_events(events)
        
        # Update logic
        game_state.update()
        
        # Render
        game_state.draw(screen)
        pygame.display.flip()
        
        clock.tick(FPS)
        
    if serial_controller:
        serial_controller.stop()
        
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
