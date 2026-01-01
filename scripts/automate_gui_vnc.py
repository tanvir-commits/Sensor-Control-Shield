#!/usr/bin/env python3
"""Automate Device Panel GUI via VNC connection.

This script connects to the Pi's VNC server and automates GUI interactions
so you can watch the actions happen in real-time on your monitor.
"""

import time
import sys
from vncdotool import api

VNC_HOST = '192.168.101'
VNC_PORT = 5900
VNC_PASSWORD = 'devicepanel'
VNC_URL = f'{VNC_HOST}:{VNC_PORT}'

def wait_for_window(client, timeout=30):
    """Wait for Device Panel window to appear."""
    print("Waiting for Device Panel window to appear...")
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            # Take a screenshot to check if window is visible
            # For now, just wait a bit
            time.sleep(1)
            print(".", end="", flush=True)
        except Exception as e:
            print(f"\nError waiting: {e}")
            time.sleep(1)
    print()

def automate_gui():
    """Main automation function."""
    print("=" * 60)
    print("Device Panel GUI Automation via VNC")
    print("=" * 60)
    print(f"Connecting to VNC server at {VNC_URL}...")
    print("(Make sure you have the VNC viewer open to watch!)")
    print()
    
    try:
        # Connect to VNC server
        client = api.connect(VNC_URL, password=VNC_PASSWORD)
        print("✓ Connected to VNC server")
        time.sleep(2)
        
        # Wait a bit for everything to settle
        print("\nWaiting 3 seconds for screen to stabilize...")
        time.sleep(3)
        
        # Device Panel window is typically 1000x1100, centered on screen
        # Menu bar is at the top
        # Tools menu is typically around x=100-150, y=20-30
        
        print("\n1. Clicking on 'Tools' menu...")
        # Click Tools menu (approximate location - may need adjustment)
        client.click(120, 25)
        time.sleep(2)  # Wait for menu to open
        
        print("2. Clicking 'Show App Suggestions...' menu item...")
        # Click menu item (below menu bar, typically around y=60-80)
        client.click(150, 70)
        time.sleep(3)  # Wait for dialog to open
        
        print("3. Waiting for suggestions dialog to load...")
        time.sleep(2)
        
        print("\n✓ Automation complete!")
        print("The suggestions dialog should now be open.")
        print("You can interact with it manually or close it.")
        
        # Keep connection open for a bit so user can see
        print("\nKeeping connection open for 5 seconds...")
        time.sleep(5)
        
        client.disconnect()
        print("✓ Disconnected from VNC")
        
    except Exception as e:
        print(f"\n✗ Error during automation: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    print("\nBefore running this script:")
    print("1. Make sure VNC server is running on Pi")
    print("2. Launch the VNC viewer: ./scripts/watch_pi_vnc.sh")
    print("3. Make sure Device Panel app is running on Pi")
    print("4. Then run this script\n")
    
    input("Press Enter when ready to start automation...")
    automate_gui()


