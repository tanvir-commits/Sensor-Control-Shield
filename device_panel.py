#!/usr/bin/env python3
"""Device Panel - Main entry point.

A GUI application for monitoring and controlling hardware interfaces
on a Raspberry Pi expansion board.
"""

import sys
import os
import subprocess
from pathlib import Path
from PySide6.QtWidgets import QApplication

from ui.main_window import MainWindow
from hardware.gpio_manager import GPIOManager
from hardware.adc_manager import ADCManager
from hardware.i2c_scanner import I2CScanner
from hardware.spi_tester import SPITester
from hardware.power_manager import PowerManager
from config.pins import I2C_BUS


class Hardware:
    """Container for all hardware managers."""
    
    def __init__(self):
        self.gpio = GPIOManager()
        self.adc = ADCManager()
        self.i2c = I2CScanner(bus=I2C_BUS)
        self.spi = SPITester()
        self.power = PowerManager()


def get_git_branch():
    """Get current git branch name.
    
    Returns:
        str: Branch name (e.g., 'main', 'dev', 'feature/power-profiler')
             Returns 'unknown' if git is not available or not in a git repo.
    """
    try:
        # Get the directory containing this script
        script_dir = Path(__file__).parent.absolute()
        
        # Try to get branch name
        result = subprocess.run(
            ['git', 'rev-parse', '--abbrev-ref', 'HEAD'],
            cwd=script_dir,
            capture_output=True,
            text=True,
            timeout=2
        )
        
        if result.returncode == 0:
            branch = result.stdout.strip()
            return branch if branch else 'unknown'
        else:
            return 'unknown'
    except (subprocess.TimeoutExpired, FileNotFoundError, Exception):
        # Git not available, not in git repo, or other error
        return 'unknown'


def launch_app_cli(app_name: str):
    """Launch an app via CLI without GUI."""
    try:
        from features.smart_suggestions.device_detector import DeviceDetector
        from features.smart_suggestions.suggestion_engine import SuggestionEngine
        from features.smart_suggestions.apps.tilt_game import TiltGameApp
        from features.smart_suggestions.apps.level_app import LevelApp
        
        print(f"🚀 Launching {app_name} programmatically...")
        
        # Initialize hardware
        hardware = Hardware()
        
        # Scan for devices
        detector = DeviceDetector()
        devices = detector.scan_all_devices(hardware=hardware)
        
        print(f"📱 Detected {len(devices)} devices:")
        for device in devices:
            device_name = getattr(device, 'name', f"Device 0x{device.address:02X}")
            print(f"   - {device_name} (0x{device.address:02X}) - {device.category}")
        
        # Map app name to class
        app_map = {
            "tilt-game": (TiltGameApp, ["IMU", "DISPLAY"]),
            "tilt": (TiltGameApp, ["IMU", "DISPLAY"]),
            "tiltgame": (TiltGameApp, ["IMU", "DISPLAY"]),
            "level": (LevelApp, ["IMU", "DISPLAY"]),
            "digital-level": (LevelApp, ["IMU", "DISPLAY"]),
        }
        
        app_name_lower = app_name.lower()
        if app_name_lower not in app_map:
            print(f"❌ Unknown app: {app_name}")
            print(f"   Available: {', '.join(app_map.keys())}")
            return 1
        
        app_class, required_categories = app_map[app_name_lower]
        
        # Filter devices by category
        app_devices = [d for d in devices if d.category in required_categories]
        
        if len(app_devices) < len(required_categories):
            print(f"❌ Missing required devices. Need: {required_categories}")
            print(f"   Found: {[d.category for d in app_devices]}")
            return 1
        
        # Create and start app
        app = app_class()
        if app.start(hardware, app_devices):
            print(f"✅ {app_name} launched successfully!")
            print(f"   App is running. Press Ctrl+C to stop.")
            
            try:
                import time
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                print("\n🛑 Stopping app...")
                app.stop()
                print("✅ App stopped.")
                return 0
        else:
            print(f"❌ Failed to launch {app_name}")
            return 1
    
    except Exception as e:
        import traceback
        print(f"Error launching app: {e}", file=sys.stderr)
        traceback.print_exc()
        return 1


def list_suggestions_cli():
    """List available app suggestions."""
    try:
        from features.smart_suggestions.device_detector import DeviceDetector
        from features.smart_suggestions.suggestion_engine import SuggestionEngine
        
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
            print(f"   Launch with: python3 device_panel.py --launch-app {suggestion.app_name.lower().replace(' ', '-')}")
        
        return 0
    
    except Exception as e:
        import traceback
        print(f"Error listing suggestions: {e}", file=sys.stderr)
        traceback.print_exc()
        return 1


def main():
    """Main application entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Device Panel - Hardware Control and Monitoring')
    parser.add_argument('--launch-app', type=str, help='Launch an app programmatically (e.g., tilt-game, level)')
    parser.add_argument('--list-suggestions', action='store_true', help='List available app suggestions')
    
    args = parser.parse_args()
    
    # Handle CLI modes
    if args.launch_app:
        return launch_app_cli(args.launch_app)
    elif args.list_suggestions:
        return list_suggestions_cli()
    
    # Default: Launch GUI
    try:
        # Get current git branch for display
        branch = get_git_branch()
        
        # Create Qt application
        app = QApplication(sys.argv)
        app_name = f"Device Panel [{branch}]"
        app.setApplicationName(app_name)
        
        # Create hardware managers
        hardware = Hardware()
        
        # Create and show main window (pass branch for display)
        window = MainWindow(mock_hardware=hardware, branch=branch)
        window.show()
        
        # Run application
        sys.exit(app.exec())
    except Exception as e:
        import traceback
        print(f"Error launching GUI: {e}", file=sys.stderr)
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
