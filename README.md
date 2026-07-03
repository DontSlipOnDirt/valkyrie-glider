# Xbox to Arduino RC Plane Control System

A complete Python + Arduino solution for controlling an RC plane using an Xbox controller.

## Quick Start (5 minutes)

### 1. Configure Python env
Create Virtual Environment (I personally like to use [UV](https://docs.astral.sh/uv/), but you could use the native one as well).

To create a virtual environment in your project directory, run:
```bash
python -m venv .venv
```
To activate it, use the appropriate command for your operating system and shell:

- macOS/Linux (bash/zsh): `source .venv/bin/activate` \
- Windows (cmd): `.venv\Scripts\activate.bat` \
- Windows (PowerShell): `.venv\Scripts\Activate.ps1` 

After activating, install the required packages:
```bash
pip install -r requirements.txt
```

### 2. Upload Arduino Code to Transmitter/Receiver
1. Open Arduino IDE
2. Open `tx_code.ino`
3. Select your board type and COM port
4. Click Upload
5. Note the COM port (e.g., COM3, COM4)
6. Repeat for `rx_code.ino`

### 3. Find Your Arduino's COM Port
```bash
python arduino_communicator.py
```
Look for your Transmitter Arduino in the output (usually CH340 USB device)

### 4. Update Port in Code
Edit one of the last lines of `main_controller.py`:
```python
controller = RCPlaneController(arduino_port='COM3', ...)  # Change COM3 to your port
```

### 5. Test Xbox Controller
```bash
python xbox_reader.py
```
Move sticks and pull triggers. You should see values update.

### 6. Test Value Mapping
```bash
python value_mapper.py
```
Verify that input ranges are mapping correctly to 0-255.

### 7. Run Full System
Connect your Xbox controller and Arduino, then:
```bash
python main_controller.py
```

You should see throttle/pitch/roll/yaw values updating in real-time!

---

## File Structure

| File | Purpose |
|------|---------|
| `xbox_reader.py` | Xbox controller input reading |
| `value_mapper.py` | Converts analog input to 0-255 PWM |
| `arduino_communicator.py` | Serial communication with Arduino |
| `main_controller.py` | Main control loop (run this!) |
| `tx_code.ino`,`rx_code.ino` | Arduino firmware (upload to board) |
| `XBOX_TO_ARDUINO_GUIDE.md` | Detailed step-by-step guide |

---

## Common Issues

### Xbox Controller Not Detected
```bash
# Install Xbox drivers from Microsoft
# Or try different USB port
```

### Arduino COM Port Not Found
```bash
# Check Device Manager (Windows)
# Or install CH340 drivers if using Arduino clone
python -c "from arduino_communicator import ArduinoSerial; ArduinoSerial.list_ports()"
```

### Values Not Mapped Correctly
- Check deadzone settings in `main_controller.py`
- Verify calibration in Windows Settings > Devices > Xbox

---

## Customization

### Change Control Mapping
Edit `main_controller.py`:
```python
controller.set_control_mapping({
    'throttle': ('left_trigger', ControlMapping.map_trigger_to_pwm),
    'pitch': ('right_stick_y', ControlMapping.map_stick_to_pwm),
    'roll': ('right_stick_x', ControlMapping.map_stick_to_pwm),
    'yaw': ('left_stick_x', ControlMapping.map_stick_to_pwm),
})
```

### Adjust Deadzone
```python
controller.set_deadzone(stick=0.20, trigger=0.05)  # 20% and 5%
```

### Change Loop Frequency
```bash
python main_controller.py --freq 100  # 100 Hz instead of 50 Hz
```

---

## Advanced Usage

### Using Simple Format (instead of Named)
```bash
python main_controller.py --simple
```

### Custom Arduino Port
```bash
python main_controller.py --port COM5 --baud 115200
```

### List Available Ports
```bash
python main_controller.py --list-ports
```

---

## For More Details
See `XBOX_TO_ARDUINO_GUIDE.md` for comprehensive documentation.

---

## Hardware Requirements
- Xbox controller (wired or wireless adapter)
- Arduino board (Uno, Nano, Mega, etc.)
- USB cable for Arduino
- Servo motors or ESC for RC plane

---

Good luck with your Valkyrie Plane! 🚀
