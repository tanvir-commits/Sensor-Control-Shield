#!/usr/bin/env python3
"""Simple button test - shows clear output"""

import sys
import serial
import time

port = '/dev/ttyACM0'
if len(sys.argv) > 1:
    port = sys.argv[1]

print("=" * 60)
print("BUTTON TEST - Monitoring UART for button presses")
print("=" * 60)
print(f"Port: {port}")
print("Press the BLUE button (PC13) on the Nucleo board")
print("You should see button state messages below")
print("Press Ctrl+C to exit")
print("=" * 60)
print()

try:
    ser = serial.Serial(port, 115200, timeout=1.0)
    time.sleep(0.5)  # Wait for connection
    
    print("Connected! Waiting for button presses...\n")
    
    while True:
        if ser.in_waiting > 0:
            line = ser.readline().decode('ascii', errors='ignore').strip()
            if 'BTN:' in line:
                print(f"✓ {line}")
            elif line and not line.startswith('HEARTBEAT'):
                print(f"  {line}")
        time.sleep(0.01)
except KeyboardInterrupt:
    print("\n\nTest stopped")
except Exception as e:
    print(f"\nError: {e}")
    print("\nMake sure:")
    print("  1. The board is connected to", port)
    print("  2. You have permission to access the port")
    print("  3. No other program is using the port")
finally:
    if 'ser' in locals():
        ser.close()

