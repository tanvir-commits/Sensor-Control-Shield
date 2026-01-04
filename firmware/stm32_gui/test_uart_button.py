#!/usr/bin/env python3
"""Simple script to test UART button commands for screen switching."""

import serial
import time
import sys

def test_screen_switching(port='/dev/ttyACM0', baud=115200):
    """Send PLAY button commands to test screen switching."""
    try:
        print(f"Connecting to {port} at {baud} baud...")
        ser = serial.Serial(port, baud, timeout=1)
        time.sleep(0.5)  # Wait for connection
        
        print("\nSending PLAY button commands to switch screens...")
        print("You should see the screen change on the display.\n")
        
        for i in range(6):  # Cycle through screens twice
            print(f"  [{i+1}] Sending BTN:PLAY:PRESS...")
            ser.write(b'BTN:PLAY:PRESS\n')
            time.sleep(0.2)  # Wait a bit
            
            print(f"  [{i+1}] Sending BTN:PLAY:RELEASE...")
            ser.write(b'BTN:PLAY:RELEASE\n')
            time.sleep(1.0)  # Wait to see screen change
            
        ser.close()
        print("\nTest complete! Screen should have cycled: Screen1 -> Screen2 -> Screen5 -> Screen1 -> ...")
        
    except serial.SerialException as e:
        print(f"Error: Could not open serial port {port}")
        print(f"  {e}")
        print("\nTry:")
        print("  - Check if device is connected")
        print("  - Try different port: /dev/ttyUSB0, /dev/ttyACM1, etc.")
        print("  - Check permissions: sudo chmod 666 /dev/ttyACM0")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
        if 'ser' in locals():
            ser.close()
        sys.exit(0)

if __name__ == '__main__':
    port = sys.argv[1] if len(sys.argv) > 1 else '/dev/ttyACM0'
    test_screen_switching(port)



