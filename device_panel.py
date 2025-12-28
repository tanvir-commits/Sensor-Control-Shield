#!/usr/bin/env python3
"""Device Panel - Main entry point.

A GUI application for monitoring and controlling hardware interfaces
on a Raspberry Pi expansion board.
"""

import sys
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


def main():
    """Main application entry point."""
    try:
        # Create Qt application
        app = QApplication(sys.argv)
        app.setApplicationName("Device Panel")
        
        # Create hardware managers
        hardware = Hardware()
        
        # Create and show main window
        window = MainWindow(mock_hardware=hardware)
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
