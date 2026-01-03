#!/usr/bin/env python3
"""Set backlight brightness via UART command"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from hardware.uart_manager import UARTManager
import time

def set_backlight(level=None):
    """Set backlight brightness
    
    Args:
        level: Brightness level (0-100) or None to cycle through levels
    """
    uart = UARTManager()
    # Try ttyUSB2 first (STM32 Nucleo), then ttyACM0
    port = '/dev/ttyUSB2'
    
    if len(sys.argv) > 1:
        port = sys.argv[1]
    
    print(f"Opening {port}...")
    if not uart.open(port, 115200):
        print(f"Failed to open {port}")
        return
    
    time.sleep(0.5)
    
    if level is not None:
        # Cycle through levels until we reach the desired one
        print(f"Setting backlight to {level}%...")
        print("(Task 14 cycles: 0%, 5%, 20%, 25%, 50%, 75%, 100%)")
        print()
        
        # Levels available: 0, 5, 20, 25, 50, 75, 100
        levels = [0, 5, 20, 25, 50, 75, 100]
        if level not in levels:
            print(f"Warning: {level}% not in available levels. Using closest match.")
            # Find closest level
            level = min(levels, key=lambda x: abs(x - level))
            print(f"Using {level}% instead.")
        
        # Send task 14 until we reach the desired level
        # This is a bit tricky since it cycles, but we can try
        for i in range(10):  # Try up to 10 times
            success, resp = uart.send_task(14)
            if success and resp:
                print(f"  Response: {resp}")
                if f"{level}%" in resp:
                    print(f"\n✓ Backlight set to {level}%")
                    break
            time.sleep(0.3)
    else:
        # Just send task 14 once to cycle to next level
        print("Cycling to next brightness level...")
        success, resp = uart.send_task(14)
        if success:
            print(f"Response: {resp}")
        else:
            print(f"Error: {resp}")
    
    uart.close()

if __name__ == '__main__':
    # Check if brightness level provided
    if len(sys.argv) > 2:
        try:
            level = int(sys.argv[2])
            set_backlight(level)
        except ValueError:
            print(f"Invalid brightness level: {sys.argv[2]}")
            print("Usage: python3 set_backlight.py [port] [brightness_level]")
            print("  brightness_level: 0, 5, 20, 25, 50, 75, or 100")
    else:
        set_backlight()

