#!/usr/bin/env python3
"""Click Launch button using Qt API instead of coordinates."""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PySide6.QtWidgets import QApplication
from PySide6.QtTest import QTest
from PySide6.QtCore import Qt

def find_and_click_launch_button(app_class_name="TiltGameApp"):
    """Find Launch button by object name and click it."""
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    
    # Find all dialogs
    dialogs = []
    for widget in app.allWidgets():
        if widget.objectName() == "App Suggestions" or "App Suggestions" in str(type(widget).__name__):
            dialogs.append(widget)
        # Also check by window title
        if hasattr(widget, 'windowTitle') and "App Suggestions" in widget.windowTitle():
            dialogs.append(widget)
    
    if not dialogs:
        print("❌ App Suggestions dialog not found")
        return False
    
    dialog = dialogs[0]
    print(f"✓ Found dialog: {dialog}")
    
    # Find Launch button by object name
    button_name = f"launch_button_{app_class_name}"
    button = dialog.findChild(type(dialog), button_name)
    
    if button is None:
        # Try finding by text
        for widget in dialog.findChildren(type(dialog)):
            if hasattr(widget, 'text') and widget.text() == "Launch":
                button = widget
                break
    
    if button is None:
        print(f"❌ Launch button not found (looking for: {button_name})")
        # List all buttons for debugging
        buttons = dialog.findChildren(type(dialog))
        print(f"   Found {len(buttons)} buttons total")
        return False
    
    print(f"✓ Found Launch button: {button}")
    
    # Click the button using Qt's test framework
    QTest.mouseClick(button, Qt.LeftButton)
    print("✓ Clicked Launch button!")
    
    return True

if __name__ == '__main__':
    app_class = sys.argv[1] if len(sys.argv) > 1 else "TiltGameApp"
    find_and_click_launch_button(app_class)


