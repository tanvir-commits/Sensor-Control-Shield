#!/usr/bin/env python3
"""Monitor UART for button debug messages"""

import sys
import serial
import time

def monitor_button():
    port = '/dev/ttyACM0'
    if len(sys.argv) > 1:
        port = sys.argv[1]
    
    print(f"Monitoring {port} for button messages...")
    print("Press the blue button (PC13) on the Nucleo board")
    print("Press Ctrl+C to exit")
    print()
    
    try:
        ser = serial.Serial(port, 115200, timeout=1.0)
        time.sleep(0.5)  # Wait for connection
        
        while True:
            if ser.in_waiting > 0:
                line = ser.readline().decode('ascii', errors='ignore').strip()
                if 'BTN:' in line:
                    print(f"[BUTTON] {line}")
                elif line and not line.startswith('HEARTBEAT'):
                    print(f"[UART] {line}")
            time.sleep(0.01)
    except KeyboardInterrupt:
        print("\nStopped monitoring")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if 'ser' in locals():
            ser.close()

if __name__ == '__main__':
    monitor_button()

