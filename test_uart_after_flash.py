#!/usr/bin/env python3
"""Test UART communication after flashing firmware"""
import sys
sys.path.insert(0, '.')
from hardware.uart_manager import UARTManager
import time

print('=' * 70)
print('Testing UART Communication After Flash')
print('=' * 70)
print()

uart = UARTManager()
try:
    print('Opening /dev/ttyUSB2 at 115200...')
    uart.open('/dev/ttyUSB2', 115200)
    time.sleep(1)  # Wait for board to stabilize
    uart.flush()
    
    print('✓ Port opened successfully')
    print()
    
    # Test 1: MCU Status (should respond quickly)
    print('Test 1: Sending TASK 2 (MCU Status)...')
    response = uart.send_command('TASK 2')
    if response[0]:
        print(f'✓ Board responded: {response[1]}')
    else:
        print(f'✗ No response: {response[1]}')
    print()
    
    # Test 2: LED Blink
    print('Test 2: Sending TASK 1 (LED Blink)...')
    response = uart.send_command('TASK 1')
    if response[0]:
        print(f'✓ Board responded: {response[1]}')
        print('  (Check if LED blinked 3 times and is now ON)')
    else:
        print(f'✗ No response: {response[1]}')
    print()
    
    uart.close()
    print('=' * 70)
    if response[0]:
        print('✓ Board is responding over UART!')
        print('  Clock configuration is working correctly.')
    else:
        print('✗ Board is NOT responding')
        print('  Possible issues:')
        print('    - Firmware not flashed correctly')
        print('    - Wrong serial port (/dev/ttyUSB2)')
        print('    - Clock configuration still incorrect')
    print('=' * 70)
    
except Exception as e:
    print(f'✗ Error: {e}')
    import traceback
    traceback.print_exc()
