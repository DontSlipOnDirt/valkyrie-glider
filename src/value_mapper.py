class ControlMapping:
    """Converts Xbox controller analog input to Arduino PWM values (0-255)"""
    
    @staticmethod
    def map_stick_to_pwm(axis_value):
        """
        Maps analog stick value (-1.0 to 1.0) to PWM (0-255).
        
        Typical RC plane mapping:
        - -1.0 → 0 (full backward/left)
        - 0.0 → 127-128 (center/neutral)
        - 1.0 → 255 (full forward/right)
        
        Args:
            axis_value (float): Input from -1.0 to 1.0
            
        Returns:
            int: PWM value from 0 to 255
        """
        # Clamp value to valid range
        axis_value = max(-1.0, min(1.0, axis_value))
        
        # Convert from [-1, 1] to [0, 255]
        pwm_value = int((axis_value + 1.0) / 2.0 * 255)
        return pwm_value
    
    @staticmethod
    def map_trigger_to_pwm(trigger_value):
        """
        Maps trigger value (0.0 to 1.0) to PWM (0-255).
        
        Typical use: throttle control
        - 0.0 → 0 (no throttle)
        - 0.5 → 127 (half throttle)
        - 1.0 → 255 (full throttle)
        
        Args:
            trigger_value (float): Input from 0.0 to 1.0
            
        Returns:
            int: PWM value from 0 to 255
        """
        # Clamp value to valid range
        trigger_value = max(0.0, min(1.0, trigger_value))
        
        # Convert from [0, 1] to [0, 255]
        pwm_value = int(trigger_value * 255)
        return pwm_value
    
    @staticmethod
    def apply_deadzone(value, deadzone=0.15):
        """
        Apply deadzone to analog sticks to filter out noise from resting position.
        
        This helps prevent unwanted drift when sticks are at rest.
        
        Args:
            value (float): Input value from -1.0 to 1.0
            deadzone (float): Deadzone threshold (0.0 to 1.0), default 15%
            
        Returns:
            float: Filtered value from -1.0 to 1.0
        """
        if abs(value) < deadzone:
            return 0.0
        
        # Scale the remaining range back to [-1, 1]
        if value > 0:
            return (value - deadzone) / (1.0 - deadzone)
        else:
            return (value + deadzone) / (1.0 - deadzone)
    
    @staticmethod
    def apply_curve(value, curve_factor=1.0):
        """
        Apply exponential curve for more responsive control at edges.
        
        curve_factor > 1.0 makes control more responsive at extremes
        curve_factor = 1.0 is linear
        curve_factor < 1.0 makes control more gradual
        
        Args:
            value (float): Input from -1.0 to 1.0
            curve_factor (float): Curve intensity, typically 1.5-3.0
            
        Returns:
            float: Curved value from -1.0 to 1.0
        """
        if value >= 0:
            return (value ** curve_factor)
        else:
            return -((-value) ** curve_factor)
    
    @staticmethod
    def scale_range(value, input_min=-1.0, input_max=1.0, 
                   output_min=0, output_max=255):
        """
        Generic range scaling for custom mappings.
        
        Args:
            value: Input value
            input_min: Input range minimum
            input_max: Input range maximum
            output_min: Output range minimum
            output_max: Output range maximum
            
        Returns:
            int: Output value in desired range
        """
        value = max(input_min, min(input_max, value))
        ratio = (value - input_min) / (input_max - input_min)
        return int(output_min + ratio * (output_max - output_min))


if __name__ == "__main__":
    # Test value mapping
    print("=" * 60)
    print("STICK MAPPING TEST: [-1.0 ... 1.0] → [0 ... 255]")
    print("=" * 60)
    test_values = [-1.0, -0.75, -0.5, -0.25, 0.0, 0.25, 0.5, 0.75, 1.0]
    for val in test_values:
        pwm = ControlMapping.map_stick_to_pwm(val)
        print(f"  {val:6.2f} → {pwm:3d}")
    
    print("\n" + "=" * 60)
    print("TRIGGER MAPPING TEST: [0.0 ... 1.0] → [0 ... 255]")
    print("=" * 60)
    test_triggers = [0.0, 0.2, 0.4, 0.6, 0.8, 1.0]
    for val in test_triggers:
        pwm = ControlMapping.map_trigger_to_pwm(val)
        print(f"  {val:5.1f} → {pwm:3d}")
    
    print("\n" + "=" * 60)
    print("DEADZONE TEST: Apply 15% deadzone")
    print("=" * 60)
    test_deadzone = [-1.0, -0.2, -0.1, -0.05, 0.0, 0.05, 0.1, 0.2, 1.0]
    for val in test_deadzone:
        filtered = ControlMapping.apply_deadzone(val, deadzone=0.15)
        pwm = ControlMapping.map_stick_to_pwm(filtered)
        print(f"  {val:6.2f} → {filtered:6.2f} → PWM {pwm:3d}")
