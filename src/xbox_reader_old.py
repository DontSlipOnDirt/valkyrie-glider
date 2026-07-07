# Charis' computer could not run the pygame library, which is why we switched to input in the other file. This file is kept for reference in case we need to switch back to pygame in the future.
import pygame
import sys

class XboxController:
    """Reads Xbox controller input and returns normalized values"""
    
    def __init__(self):
        """Initialize pygame and detect Xbox controller"""
        pygame.init()
        pygame.joystick.init()
        
        joysticks = pygame.joystick.get_count()
        if joysticks == 0:
            raise Exception("No Xbox controller detected!")
        
        self.joystick = pygame.joystick.Joystick(0)
        self.joystick.init()
        
        print(f"✓ Controller detected: {self.joystick.get_name()}")
        print(f"  Axes: {self.joystick.get_numaxes()}")
        print(f"  Buttons: {self.joystick.get_numbuttons()}")
    
    def read_input(self):
        """
        Read current controller state.
        
        Returns:
            dict: Controller state with all axes and button states
            
        Axes mapping (Xbox controller):
        - 0: Left stick X (-1 to 1)
        - 1: Left stick Y (-1 to 1) 
        - 2: Left trigger (0 to 1)
        - 3: Right stick X (-1 to 1)
        - 4: Right stick Y (-1 to 1)
        - 5: Right trigger (0 to 1)
        """
        pygame.event.pump()  # Update the internal event queue
        
        state = {
            'left_stick_x': self.joystick.get_axis(0),
            'left_stick_y': -self.joystick.get_axis(1),  # Invert Y for intuitive control
            'left_trigger': self.joystick.get_axis(4),
            'right_stick_x': self.joystick.get_axis(2),
            'right_stick_y': -self.joystick.get_axis(3),  # Invert Y
            'right_trigger': self.joystick.get_axis(5),
            'buttons': {
                'A': self.joystick.get_button(0),
                'B': self.joystick.get_button(1),
                'X': self.joystick.get_button(2),
                'Y': self.joystick.get_button(3),
                'LB': self.joystick.get_button(4),
                'RB': self.joystick.get_button(5),
                'back': self.joystick.get_button(6),
                'start': self.joystick.get_button(7),
            }
        }
        return state
    
    def cleanup(self):
        """Clean up pygame resources"""
        pygame.quit()
        print("✓ Controller cleanup complete")


if __name__ == "__main__":
    # Test the controller
    try:
        controller = XboxController()
        print("\nReading controller input (Press Ctrl+C to stop)...\n")
        
        import time
        while True:
            state = controller.read_input()
            
            # Print only non-zero values
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

