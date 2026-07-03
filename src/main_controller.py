#!/usr/bin/env python3
"""
RC Plane Xbox Controller → Arduino Controller
Main control loop that integrates Xbox input, value mapping, and serial communication.
"""

import time
import argparse
from xbox_reader import XboxController
from value_mapper import ControlMapping
from arduino_communicator import ArduinoSerial


class RCPlaneController:
    """Integrates Xbox controller input and Arduino communication"""
    
    def __init__(self, arduino_port='COM3', baudrate=9600, 
                 use_named_format=True, loop_frequency=50):
        """
        Initialize the complete control system.
        
        Args:
            arduino_port (str): Serial port for Arduino (e.g., 'COM3')
            baudrate (int): Baudrate for serial communication
            use_named_format (bool): Use named format (P:channel:value) or simple (val1,val2,...)
            loop_frequency (int): Control loop frequency in Hz (50 is typical for RC)
        """
        print("Initializing RC Plane Controller...\n")
        
        try:
            self.xbox = XboxController()
        except Exception as e:
            print(f"✗ Failed to initialize Xbox controller: {e}")
            raise
        
        try:
            self.arduino = ArduinoSerial(port=arduino_port, baudrate=baudrate)
        except Exception as e:
            print(f"✗ Failed to initialize Arduino connection: {e}")
            self.xbox.cleanup()
            raise
        
        self.running = True
        self.use_named_format = use_named_format
        self.loop_frequency = loop_frequency
        self.loop_delay = 1.0 / loop_frequency
        
        # Define channel mappings: channel_name -> (xbox_input_name, mapper_function)
        self.control_mapping = {
            'throttle': ('right_trigger', ControlMapping.map_trigger_to_pwm),
            'pitch': ('left_stick_y', ControlMapping.map_stick_to_pwm),
            'roll': ('left_stick_x', ControlMapping.map_stick_to_pwm),
            'yaw': ('right_stick_x', ControlMapping.map_stick_to_pwm),
        }
        
        # Settings
        self.deadzone_stick = 0.15  # 15% deadzone for sticks
        self.deadzone_trigger = 0.05  # 5% deadzone for triggers
        self.curve_factor = 1.0  # No curve by default (1.0 = linear)
        
        print(f"✓ RC Plane Controller initialized")
        print(f"  - Loop frequency: {loop_frequency} Hz")
        print(f"  - Communication format: {'Named' if use_named_format else 'Simple'}")
        print(f"  - Stick deadzone: {self.deadzone_stick*100:.0f}%")
        print(f"\nPress Ctrl+C to stop\n")
    
    def set_control_mapping(self, mapping):
        """
        Override default control mapping.
        
        Args:
            mapping (dict): Custom mapping dictionary
            
        Example:
            controller.set_control_mapping({
                'throttle': ('left_trigger', ControlMapping.map_trigger_to_pwm),
                'pitch': ('right_stick_y', ControlMapping.map_stick_to_pwm),
            })
        """
        self.control_mapping = mapping
        print(f"✓ Control mapping updated")
    
    def set_deadzone(self, stick=0.15, trigger=0.05):
        """
        Set deadzone for analog inputs.
        
        Args:
            stick (float): Deadzone percentage for sticks (0.0-1.0)
            trigger (float): Deadzone percentage for triggers (0.0-1.0)
        """
        self.deadzone_stick = stick
        self.deadzone_trigger = trigger
        print(f"✓ Deadzone updated: stick={stick*100:.0f}%, trigger={trigger*100:.0f}%")
    
    def process_input(self):
        """
        Main control loop - reads input and sends to Arduino.
        Blocks until interrupted.
        """
        try:
            print(f"{'Throttle':>10} | {'Pitch':>10} | {'Roll':>10} | {'Yaw':>10}")
            print("-" * 50)
            
            while self.running:
                # Read Xbox controller
                controller_state = self.xbox.read_input()
                
                # Build PWM values
                pwm_values = {}
                for channel, (input_name, mapper) in self.control_mapping.items():
                    raw_value = controller_state[input_name]
                    
                    # Apply appropriate deadzone
                    if 'trigger' in input_name:
                        raw_value = ControlMapping.apply_deadzone(
                            raw_value, 
                            deadzone=self.deadzone_trigger
                        )
                    elif 'stick' in input_name:
                        raw_value = ControlMapping.apply_deadzone(
                            raw_value, 
                            deadzone=self.deadzone_stick
                        )
                    
                    # Apply curve if set
                    if self.curve_factor != 1.0:
                        raw_value = ControlMapping.apply_curve(
                            raw_value, 
                            curve_factor=self.curve_factor
                        )
                    
                    # Map to PWM
                    pwm_values[channel] = mapper(raw_value)
                
                # Send to Arduino
                if self.use_named_format:
                    self.arduino.send_pwm_values(pwm_values)
                else:
                    # Send in fixed order: throttle, pitch, roll, yaw
                    self.arduino.send_simple_values(
                        pwm_values['throttle'],
                        pwm_values['pitch'],
                        pwm_values['roll'],
                        pwm_values['yaw']
                    )
                
                # Print debug info (only update when values change significantly)
                self._print_status(pwm_values)
                
                # Control loop timing
                time.sleep(self.loop_delay)
        
        except KeyboardInterrupt:
            print("\n\n✓ Control interrupted by user")
            self.cleanup()
        except Exception as e:
            print(f"\n✗ Error in control loop: {e}")
            self.cleanup()
            raise
    
    def _print_status(self, pwm_values):
        """Print current control values"""
        status = (
            f"\r{pwm_values['throttle']:>10} | "
            f"{pwm_values['pitch']:>10} | "
            f"{pwm_values['roll']:>10} | "
            f"{pwm_values['yaw']:>10}"
        )
        print(status, end='', flush=True)
    
    def cleanup(self):
        """Shutdown gracefully"""
        self.running = False
        print("\nShutting down...")
        self.arduino.close()
        self.xbox.cleanup()
        print("✓ System shutdown complete")


def main():
    """Command-line entry point"""
    parser = argparse.ArgumentParser(
        description='RC Plane Xbox Controller to Arduino Bridge'
    )
    parser.add_argument(
        '--port', 
        default='COM3',
        help='Arduino serial port (default: COM3)'
    )
    parser.add_argument(
        '--baud',
        type=int,
        default=9600,
        help='Serial baud rate (default: 9600)'
    )
    parser.add_argument(
        '--simple',
        action='store_true',
        help='Use simple format (val1,val2,val3) instead of named format'
    )
    parser.add_argument(
        '--freq',
        type=int,
        default=50,
        help='Control loop frequency in Hz (default: 50)'
    )
    parser.add_argument(
        '--list-ports',
        action='store_true',
        help='List available serial ports and exit'
    )
    
    args = parser.parse_args()
    
    if args.list_ports:
        ArduinoSerial.list_ports()
        return
    
    try:
        controller = RCPlaneController(
            arduino_port='COM7', # hardcoded for testing; replace with actual
            baudrate=args.baud,
            use_named_format=not args.simple,
            loop_frequency=args.freq
        )
        controller.process_input()
    except Exception as e:
        print(f"Fatal error: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
