#!/usr/bin/env python3
"""Simplest automation: Press Enter on the dialog (triggers default Launch button)."""

import subprocess
import sys
import time

def click_launch_via_enter():
    """Open dialog and press Enter - simplest automation possible!"""
    
    # Find Device Panel window
    result = subprocess.run(['xdotool', 'search', '--name', 'Device Panel'], 
                          capture_output=True, text=True)
    window_ids = [id for id in result.stdout.strip().split('\n') if id]
    
    if not window_ids:
        print("❌ Device Panel window not found")
        return False
    
    main_window = window_ids[0]
    print(f"✓ Found Device Panel: {main_window}")
    
    # Activate and open menu
    subprocess.run(['xdotool', 'windowactivate', main_window])
    time.sleep(0.5)
    subprocess.run(['xdotool', 'key', 'alt+t'])  # Tools menu
    time.sleep(1)
    subprocess.run(['xdotool', 'key', 'Down'])   # Select "Show App Suggestions..."
    time.sleep(0.5)
    subprocess.run(['xdotool', 'key', 'Return']) # Open dialog
    time.sleep(2)
    
    # Find dialog
    result = subprocess.run(['xdotool', 'search', '--name', 'App Suggestions'], 
                          capture_output=True, text=True)
    dialog_ids = [id for id in result.stdout.strip().split('\n') if id]
    
    if not dialog_ids:
        print("❌ Dialog not found")
        return False
    
    dialog = dialog_ids[0]
    print(f"✓ Found dialog: {dialog}")
    
    # Activate dialog and press Enter (triggers default Launch button!)
    subprocess.run(['xdotool', 'windowactivate', dialog])
    time.sleep(0.5)
    subprocess.run(['xdotool', 'key', 'Return'])
    print("✅ Pressed Enter - Launch button should be triggered!")
    
    return True

if __name__ == '__main__':
    success = click_launch_via_enter()
    sys.exit(0 if success else 1)


