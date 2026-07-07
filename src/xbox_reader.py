from inputs import get_gamepad
import threading
print(">>> xbox_reader.py NEW XInput VERSION LOADED <<<")
class XboxController:
    """Reads Xbox controller input via native XInput and returns normalized values"""

    MAX_TRIG_VAL = 255
    MAX_JOY_VAL = 32767

    def __init__(self):
        """Initialize controller state and start background reader thread"""
        self._state = {
            'left_stick_x': 0.0,
            'left_stick_y': 0.0,
            'right_stick_x': 0.0,
            'right_stick_y': 0.0,
            'left_trigger': 0.0,
            'right_trigger': 0.0,
            'buttons': {
                'A': 0, 'B': 0, 'X': 0, 'Y': 0,
                'LB': 0, 'RB': 0, 'back': 0, 'start': 0,
            }
        }
        self._lock = threading.Lock()
        self._running = True

        # Quick check that a controller is actually present
        try:
            get_gamepad()
        except Exception as e:
            raise Exception(f"No Xbox controller detected! ({e})")

        self._thread = threading.Thread(target=self._update_loop, daemon=True)
        self._thread.start()

        print("✓ Controller detected (XInput)")

    def _update_loop(self):
        """Background thread: continuously reads raw XInput events into shared state"""
        while self._running:
            events = get_gamepad()
            with self._lock:
                for event in events:
                    code = event.code
                    val = event.state

                    if code == 'ABS_X':
                        self._state['left_stick_x'] = val / self.MAX_JOY_VAL
                    elif code == 'ABS_Y':
                        self._state['left_stick_y'] = -val / self.MAX_JOY_VAL  # invert for intuitive up=positive
                    elif code == 'ABS_RX':
                        self._state['right_stick_x'] = val / self.MAX_JOY_VAL
                    elif code == 'ABS_RY':
                        self._state['right_stick_y'] = -val / self.MAX_JOY_VAL
                    elif code == 'ABS_Z':
                        self._state['left_trigger'] = val / self.MAX_TRIG_VAL
                    elif code == 'ABS_RZ':
                        self._state['right_trigger'] = val / self.MAX_TRIG_VAL
                    elif code == 'BTN_SOUTH':
                        self._state['buttons']['A'] = val
                    elif code == 'BTN_EAST':
                        self._state['buttons']['B'] = val
                    elif code == 'BTN_NORTH':
                        self._state['buttons']['X'] = val
                    elif code == 'BTN_WEST':
                        self._state['buttons']['Y'] = val
                    elif code == 'BTN_TL':
                        self._state['buttons']['LB'] = val
                    elif code == 'BTN_TR':
                        self._state['buttons']['RB'] = val
                    elif code == 'BTN_SELECT':
                        self._state['buttons']['back'] = val
                    elif code == 'BTN_START':
                        self._state['buttons']['start'] = val

    def read_input(self):
        """
        Return the latest controller state as a dict (thread-safe snapshot).

        Returns:
            dict: Same shape as before — left_stick_x/y, right_stick_x/y,
                  left_trigger, right_trigger, buttons
        """
        with self._lock:
            # Return a shallow copy so callers can't mutate internal state
            return {
                'left_stick_x': self._state['left_stick_x'],
                'left_stick_y': self._state['left_stick_y'],
                'right_stick_x': self._state['right_stick_x'],
                'right_stick_y': self._state['right_stick_y'],
                'left_trigger': self._state['left_trigger'],
                'right_trigger': self._state['right_trigger'],
                'buttons': dict(self._state['buttons']),
            }

    def cleanup(self):
        """Stop the background reader thread"""
        self._running = False
        print("✓ Controller cleanup complete")


if __name__ == "__main__":
    import time
    try:
        controller = XboxController()
        print("\nReading controller input (Press Ctrl+C to stop)...\n")
        while True:
            state = controller.read_input()
            print(f"LX: {state['left_stick_x']:6.2f} | "
                  f"LY: {state['left_stick_y']:6.2f} | "
                  f"RX: {state['right_stick_x']:6.2f} | "
                  f"RY: {state['right_stick_y']:6.2f} | "
                  f"LT: {state['left_trigger']:6.2f} | "
                  f"RT: {state['right_trigger']:6.2f}",
                  end='\r')
            time.sleep(0.05)
    except KeyboardInterrupt:
        print("\n\nTest interrupted")
        controller.cleanup()
    except Exception as e:
        print(f"Error: {e}")