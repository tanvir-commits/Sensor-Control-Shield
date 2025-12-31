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


def main():
    """Main application entry point."""
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
