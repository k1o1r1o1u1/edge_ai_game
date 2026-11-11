# main.py
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
    parser.add_argument("--fullscreen", action="store_true", help="Start directly in fullscreen mode")
    args = parser.parse_args()

    pygame.init()
    
    # Internal native rendering canvas (maintains crisp 16:10 / 960x600 layout)
    canvas = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    
    # Display window / fullscreen management
    is_fullscreen = args.fullscreen
    display_flags = pygame.FULLSCREEN if is_fullscreen else pygame.RESIZABLE
    current_size = (0, 0) if is_fullscreen else (SCREEN_WIDTH, SCREEN_HEIGHT)
    screen = pygame.display.set_mode(current_size, display_flags)
    pygame.display.set_caption("Edge AI Cyber Fighting Game")
    clock = pygame.time.Clock()

    def toggle_fullscreen():
        nonlocal is_fullscreen, screen
        is_fullscreen = not is_fullscreen
        if is_fullscreen:
            screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        else:
            screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)

    game_state = GameState()
    command_parser = CommandParser(game_state)
    keyboard_controller = KeyboardController(command_parser, toggle_fullscreen_callback=toggle_fullscreen)

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
        print("Press SPACE or ESC to Pause. Press F11 or F to toggle Fullscreen.")

    running = True
    while running:
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.VIDEORESIZE and not is_fullscreen:
                screen = pygame.display.set_mode(event.size, pygame.RESIZABLE)

        # Keyboard controls & global shortcuts
        keyboard_controller.process_events(events)

        # Update logic (handles pause internally)
        game_state.update()

        # Render to native 960x600 canvas
        game_state.draw(canvas)

        # Letterboxed / aspect-ratio preserved scaling to window/screen
        win_w, win_h = screen.get_size()
        scale = min(win_w / SCREEN_WIDTH, win_h / SCREEN_HEIGHT)
        scaled_w = int(SCREEN_WIDTH * scale)
        scaled_h = int(SCREEN_HEIGHT * scale)
        offset_x = (win_w - scaled_w) // 2
        offset_y = (win_h - scaled_h) // 2

        scaled_surface = pygame.transform.smoothscale(canvas, (scaled_w, scaled_h))
        screen.fill((10, 10, 15))  # Pillarbox / letterbox bars background
        screen.blit(scaled_surface, (offset_x, offset_y))

        pygame.display.flip()
        clock.tick(FPS)

    if serial_controller:
        serial_controller.stop()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
