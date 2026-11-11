# engine/command_parser.py
import time
from config.settings import COOLDOWN_ACTION

class CommandParser:
    def __init__(self, game_state):
        self.game_state = game_state
        self.last_action_time = 0
        self.valid_commands = ["PUNCH", "BLOCK", "DODGE", "SPECIAL"]
        
    def process_command(self, raw_command):
        # Clean and normalize
        command = raw_command.strip().upper()
        
        if command not in self.valid_commands:
            return  # Ignore IDLE or unknown commands
            
        current_time = time.time() * 1000
        
        # Check global cooldown to prevent gesture spam
        if current_time - self.last_action_time >= COOLDOWN_ACTION:
            self.game_state.handle_command(command)
            self.last_action_time = current_time
