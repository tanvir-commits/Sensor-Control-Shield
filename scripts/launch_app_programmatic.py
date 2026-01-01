#!/usr/bin/env python3
"""Programmatic API to launch apps without GUI automation.

This is much better than clicking coordinates - we call the functions directly!
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from features.smart_suggestions.device_detector import DeviceDetector
from features.smart_suggestions.suggestion_engine import SuggestionEngine
from features.smart_suggestions.apps.tilt_game import TiltGameApp
from features.smart_suggestions.apps.level_app import LevelApp
from hardware.hardware import Hardware


def launch_app_programmatically(app_name: str):
    """Launch an app programmatically without GUI."""
    print(f"🚀 Launching {app_name} programmatically...")
    
    # Initialize hardware
    hardware = Hardware()
    
    # Scan for devices
    detector = DeviceDetector()
    devices = detector.scan_all_devices(hardware=hardware)
    
    print(f"📱 Detected {len(devices)} devices:")
    for device in devices:
        print(f"   - {device.name} (0x{device.address:02X}) - {device.category}")
    
    # Find devices needed for the app
    if app_name.lower() in ["tilt game", "tiltgame", "tilt"]:
        app_class = TiltGameApp
        required_categories = ["IMU", "DISPLAY"]
    elif app_name.lower() in ["level", "digital level"]:
        app_class = LevelApp
        required_categories = ["IMU", "DISPLAY"]
    else:
        print(f"❌ Unknown app: {app_name}")
        return False
    
    # Filter devices by category
    app_devices = [d for d in devices if d.category in required_categories]
    
    if len(app_devices) < len(required_categories):
        print(f"❌ Missing required devices. Need: {required_categories}")
        print(f"   Found: {[d.category for d in app_devices]}")
        return False
    
    # Create and start app
    app = app_class()
    if app.start(hardware, app_devices):
        print(f"✅ {app_name} launched successfully!")
        print(f"   App is running. Press Ctrl+C to stop.")
        
        try:
            # Keep running
            import time
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n🛑 Stopping app...")
            app.stop()
            print("✅ App stopped.")
            return True
    else:
        print(f"❌ Failed to launch {app_name}")
        return False


def list_suggestions():
    """List available app suggestions based on detected devices."""
    print("🔍 Scanning for devices and generating suggestions...")
    
    hardware = Hardware()
    detector = DeviceDetector()
    engine = SuggestionEngine()
    
    devices = detector.scan_all_devices(hardware=hardware)
    suggestions = engine.generate_suggestions(devices)
    
    print(f"\n📱 Detected {len(devices)} devices:")
    for device in devices:
        print(f"   - {device.name} (0x{device.address:02X}) - {device.category}")
    
    print(f"\n💡 Found {len(suggestions)} suggestions:")
    for i, suggestion in enumerate(suggestions, 1):
        print(f"\n{i}. {suggestion.app_name}")
        print(f"   Description: {suggestion.description}")
        print(f"   Requires: {', '.join(suggestion.required_devices)}")
        print(f"   App class: {suggestion.app_class}")
    
    return suggestions


if __name__ == '__main__':
    if len(sys.argv) > 1:
        app_name = sys.argv[1]
        launch_app_programmatically(app_name)
    else:
        print("Usage:")
        print("  python3 scripts/launch_app_programmatic.py <app_name>")
        print("\nAvailable apps:")
        print("  - tilt-game (or tilt)")
        print("  - digital-level (or level)")
        print("\nOr run without arguments to see suggestions:")
        suggestions = list_suggestions()


