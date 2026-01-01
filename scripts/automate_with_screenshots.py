#!/usr/bin/env python3
"""Enhanced automation script with screenshot capability."""

import subprocess
import time
import os
from pathlib import Path

PI_HOST = 'a@192.168.101'
DISPLAY = ':1'
SCREENSHOT_DIR = Path('/tmp/vnc_automation_screenshots')
SCREENSHOT_DIR.mkdir(exist_ok=True)

def take_screenshot(name):
    """Take a screenshot and download it."""
    timestamp = time.strftime("%H%M%S")
    filename = f"{name}_{timestamp}.png"
    local_path = SCREENSHOT_DIR / filename
    
    print(f"📸 Taking screenshot: {name}...")
    
    # Take screenshot on Pi
    result = subprocess.run(
        f'ssh {PI_HOST} "export DISPLAY={DISPLAY} && import -window root /tmp/vnc_screenshot.png"',
        shell=True, capture_output=True, text=True
    )
    
    if result.returncode != 0:
        print(f"  ✗ Failed: {result.stderr}")
        return None
    
    # Download screenshot
    result = subprocess.run(
        f'scp {PI_HOST}:/tmp/vnc_screenshot.png {local_path}',
        shell=True, capture_output=True, text=True
    )
    
    if result.returncode == 0:
        print(f"  ✓ Saved to: {local_path}")
        return str(local_path)
    else:
        print(f"  ✗ Download failed: {result.stderr}")
        return None

def run_command(cmd, description):
    """Run a command and optionally take screenshot."""
    print(f"\n🔧 {description}")
    print(f"   Command: {cmd}")
    
    result = subprocess.run(
        f'ssh {PI_HOST} "export DISPLAY={DISPLAY} && {cmd}"',
        shell=True, capture_output=True, text=True
    )
    
    if result.returncode == 0:
        print(f"   ✓ Success")
        if result.stdout.strip():
            print(f"   Output: {result.stdout.strip()}")
    else:
        print(f"   ✗ Failed: {result.stderr}")
    
    return result.returncode == 0

def find_dialog():
    """Find the App Suggestions dialog."""
    result = subprocess.run(
        f'ssh {PI_HOST} "export DISPLAY={DISPLAY} && xdotool search --all --name \'App Suggestions\' | head -1"',
        shell=True, capture_output=True, text=True
    )
    
    if result.returncode == 0 and result.stdout.strip():
        return result.stdout.strip()
    return None

def main():
    print("=" * 60)
    print("VNC Automation with Screenshots")
    print("=" * 60)
    
    # Take initial screenshot
    take_screenshot("01_initial_state")
    
    # Find dialog
    print("\n🔍 Finding App Suggestions dialog...")
    dialog_id = find_dialog()
    
    if not dialog_id:
        print("✗ Dialog not found. Please open it manually.")
        return
    
    print(f"✓ Found dialog: {dialog_id}")
    take_screenshot("02_dialog_found")
    
    # Activate dialog
    run_command(f"xdotool windowactivate {dialog_id}", "Activating dialog")
    time.sleep(0.5)
    take_screenshot("03_dialog_activated")
    
    # Click Launch button
    print("\n🎮 Clicking Launch button for Tilt Game...")
    run_command(
        f"xdotool windowactivate {dialog_id} && xdotool mousemove --window {dialog_id} 700 180 && sleep 0.5 && xdotool click 1",
        "Clicking Launch button"
    )
    time.sleep(2)
    take_screenshot("04_after_launch_click")
    
    # Check if game started
    result = subprocess.run(
        f'ssh {PI_HOST} "ps aux | grep -i \'tilt\|game\' | grep python | grep -v grep"',
        shell=True, capture_output=True, text=True
    )
    
    if result.stdout.strip():
        print("\n✓ Tilt Game appears to be running!")
        take_screenshot("05_game_running")
    else:
        print("\n? Game process not found - may have started differently")
    
    print("\n" + "=" * 60)
    print("Automation complete! Check screenshots in:")
    print(f"  {SCREENSHOT_DIR}")
    print("=" * 60)

if __name__ == '__main__':
    main()


