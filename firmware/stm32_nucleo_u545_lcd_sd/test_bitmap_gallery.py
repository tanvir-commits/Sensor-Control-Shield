#!/usr/bin/env python3
"""Test bitmap gallery via UART"""

import sys
import os
import time

# Add project root to path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
sys.path.insert(0, project_root)

from hardware.uart_manager import UARTManager

def test_bitmap_gallery():
    uart = UARTManager()
    
    # Try to open UART
    port = '/dev/ttyACM0'
    if len(sys.argv) > 1:
        port = sys.argv[1]
    
    print(f"Opening {port}...")
    if not uart.open(port, 115200):
        print(f"Failed to open {port}")
        return
    
    print("Testing bitmap gallery...")
    print()
    
    # Check current mode and bitmap count
    print("1. Checking gallery status (task 15)...")
    success, response = uart.send_task(15)
    print(f"   Response: {response}")
    print()
    
    # Wait a bit
    time.sleep(0.5)
    
    # Try to cycle to next bitmap
    print("2. Cycling to next bitmap (task 16)...")
    success, response = uart.send_task(16)
    print(f"   Response: {response}")
    print()
    
    time.sleep(0.5)
    
    # Try again
    print("3. Cycling to next bitmap again (task 16)...")
    success, response = uart.send_task(16)
    print(f"   Response: {response}")
    print()
    
    uart.close()
    print("Test complete!")

if __name__ == '__main__':
    test_bitmap_gallery()

