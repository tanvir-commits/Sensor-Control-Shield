#!/usr/bin/env python3
"""
LCD Test Script for STM32 NUCLEO-U545RE-Q
Tests LCD functionality via UART commands
"""

import sys
import os
import time

# Add project root to path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
sys.path.insert(0, project_root)

from hardware.uart_manager import UARTManager

def test_lcd(port: str, baud_rate: int = 115200):
    """Test LCD functionality."""
    print("=" * 60)
    print("LCD Functionality Test")
    print("=" * 60)
    print(f"Port: {port}")
    print(f"Baud: {baud_rate}\n")
    
    uart = UARTManager()
    
    print("Connecting...")
    if not uart.open(port, baud_rate):
        print(f"✗ FAIL: Failed to open UART port {port}")
        return False
    
    print("✓ Connected\n")
    
    # Wait for any startup messages
    time.sleep(0.5)
    
    # Wait for board to stabilize
    time.sleep(1.5)
    
    # Test 1: Basic UART Communication
    print("Test 1: Basic UART Communication (TASK 1)")
    print("-" * 60)
    success, response = uart.send_command("TASK 1")
    if success and response and "OK" in response:
        print(f"✓ PASS: {response}")
    else:
        print(f"✗ FAIL: {response}")
        uart.close()
        return False
    print()
    
    time.sleep(0.5)
    
    # Test 2: LCD Initialize
    print("Test 2: LCD Initialize (TASK 9)")
    print("-" * 60)
    success, response = uart.send_command("TASK 9")
    if success and response and "OK" in response:
        print(f"✓ PASS: {response}")
    else:
        print(f"✗ FAIL: {response}")
        print("  → Check LCD connections:")
        print("     PC9 (D10) → CS, PA9 (D8) → DC, PA8 (D7) → RST")
        print("     PB10 (D6) → BL, PA5 (D13) → SCK, PA7 (D11) → MOSI")
        print("     VCC → 3.3V, GND → GND")
    print()
    
    # Wait a bit for initialization
    time.sleep(0.5)
    
    # Test 3: LCD Test Pattern
    print("Test 3: LCD Test Pattern (TASK 10)")
    print("-" * 60)
    success, response = uart.send_command("TASK 10")
    if success and response and "OK" in response:
        print(f"✓ PASS: {response}")
        print("  → LCD should display test patterns:")
        print("     - Color fills (red, green, blue, white)")
        print("     - Colored rectangles")
    else:
        print(f"✗ FAIL: {response}")
    print()
    
    uart.close()
    
    print("=" * 60)
    print("Test Summary")
    print("=" * 60)
    print("✓ UART communication: Working")
    print("? LCD: Check display for test patterns")
    print()
    
    return True

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: test_lcd.py <port> [baud_rate]")
        print("Example: test_lcd.py /dev/ttyUSB2 115200")
        sys.exit(1)
    
    port = sys.argv[1]
    baud_rate = int(sys.argv[2]) if len(sys.argv) > 2 else 115200
    
    test_lcd(port, baud_rate)

