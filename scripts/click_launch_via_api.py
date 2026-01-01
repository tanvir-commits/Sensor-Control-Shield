#!/usr/bin/env python3
"""Click Launch button using Qt API - proper way to automate Qt apps."""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PySide6.QtWidgets import QApplication, QPushButton
from PySide6.QtTest import QTest
from PySide6.QtCore import Qt

def click_launch_button(app_class_name="TiltGameApp"):
    """Find and click Launch button using Qt API."""
    app = QApplication.instance()
    if app is None:
        print("❌ No QApplication instance found. Make sure Device Panel GUI is running.")
        return False
    
    print(f"🔍 Looking for Launch button for {app_class_name}...")
    
    # Find all top-level widgets (dialogs)
    all_widgets = app.allWidgets()
    dialog = None
    
    for widget in all_widgets:
        # Check by window title
        if hasattr(widget, 'windowTitle'):
            if "App Suggestions" in widget.windowTitle():
                dialog = widget
                print(f"✓ Found dialog: {widget.windowTitle()}")
                break
    
    if not dialog:
        print("❌ App Suggestions dialog not found")
        print("   Please open Tools → Show App Suggestions...")
        return False
    
    # Find button by object name
    button_name = f"launch_button_{app_class_name}"
    button = dialog.findChild(QPushButton, button_name)
    
    if not button:
        print(f"❌ Button '{button_name}' not found")
        print("   Trying to find any Launch button...")
        # Try finding by text
        buttons = dialog.findChildren(QPushButton)
        for btn in buttons:
            if btn.text() == "Launch":
                button = btn
                print(f"✓ Found Launch button by text: {btn}")
                break
    
    if not button:
        print("❌ Launch button not found")
        # List all buttons for debugging
        buttons = dialog.findChildren(QPushButton)
        print(f"   Found {len(buttons)} buttons:")
        for btn in buttons:
            print(f"     - '{btn.text()}' (objectName: {btn.objectName()})")
        return False
    
    print(f"✓ Found Launch button: '{button.text()}' (objectName: {button.objectName()})")
    
    # Make sure button is visible and enabled
    if not button.isVisible():
        print("⚠️  Button is not visible")
    if not button.isEnabled():
        print("⚠️  Button is not enabled")
    
    # Click using Qt's test framework
    print("🖱️  Clicking Launch button...")
    QTest.mouseClick(button, Qt.LeftButton)
    print("✅ Launch button clicked!")
    
    return True

if __name__ == '__main__':
    app_class = sys.argv[1] if len(sys.argv) > 1 else "TiltGameApp"
    success = click_launch_button(app_class)
    sys.exit(0 if success else 1)

