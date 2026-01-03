#!/usr/bin/env python3
"""Test all QA tasks to verify they respond correctly."""

import serial
import time
import sys

def test_tasks(port='/dev/ttyACM0', baud=115200):
    """Test all tasks on the specified port."""
    try:
        uart = serial.Serial(port, baud, timeout=3)
        print(f'Connected to {port} at {baud} baud\n')
        
        # Wait for connection to stabilize
        time.sleep(2)
        uart.reset_input_buffer()
        
        # Expected responses for each task
        expected = {
            1: ['LED', 'blink', 'OK'],
            2: ['LCD', 'off', 'OK'],
            3: ['LCD', 'on', 'OK'],
            4: ['Gallery', 'Normal', 'bitmap', 'OK']
        }
        
        print('=' * 50)
        print('Testing All Tasks')
        print('=' * 50)
        
        results = {}
        
        for task_num in range(1, 5):
            print(f'\n[TASK {task_num}]')
            print('-' * 30)
            
            # Clear buffer
            time.sleep(0.3)
            uart.reset_input_buffer()
            
            # Send command
            cmd = f'TASK {task_num}\r\n'
            uart.write(cmd.encode())
            uart.flush()
            print(f'Sent: {cmd.strip()}')
            
            # Wait for response
            time.sleep(2)
            
            # Read response
            response = uart.read(uart.in_waiting).decode('utf-8', errors='ignore')
            
            if response:
                # Filter out heartbeat and clean up
                lines = []
                for line in response.split('\n'):
                    line = line.strip()
                    if line and not line.startswith('HEARTBEAT') and not line.startswith('['):
                        lines.append(line)
                
                if lines:
                    print(f'Response received:')
                    for line in lines[:5]:  # Show up to 5 lines
                        print(f'  {line}')
                    
                    # Check if response contains expected keywords
                    response_lower = ' '.join(lines).lower()
                    expected_keywords = expected.get(task_num, [])
                    found_keywords = [kw for kw in expected_keywords if kw.lower() in response_lower]
                    
                    if found_keywords:
                        print(f'✓ Contains expected keywords: {found_keywords}')
                        results[task_num] = 'PASS'
                    else:
                        print(f'? Unexpected response (expected: {expected_keywords})')
                        results[task_num] = 'UNEXPECTED'
                else:
                    print('✗ No valid response lines')
                    results[task_num] = 'FAIL'
            else:
                print('✗ No response received')
                results[task_num] = 'FAIL'
        
        # Summary
        print('\n' + '=' * 50)
        print('Summary')
        print('=' * 50)
        for task_num in range(1, 5):
            status = results.get(task_num, 'NOT TESTED')
            print(f'TASK {task_num}: {status}')
        
        uart.close()
        return results
        
    except serial.SerialException as e:
        print(f'Error opening serial port {port}: {e}')
        print('\nTrying alternative ports...')
        return None
    except Exception as e:
        print(f'Error: {e}')
        import traceback
        traceback.print_exc()
        return None

if __name__ == '__main__':
    # Try multiple ports
    ports_to_try = ['/dev/ttyACM0', '/dev/ttyUSB0', '/dev/ttyUSB2']
    
    results = None
    for port in ports_to_try:
        print(f'\nTrying port: {port}')
        results = test_tasks(port)
        if results:
            break
    
    if not results:
        print('\n✗ Could not connect to any port')
        print('Please ensure:')
        print('  1. Board is powered and connected')
        print('  2. UART cable is connected')
        print('  3. Board has been reset after flashing')
        sys.exit(1)

