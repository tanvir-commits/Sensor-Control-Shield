#!/usr/bin/env python3
"""Test backlight brightness commands"""
import sys
sys.path.insert(0, '../..')
from hardware.uart_manager import UARTManager
import time

print('=' * 70)
print('Testing Backlight Brightness Commands')
print('=' * 70)
print()

uart = UARTManager()
try:
    # Try both possible ports
    ports = ['/dev/ttyUSB2', '/dev/ttyACM0']
    port_opened = False
    
    for port in ports:
        try:
            print(f'Attempting to open {port} at 115200...')
            uart.open(port, 115200)
            time.sleep(1)  # Wait for board to stabilize
            uart.flush()
            print(f'✓ Port {port} opened successfully')
            port_opened = True
            break
        except Exception as e:
            print(f'✗ Failed to open {port}: {e}')
            continue
    
    if not port_opened:
        print('✗ Could not open any serial port')
        sys.exit(1)
    
    print()
    
    # Test Task 14: Cycle through brightness levels
    print('Test 1: Task 14 - Cycling through brightness levels (0%, 25%, 50%, 75%, 100%)')
    print('-' * 70)
    for i in range(5):
        print(f'\nSending TASK 14 (cycle {i+1}/5)...')
        response = uart.send_command('TASK 14')
        if response[0]:
            print(f'✓ Response: {response[1]}')
        else:
            print(f'✗ No response: {response[1]}')
        time.sleep(1)  # Wait 1 second between commands to see the brightness change
    
    print()
    print('-' * 70)
    print()
    
    # Test Task 12: Toggle between 0% and 50%
    print('Test 2: Task 12 - Toggle between 0% and 50% brightness')
    print('-' * 70)
    for i in range(4):
        print(f'\nSending TASK 12 (toggle {i+1}/4)...')
        response = uart.send_command('TASK 12')
        if response[0]:
            print(f'✓ Response: {response[1]}')
        else:
            print(f'✗ No response: {response[1]}')
        time.sleep(1)  # Wait 1 second between commands
    
    print()
    print('-' * 70)
    print()
    
    # Final test: Set to 100% brightness
    print('Test 3: Setting to maximum brightness (100%)')
    print('-' * 70)
    # Cycle through Task 14 until we get to 100%
    for i in range(5):
        response = uart.send_command('TASK 14')
        if response[0] and '100%' in response[1]:
            print(f'✓ Reached 100% brightness: {response[1]}')
            break
        time.sleep(0.5)
    
    print()
    print('=' * 70)
    print('✓ Backlight brightness tests completed!')
    print('  Check the LCD backlight to verify brightness changes.')
    print('=' * 70)
    
    uart.close()
    
except Exception as e:
    print(f'✗ Error: {e}')
    import traceback
    traceback.print_exc()
    if uart.is_open():
        uart.close()

