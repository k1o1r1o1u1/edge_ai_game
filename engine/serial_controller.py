import threading
import serial
import serial.tools.list_ports
import time
from config.settings import SERIAL_PORT, BAUD_RATE

class SerialController:
    def __init__(self, command_parser):
        self.command_parser = command_parser
        self.serial_conn = None
        self.running = False
        self.thread = None
        
    def _find_esp32_port(self):
        ports = serial.tools.list_ports.comports()
        for port in ports:
            # Common USB-to-Serial chips used in ESP32 boards
            if "CH340" in port.description or "CP210" in port.description or "UART" in port.description:
                return port.device
        # Fallback to the first available port if specific chips aren't found in description
        if ports:
            return ports[0].device
        return None

    def start(self):
        port_to_use = SERIAL_PORT
        if port_to_use == "AUTO":
            found_port = self._find_esp32_port()
            if found_port:
                print(f"Auto-detected ESP32 on port: {found_port}")
                port_to_use = found_port
            else:
                raise serial.SerialException("Could not auto-detect ESP32. Please specify the port manually in config/settings.py")

        try:
            self.serial_conn = serial.Serial(port_to_use, BAUD_RATE, timeout=1)
            self.running = True
            self.thread = threading.Thread(target=self._read_loop, daemon=True)
            self.thread.start()
        except serial.SerialException as e:
            print(f"Error opening serial port {port_to_use}: {e}")
            raise e
            
    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join(timeout=2)
        if self.serial_conn and self.serial_conn.is_open:
            self.serial_conn.close()
            
    def _read_loop(self):
        while self.running:
            try:
                if self.serial_conn and self.serial_conn.is_open:
                    if self.serial_conn.in_waiting > 0:
                        line = self.serial_conn.readline().decode('utf-8', errors='ignore').strip()
                        if line:
                            upper_line = line.upper()
                            for cmd in self.command_parser.valid_commands:
                                if cmd in upper_line:
                                    self.command_parser.process_command(cmd)
                                    break
                else:
                    time.sleep(0.1)
            except Exception as e:
                print(f"Serial read error: {e}")
                time.sleep(1)