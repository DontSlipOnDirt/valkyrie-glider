#!/usr/bin/env python3
"""
Diagnostic script to test each component of the RC plane control system.
Run this to verify everything is working before full operation.
"""

import sys
import time

def test_imports():
    """Test that all required libraries are installed"""
    print("=" * 60)
    print("TEST 1: Checking Required Libraries")
    print("=" * 60)
    
    libraries = [
        ('pygame', 'Xbox controller support'),
        ('serial', 'Arduino serial communication'),
    ]
    
    all_ok = True
    for lib, description in libraries:
        try:
            __import__(lib)
            print(f"✓ {lib:15s} - {description}")
        except ImportError:
            print(f"✗ {lib:15s} - NOT INSTALLED")
            all_ok = False
    
    if not all_ok:
        print("\nInstall missing libraries with:")
        print("  pip install -r requirements.txt")
        return False
    
    print("\n✓ All libraries OK\n")
    return True


def test_xbox_controller():
    """Test Xbox controller detection"""
    print("=" * 60)
    print("TEST 2: Xbox Controller Detection")
    print("=" * 60)
    
    try:
        from xbox_reader import XboxController
        
        print("Detecting Xbox controller...")
        controller = XboxController()
        
        print("\nReading input for 5 seconds...")
        print("(Move sticks and pull triggers)\n")
        
        for i in range(50):
            state = controller.read_input()
            
            # Print if any non-zero value
            has_input = any(abs(state[k]) > 0.1 for k in [
                'left_stick_x', 'left_stick_y', 
                'right_stick_x', 'right_stick_y',
                'left_trigger', 'right_trigger'
            ])
            
            if has_input:
                print(f"Input detected! LX={state['left_stick_x']:.2f} "
                      f"LY={state['left_stick_y']:.2f} "
                      f"RT={state['right_trigger']:.2f}")
            
            time.sleep(0.1)
        
        controller.cleanup()
        print("\n✓ Xbox controller test OK\n")
        return True
    
    except Exception as e:
        print(f"✗ Xbox controller test FAILED: {e}\n")
        print("Make sure:")
        print("  1. Xbox controller is connected to PC")
        print("  2. Controller is powered on")
        print("  3. Windows recognizes the controller")
        return False


def test_value_mapping():
    """Test input to PWM mapping"""
    print("=" * 60)
    print("TEST 3: Value Mapping (Input → 0-255 PWM)")
    print("=" * 60)
    
    try:
        from value_mapper import ControlMapping
        
        print("\nTesting stick mapping [-1.0 to 1.0] → [0 to 255]:")
        test_cases = [
            (-1.0, 0, "Full left/back"),
            (-0.5, 64, "Half left/back"),
            (0.0, 127, "Center"),
            (0.5, 191, "Half right/forward"),
            (1.0, 255, "Full right/forward"),
        ]
        
        all_ok = True
        for input_val, expected, description in test_cases:
            result = ControlMapping.map_stick_to_pwm(input_val)
            status = "✓" if result == expected else "✗"
            print(f"  {status} {input_val:5.1f} → {result:3d} (expected {expected}) - {description}")
            if result != expected:
                all_ok = False
        
        print("\nTesting trigger mapping [0.0 to 1.0] → [0 to 255]:")
        test_cases = [
            (0.0, 0, "No throttle"),
            (0.5, 127, "Half throttle"),
            (1.0, 255, "Full throttle"),
        ]
        
        for input_val, expected, description in test_cases:
            result = ControlMapping.map_trigger_to_pwm(input_val)
            status = "✓" if result == expected else "✗"
            print(f"  {status} {input_val:5.1f} → {result:3d} (expected {expected}) - {description}")
            if result != expected:
                all_ok = False
        
        if all_ok:
            print("\n✓ Value mapping test OK\n")
            return True
        else:
            print("\n✗ Value mapping test FAILED\n")
            return False
    
    except Exception as e:
        print(f"✗ Value mapping test FAILED: {e}\n")
        return False


def test_serial_communication():
    """Test Arduino serial communication"""
    print("=" * 60)
    print("TEST 4: Serial Communication")
    print("=" * 60)
    
    try:
        from arduino_communicator import ArduinoSerial
        
        print("\nAvailable serial ports:")
        ArduinoSerial.list_ports()
        
        print("\nTo test Arduino communication:")
        print("  1. Connect Arduino via USB")
        print("  2. Note the COM port from the list above")
        print("  3. Modify the port in main_controller.py line with:")
        print("     controller = RCPlaneController(arduino_port='COMX')")
        print("\n✓ Serial communication test OK\n")
        return True
    
    except Exception as e:
        print(f"✗ Serial communication test FAILED: {e}\n")
        return False


def test_module_imports():
    """Test that all modules can be imported"""
    print("=" * 60)
    print("TEST 5: Module Imports")
    print("=" * 60)
    
    modules = [
        ('xbox_reader', 'XboxController'),
        ('value_mapper', 'ControlMapping'),
        ('arduino_communicator', 'ArduinoSerial'),
        ('main_controller', 'RCPlaneController'),
    ]
    
    all_ok = True
    for module_name, class_name in modules:
        try:
            module = __import__(module_name)
            cls = getattr(module, class_name)
            print(f"✓ {module_name:25s} - {class_name}")
        except Exception as e:
            print(f"✗ {module_name:25s} - FAILED: {e}")
            all_ok = False
    
    if all_ok:
        print("\n✓ All modules imported successfully\n")
        return True
    else:
        print("\n✗ Some modules failed to import\n")
        return False


def main():
    """Run all diagnostic tests"""
    print("\n")
    print("╔" + "=" * 58 + "╗")
    print("║" + " " * 58 + "║")
    print("║" + "  RC PLANE CONTROL SYSTEM - DIAGNOSTIC TEST".center(58) + "║")
    print("║" + " " * 58 + "║")
    print("╚" + "=" * 58 + "╝")
    print()
    
    results = []
    
    # Run tests
    results.append(("Required Libraries", test_imports()))
    if results[-1][1]:  # Only continue if imports OK
        results.append(("Xbox Controller", test_xbox_controller()))
        results.append(("Value Mapping", test_value_mapping()))
        results.append(("Serial Communication", test_serial_communication()))
        results.append(("Module Imports", test_module_imports()))
    
    # Summary
    print("=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"  {status:8s} - {test_name}")
    
    print("=" * 60)
    
    # Overall result
    passed = sum(1 for _, r in results if r)
    total = len(results)
    
    if passed == total:
        print(f"\n✓ All tests passed! ({passed}/{total})")
        print("\nNext steps:")
        print("  1. Connect an Xbox controller")
        print("  2. Upload rc_plane_receiver.ino to Arduino")
        print("  3. Update the COM port in main_controller.py")
        print("  4. Run: python main_controller.py")
        return 0
    else:
        print(f"\n✗ Some tests failed ({passed}/{total})")
        print("\nFix the failures above before proceeding.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
