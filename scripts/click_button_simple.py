#!/usr/bin/env python3
"""Simple script to click Launch button - run this while Device Panel is open."""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PySide6.QtWidgets import QApplication, QPushButton

def click_launch_button():
    """Find the dialog and click the Launch button."""
    app = QApplication.instance()
    if not app:
        print("❌ No QApplication found. Make sure Device Panel GUI is running.")
        print("   Run this script on the Pi where Device Panel is running.")
        return False
    
    print("🔍 Looking for App Suggestions dialog...")
    
    # Find dialog by window title
    dialog = None
    for widget in app.allWidgets():
        if hasattr(widget, 'windowTitle'):
            title = widget.windowTitle()
            if "App Suggestions" in title or "Suggestions" in title:
                dialog = widget
                print(f"✓ Found dialog: '{title}'")
                break
    
    if not dialog:
        print("❌ Dialog not found.")
        print("   Please open: Tools → Show App Suggestions...")
        print("\n   Available windows:")
        for widget in app.allWidgets():
            if hasattr(widget, 'windowTitle'):
                print(f"     - {widget.windowTitle()}")
        return False
    
    # Find Launch button
    print("🔍 Looking for Launch button...")
    button = dialog.findChild(QPushButton, "launch_button_TiltGameApp")
    
    if not button:
        # Try finding by text
        buttons = dialog.findChildren(QPushButton)
        for btn in buttons:
            if btn.text() == "Launch":
                button = btn
                print(f"✓ Found Launch button by text")
                break
    
    if not button:
        print("❌ Launch button not found.")
        buttons = dialog.findChildren(QPushButton)
        print(f"   Found {len(buttons)} buttons:")
        for btn in buttons:
            print(f"     - '{btn.text()}' (objectName: {btn.objectName()})")
        return False
    
    print(f"✓ Found Launch button: '{button.text()}'")
    print("🖱️  Clicking button...")
    
    # THE SIMPLE SOLUTION: Just call click()!
    button.click()
    
    print("✅ Button clicked! The Tilt Game should launch now.")
    return True

if __name__ == '__main__':
    success = click_launch_button()
    sys.exit(0 if success else 1)


