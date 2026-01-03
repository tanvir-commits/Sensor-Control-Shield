#!/usr/bin/env python3
"""
Test script for SD card functionality on STM32 NUCLEO-U545RE-Q

Usage:
    python3 test_sd_card.py [port] [baud_rate]

Example:
    python3 test_sd_card.py /dev/ttyUSB2 115200
"""

import sys
import os
import time

# Add project root to path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
sys.path.insert(0, project_root)

from hardware.uart_manager import UARTManager

def test_sd_card(port='/dev/ttyUSB2', baud_rate=115200):
    """Test SD card functionality via UART commands."""
    
    print("=" * 60)
    print("SD Card Functionality Test")
    print("=" * 60)
    print(f"Port: {port}")
    print(f"Baud: {baud_rate}\n")
    
    uart = UARTManager()
    
    # Connect
    print("Connecting...")
    if not uart.open(port, baud_rate, timeout=3.0):
        print(f"✗ Failed to connect to {port}")
        return False
    
    print("✓ Connected\n")
    time.sleep(1.5)  # Wait for board to stabilize
    
    results = {}
    
    # Test 1: Basic communication
    print("Test 1: Basic UART Communication (TASK 1)")
    print("-" * 60)
    success, response = uart.send_command('TASK 1')
    results['task1'] = (success, response)
    if success and 'OK' in response:
        print(f"✓ PASS: {response}\n")
    else:
        print(f"✗ FAIL: {response}\n")
        uart.close()
        return False
    
    time.sleep(0.5)
    
    # Test 2: MCU Status
    print("Test 2: MCU Status (TASK 2)")
    print("-" * 60)
    success, response = uart.send_command('TASK 2')
    results['task2'] = (success, response)
    if success and 'OK' in response:
        print(f"✓ PASS: {response}\n")
    else:
        print(f"✗ FAIL: {response}\n")
    
    time.sleep(0.5)
    
    # Test 3: SD Card Initialize
    print("Test 3: SD Card Initialize (TASK 6)")
    print("-" * 60)
    success, response = uart.send_command('TASK 6')
    results['task6'] = (success, response)
    print(f"Response: {response}")
    
    if 'not registered' in response:
        print("⚠ TASK 6 not registered")
        print("  → Board is running old firmware")
        print("  → Flash new firmware: cd firmware/stm32_nucleo_u545_lcd_sd && make flash\n")
        sd_available = False
    elif success and 'OK' in response and 'initialized' in response.lower():
        print("✓ PASS: SD card initialized successfully\n")
        sd_available = True
    elif 'ERR' in response:
        print("✗ FAIL: SD card initialization failed")
        print("  → Check SD card connections (Arduino shield):")
        print("     PC9 (D10) → CS, PA5 (D13) → SCK, PA6 (D12) → MISO, PA7 (D11) → MOSI")
        print("     VCC → 3.3V, GND → GND")
        print("     Shield should plug directly into CN7 Arduino header")
        print(f"  → Error: {response}\n")
        sd_available = False
    else:
        print(f"⚠ Unexpected response: {response}\n")
        sd_available = False
    
    if not sd_available:
        uart.close()
        print("=" * 60)
        print("Test Summary")
        print("=" * 60)
        print("✓ UART communication: Working")
        print("⚠ SD card: Not available (firmware or hardware issue)")
        return False
    
    time.sleep(0.5)
    
    # Test 4: SD Card Read
    print("Test 4: SD Card Read Block 0 (TASK 7)")
    print("-" * 60)
    success, response = uart.send_command('TASK 7')
    results['task7'] = (success, response)
    print(f"Response: {response}")
    
    if success and 'OK' in response and 'read OK' in response.lower():
        print("✓ PASS: SD card read successful")
        # Extract hex data if present
        if 'first bytes:' in response:
            hex_part = response.split('first bytes:')[1].strip()
            print(f"  → First 16 bytes: {hex_part}\n")
        else:
            print()
    elif 'not initialized' in response.lower():
        print("✗ FAIL: SD card not initialized")
        print("  → Run TASK 6 first\n")
    else:
        print(f"✗ FAIL: {response}\n")
    
    time.sleep(0.5)
    
    # Test 5: SD Card Write
    print("Test 5: SD Card Write Block 0 (TASK 8)")
    print("-" * 60)
    success, response = uart.send_command('TASK 8')
    results['task8'] = (success, response)
    print(f"Response: {response}")
    
    if success and 'OK' in response and 'written' in response.lower():
        print("✓ PASS: SD card write successful")
        print("  → Test pattern written to block 0\n")
    elif 'not initialized' in response.lower():
        print("✗ FAIL: SD card not initialized")
        print("  → Run TASK 6 first\n")
    else:
        print(f"✗ FAIL: {response}\n")
    
    # Test 6: Verify write by reading again
    print("Test 6: Verify Write (Read Block 0 again)")
    print("-" * 60)
    time.sleep(0.5)
    success, response = uart.send_command('TASK 7')
    results['task7_verify'] = (success, response)
    print(f"Response: {response}")
    
    if success and 'OK' in response:
        print("✓ PASS: Block read after write successful")
        if 'first bytes:' in response:
            hex_part = response.split('first bytes:')[1].strip()
            print(f"  → Data: {hex_part}")
            # Check if it matches test pattern (00 01 02 03 ...)
            if hex_part.startswith('00010203'):
                print("  → ✓ Test pattern verified!\n")
            else:
                print("  → ⚠ Data doesn't match expected pattern\n")
        else:
            print()
    else:
        print(f"✗ FAIL: {response}\n")
    
    uart.close()
    
    # Summary
    print("=" * 60)
    print("Test Summary")
    print("=" * 60)
    print(f"UART Communication: {'✓ PASS' if results.get('task1', (False,))[0] else '✗ FAIL'}")
    print(f"MCU Status: {'✓ PASS' if results.get('task2', (False,))[0] else '✗ FAIL'}")
    print(f"SD Card Init: {'✓ PASS' if results.get('task6', (False,))[0] and 'initialized' in results.get('task6', (False, ''))[1].lower() else '✗ FAIL'}")
    print(f"SD Card Read: {'✓ PASS' if results.get('task7', (False,))[0] else '✗ FAIL'}")
    print(f"SD Card Write: {'✓ PASS' if results.get('task8', (False,))[0] else '✗ FAIL'}")
    print("=" * 60)
    
    # Overall result
    all_passed = (
        results.get('task1', (False,))[0] and
        results.get('task2', (False,))[0] and
        results.get('task6', (False,))[0] and
        results.get('task7', (False,))[0] and
        results.get('task8', (False,))[0]
    )
    
    if all_passed:
        print("\n🎉 All tests PASSED! SD card functionality is working.\n")
        return True
    else:
        print("\n⚠ Some tests failed. Check individual results above.\n")
        return False

if __name__ == '__main__':
    port = sys.argv[1] if len(sys.argv) > 1 else '/dev/ttyUSB2'
    baud = int(sys.argv[2]) if len(sys.argv) > 2 else 115200
    
    try:
        success = test_sd_card(port, baud)
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

