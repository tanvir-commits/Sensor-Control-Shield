#!/usr/bin/env python3
"""Launch app by calling dialog method directly - best approach!"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PySide6.QtWidgets import QApplication
from features.smart_suggestions.ui.suggestions_dialog import SuggestionsDialog

# Import Hardware class (same way device_panel.py does it)
import sys
import os
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)

from device_panel import Hardware

def launch_app_via_dialog_api(app_class_name="TiltGameApp"):
    """Launch app by directly calling dialog methods - no clicking needed!"""
    app = QApplication.instance()
    if app is None:
        print("❌ No QApplication found. Creating one...")
        app = QApplication(sys.argv)
    
    print(f"🚀 Launching {app_class_name} via dialog API...")
    
    # Create hardware and dialog (same as GUI does)
    hardware = Hardware()
    dialog = SuggestionsDialog(hardware)
    
    # Scan for devices
    dialog.scan_devices()
    
    # Get devices needed for the app
    devices = dialog.detector.scan_all_devices(hardware=hardware)
    
    # Filter by category
    if app_class_name == "TiltGameApp":
        required = ["IMU", "DISPLAY"]
    elif app_class_name == "LevelApp":
        required = ["IMU", "DISPLAY"]
    else:
        print(f"❌ Unknown app: {app_class_name}")
        return False
    
    app_devices = [d for d in devices if d.category in required]
    
    if len(app_devices) < len(required):
        print(f"❌ Missing devices. Need: {required}, Found: {[d.category for d in app_devices]}")
        return False
    
    # Call launch_app directly - no clicking needed!
    print(f"✓ Calling dialog.launch_app('{app_class_name}', devices)...")
    dialog.launch_app(app_class_name, app_devices)
    
    print(f"✅ {app_class_name} launched!")
    print("   App is running. The ball should be visible on the LCD!")
    
    return True

if __name__ == '__main__':
    app_class = sys.argv[1] if len(sys.argv) > 1 else "TiltGameApp"
    success = launch_app_via_dialog_api(app_class)
    sys.exit(0 if success else 1)

