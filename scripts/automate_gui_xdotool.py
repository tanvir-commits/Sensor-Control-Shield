#!/usr/bin/env python3
"""Automate Device Panel GUI using xdotool via SSH.

This script uses SSH to run xdotool commands on the Pi, automating GUI interactions.
You can watch the actions happen in real-time on your monitor connected to the Pi.
"""

import subprocess
import time
import sys

PI_HOST = 'a@192.168.101'
DISPLAY = ':0'

def run_ssh_command(cmd):
    """Run a command on the Pi via SSH."""
    full_cmd = f'ssh {PI_HOST} "export DISPLAY={DISPLAY} && {cmd}"'
    print(f"Running: {cmd}")
    result = subprocess.run(full_cmd, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error: {result.stderr}")
    return result.returncode == 0

def find_window(title_pattern):
    """Find window by title pattern."""
    cmd = f'xdotool search --name "{title_pattern}" | head -1'
    result = subprocess.run(
        f'ssh {PI_HOST} "export DISPLAY={DISPLAY} && {cmd}"',
        shell=True, capture_output=True, text=True
    )
    if result.returncode == 0 and result.stdout.strip():
        return result.stdout.strip()
    return None

def wait_for_window(title_pattern, timeout=30):
    """Wait for window to appear."""
    print(f"Waiting for window matching '{title_pattern}'...")
    start_time = time.time()
    while time.time() - start_time < timeout:
        window_id = find_window(title_pattern)
        if window_id:
            print(f"✓ Found window: {window_id}")
            return window_id
        time.sleep(0.5)
        print(".", end="", flush=True)
    print("\n✗ Window not found")
    return None

def automate_gui():
    """Main automation function."""
    print("=" * 60)
    print("Device Panel GUI Automation via xdotool")
    print("=" * 60)
    print("Make sure Device Panel is running and visible on your monitor!")
    print()
    
    # Wait for Device Panel window - try multiple patterns
    window_id = None
    for pattern in ["Device Panel", "device_panel", "QApplication"]:
        window_id = wait_for_window(pattern)
        if window_id:
            break
    
    if not window_id:
        # Try finding by class instead
        print("Trying to find window by class...")
        result = subprocess.run(
            f'ssh {PI_HOST} "export DISPLAY={DISPLAY} && xdotool search --class QApplication | head -1"',
            shell=True, capture_output=True, text=True
        )
        if result.returncode == 0 and result.stdout.strip():
            window_id = result.stdout.strip()
            print(f"✓ Found window by class: {window_id}")
    
    if not window_id:
        print("Device Panel window not found. Is the app running?")
        return False
    
    # Activate the window
    print("\n1. Activating Device Panel window...")
    run_ssh_command(f'xdotool windowactivate {window_id}')
    time.sleep(1)
    
    # Click on Tools menu (Alt+T or click at menu location)
    print("2. Opening 'Tools' menu...")
    # Try keyboard shortcut first (Alt+T)
    run_ssh_command(f'xdotool key --window {window_id} alt+t')
    time.sleep(2)
    
    # Click on "Show App Suggestions..." menu item
    print("3. Clicking 'Show App Suggestions...'...")
    # Menu items are typically below the menu bar
    # Try multiple Y coordinates to find the menu item
    for y_pos in [70, 90, 110]:
        print(f"   Trying Y position: {y_pos}")
        run_ssh_command(f'xdotool mousemove --window {window_id} 150 {y_pos}')
        time.sleep(0.3)
        run_ssh_command(f'xdotool click --window {window_id} 1')
        time.sleep(2)
        
        # Check if dialog opened
        result = subprocess.run(
            f'ssh {PI_HOST} "export DISPLAY={DISPLAY} && xdotool search --class QDialog | head -1"',
            shell=True, capture_output=True, text=True
        )
        if result.returncode == 0 and result.stdout.strip():
            print(f"   ✓ Dialog detected!")
            break
    
    # Wait for dialog
    print("4. Waiting for suggestions dialog...")
    dialog_id = wait_for_window("App Suggestions")
    if dialog_id:
        print("✓ Suggestions dialog opened!")
        print("\nAutomation complete! The dialog should be visible on your monitor.")
    else:
        print("Dialog may have opened but wasn't detected.")
    
    return True

if __name__ == '__main__':
    print("\nBefore running:")
    print("1. Make sure Device Panel app is running on Pi")
    print("2. Make sure you can see it on your monitor")
    print("3. Then run this script\n")
    
    input("Press Enter when ready to start automation...")
    automate_gui()

