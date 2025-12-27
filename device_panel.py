#!/usr/bin/env python3
"""Device Panel - Main entry point.

A GUI application for monitoring and controlling hardware interfaces
on a Raspberry Pi expansion board.
"""

import sys
from PySide6.QtWidgets import QApplication

from ui.main_window import MainWindow
from mock.mock_hardware import MockHardware


def main():
    """Main application entry point."""
    try:
        # Create Qt application
        app = QApplication(sys.argv)
        app.setApplicationName("Device Panel")
        
        # Create mock hardware for UI design
        mock_hw = MockHardware()
        
        # Create and show main window
        window = MainWindow(mock_hardware=mock_hw)
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

