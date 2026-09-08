# Edge AI Motion-Controlled Fighting Game

This is the Day 3 demonstration game for the Edge AI Workshop. It connects with an ESP32 over USB Serial to receive motion predictions from a TinyML model and uses them to control a 2D fighting game.

## 1. What the game does
The game provides visual feedback for motion predictions. You play against a boss character. 
Commands control the player:
- **PUNCH**: Deals damage.
- **BLOCK**: Reduces incoming damage from boss attacks.
- **DODGE**: Evades incoming boss attacks.
- **SPECIAL**: Deals massive damage (This is the student challenge!).

## 2. How to install dependencies
Make sure you have Python installed, then run:
```bash
pip install -r requirements.txt
```

## 3. How to run the game (with ESP32 connected)
Ensure the ESP32 is plugged in and printing predictions to serial. Edit `config/settings.py` to match your COM port and baud rate if needed.
```bash
python main.py
```

## 4. How to run simulation mode
To test the game without an ESP32 connected, use simulation mode which enables keyboard controls:
```bash
python main.py --simulation
```
**Controls**: 
- `P` = PUNCH
- `B` = BLOCK
- `D` = DODGE
- `S` = SPECIAL

## 5. How to connect an ESP32
1. Flash the ESP32 with the inference firmware.
2. Plug the ESP32 into your laptop via a data-capable USB cable.
3. Identify the COM port (e.g., `COM3` on Windows, `/dev/ttyUSB0` on Linux/Mac).

## 6. How to configure the serial port
Open `config/settings.py` and modify these variables:
```python
SERIAL_PORT = "AUTO"  # Will automatically find the connected ESP32
BAUD_RATE = 115200
```
If auto-detect fails, you can manually enter the port (e.g., `SERIAL_PORT = "COM3"`).

## 7. What commands the game expects
The game listens to the serial port for lines containing any of the following keywords:
- `PUNCH`
- `BLOCK`
- `DODGE`
- `SPECIAL`
- `IDLE`

For example, if your ESP32 prints `Motion: PUNCH | Confidence: 94%`, the game will extract `PUNCH` and trigger the action.

## 8. How each command affects gameplay
- **PUNCH**: Deals standard damage (10) and increases combo score.
- **BLOCK**: Changes player color to yellow and mitigates 75% of incoming boss damage for 1 second.
- **DODGE**: Changes player color to cyan and fully evades incoming damage for 0.8 seconds.
- **SPECIAL**: Deals huge damage (50) and increases combo score by 2.
- **IDLE**: Reverts to default state, doing nothing.

## 9. How to troubleshoot serial communication
- **"Failed to start serial"**: Check if the `SERIAL_PORT` in `config/settings.py` matches your device, or if "AUTO" is failing, specify the port manually. Make sure no other program (like the Arduino Serial Monitor) is using the port.
- **Game ignores commands**: Ensure the ESP32 is sending the exact keywords (`PUNCH`, `BLOCK`, etc.) and that they are separated by newlines. The game filters out repeated rapid inputs using a cooldown system.

## 10. How to test the game without hardware
Run `python run_game.py` or `python main.py --simulation`. The game is fully functional and can be tested from start to finish using the keyboard.

## 11. Creating a Standalone Executable
If you want to package the game as a single standalone executable (e.g., `.exe`) for easy distribution on student laptops, use PyInstaller:
```bash
pyinstaller --onefile --noconsole --name "EdgeAIGame" main.py
```
The executable will be generated in the `dist/` folder.

---

## Integration Document

**ESP32 TinyML Pipeline**:
1. Human Movement
2. MPU6050 (Sensors)
3. ESP32 Sampling (Fixed time window)
4. Preprocessing & TinyML Model
5. Motion Prediction (e.g., PUNCH)
6. USB Serial (e.g., `Serial.println("PUNCH")`)
7. Game Command Parser (Filters spam and applies cooldowns)
8. Game Action (Visual update and health reduction)
