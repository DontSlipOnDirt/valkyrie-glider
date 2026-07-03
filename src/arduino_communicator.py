import serial
import time

class ArduinoSerial:
    """Manages serial communication with Arduino board"""
    
    def __init__(self, port='COM3', baudrate=9600, timeout=1.0):
        """
        Initialize serial connection to Arduino.
        
        Args:
            port (str): Serial port (e.g., 'COM3' on Windows)
                       Use 'list' to see available ports
            baudrate (int): Baud rate (must match Arduino code, typically 9600)
            timeout (float): Read timeout in seconds
            
        Raises:
            Exception: If port cannot be opened
        """
        if port.lower() == 'list':
            self.list_ports()
            raise ValueError("List requested. Found available ports above.")
        
        try:
            self.ser = serial.Serial(port=port, baudrate=baudrate, timeout=timeout)
            time.sleep(2)  # Wait for Arduino to initialize
            self.port = port
            self.baudrate = baudrate
            print(f"✓ Connected to Arduino on {port} at {baudrate} baud")
        except serial.SerialException as e:
            print(f"✗ Error opening serial port {port}: {e}")
            self.list_ports()
            raise
    
    @staticmethod
    def list_ports():
        """List all available serial ports"""
        try:
            import serial.tools.list_ports
            ports = serial.tools.list_ports.comports()
            if ports:
                print("\nAvailable serial ports:")
                for port in ports:
                    print(f"  {port.device:10s} - {port.description}")
            else:
                print("No serial ports found")
        except Exception as e:
            print(f"Could not list ports: {e}")
    
    def send_pwm_values(self, channel_values):
        """
        Send PWM values to Arduino using named channel format.
        
        Format sent: "P:channel1:value1,channel2:value2,...\n"
        
        Args:
            channel_values (dict): {'throttle': 128, 'pitch': 200, ...}
            
        Returns:
            bool: True if sent successfully, False otherwise
        """
        if not self.ser.is_open:
            print("✗ Serial port is closed!")
            return False
        
        try:
            # Build message: "P:throttle:128,pitch:200,roll:150,yaw:180\n"
            message = "P:"
            for channel, value in channel_values.items():
                # Ensure value is in 0-255 range
                value = max(0, min(255, int(value)))
                message += f"{channel}:{value},"
            
            # Remove trailing comma and add newline
            message = message.rstrip(',') + '\n'
            
            self.ser.write(message.encode())
            return True
        except Exception as e:
            print(f"✗ Error sending data: {e}")
            return False
    
    def send_simple_values(self, *values):
        """
        Send simple comma-separated PWM values.
        
        Format sent: "value1,value2,value3,...\n"
        Arduino must know the order of channels.
        
        Usage:
            send_simple_values(128, 200, 150, 180)  # throttle,pitch,roll,yaw
        
        Args:
            values: Variable number of 0-255 integers
            
        Returns:
            bool: True if sent successfully, False otherwise
        """
        if not self.ser.is_open:
            print("✗ Serial port is closed!")
            return False
        
        try:
            # Convert all values to 0-255 range
            value_strs = [str(max(0, min(255, int(v)))) for v in values]
            message = ','.join(value_strs) + '\n'
            
            self.ser.write(message.encode())
            return True
        except Exception as e:
            print(f"✗ Error sending data: {e}")
            return False
    
    def read_response(self):
        """
        Read a response line from Arduino.
        
        Returns:
            str: Response from Arduino, or None if no data available
        """
        try:
            if self.ser.in_waiting > 0:
                response = self.ser.readline().decode('utf-8').strip()
                return response
        except Exception as e:
            print(f"✗ Error reading data: {e}")
        return None
    
    def wait_for_ready(self, timeout=5):
        """
        Wait for Arduino to send ready message.
        
        Args:
            timeout (int): Maximum seconds to wait
            
        Returns:
            bool: True if Arduino sent ready message, False on timeout
        """
        start_time = time.time()
        while time.time() - start_time < timeout:
            response = self.read_response()
            if response and 'ready' in response.lower():
                print(f"✓ Arduino ready: {response}")
                return True
            time.sleep(0.1)
        return False
    
    def close(self):
        """Close serial connection"""
        if self.ser.is_open:
            self.ser.close()
            print(f"✓ Closed serial connection on {self.port}")
    
    def __enter__(self):
        """Context manager support"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager support"""
        self.close()


if __name__ == "__main__":
    # Test serial communication
    try:
        print("Testing serial communication...\n")
        
        # List available ports
        ArduinoSerial.list_ports()
        
        # Try to connect (will fail if no Arduino, which is fine for testing)
        print("\nTo test actual connection, modify the port below:")
        print('  serial_comm = ArduinoSerial("COM3")  # Change COM3 to your port\n')
        
        # Example of what the code would look like:
        # serial_comm = ArduinoSerial("COM3")
        # serial_comm.send_simple_values(128, 127, 127, 127)
        # time.sleep(1)
        # serial_comm.send_pwm_values({'throttle': 128, 'pitch': 127})
        # serial_comm.close()
        
    except Exception as e:
        print(f"Note: {e}")
