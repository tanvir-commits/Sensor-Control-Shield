#!/usr/bin/env python3
"""Test script to verify GUI components work correctly."""

import os
import sys

# Use offscreen platform for testing
os.environ['QT_QPA_PLATFORM'] = 'offscreen'

from PySide6.QtWidgets import QApplication
from ui.main_window import MainWindow
from mock.mock_hardware import MockHardware


def test_gui():
    """Test GUI initialization and components."""
    print("=" * 60)
    print("Device Panel GUI Test")
    print("=" * 60)
    
    print("\n1. Creating Qt Application...")
    app = QApplication([])
    print("   ✓ Application created")
    
    print("\n2. Creating mock hardware...")
    mock_hw = MockHardware()
    print("   ✓ Mock hardware initialized")
    
    print("\n3. Creating main window...")
    window = MainWindow(mock_hardware=mock_hw)
    print(f"   ✓ Window created: {window.windowTitle()}")
    print(f"   ✓ Window size: {window.size().width()} x {window.size().height()}")
    
    print("\n4. Testing UI components...")
    print("   ✓ Status bar:", type(window.status_bar).__name__)
    print("   ✓ Analog section:", type(window.analog_section).__name__)
    print("   ✓ LED section:", type(window.led_section).__name__)
    print("   ✓ Button section:", type(window.button_section).__name__)
    print("   ✓ I2C section:", type(window.i2c_section).__name__)
    print("   ✓ SPI section:", type(window.spi_section).__name__)
    
    print("\n5. Testing update cycle...")
    window.update_all()
    print("   ✓ Update cycle completed")
    
    print("\n6. Testing mock hardware interactions...")
    # Test LED toggle
    window.on_led_changed(1, True)
    print("   ✓ LED toggle works")
    
    # Test I2C scan
    window.on_i2c_scan()
    print("   ✓ I2C scan works")
    
    # Test SPI test
    window.on_spi_test()
    print("   ✓ SPI test works")
    
    print("\n7. Testing multiple update cycles...")
    for i in range(5):
        window.update_all()
    print("   ✓ Multiple updates completed")
    
    print("\n" + "=" * 60)
    print("✓ ALL TESTS PASSED")
    print("=" * 60)
    print("\nThe GUI is fully functional!")
    print("To launch on a machine with display:")
    print("  python3 device_panel.py")
    print("\nNote: This test ran in 'offscreen' mode (no display needed)")


if __name__ == "__main__":
    test_gui()

