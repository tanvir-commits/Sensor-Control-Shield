#!/usr/bin/env python3
"""Click Launch button using QAction - Qt best practice!"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QAction

def trigger_launch_via_action(app_class_name="TiltGameApp"):
    """Trigger launch using QAction - the proper Qt way!"""
    app = QApplication.instance()
    if app is None:
        print("❌ No QApplication found. Make sure Device Panel GUI is running.")
        return False
    
    print(f"🔍 Looking for launch action: launch_{app_class_name}_action...")
    
    # Find all widgets
    all_widgets = app.allWidgets()
    dialog = None
    
    for widget in all_widgets:
        if hasattr(widget, 'windowTitle') and "App Suggestions" in widget.windowTitle():
            dialog = widget
            print(f"✓ Found dialog: {widget.windowTitle()}")
            break
    
    if not dialog:
        print("❌ App Suggestions dialog not found")
        print("   Please open Tools → Show App Suggestions...")
        return False
    
    # Find action by object name
    action_name = f"launch_{app_class_name}_action"
    action = dialog.findChild(QAction, action_name)
    
    if not action:
        print(f"❌ Action '{action_name}' not found")
        # List all actions for debugging
        actions = dialog.findChildren(QAction)
        print(f"   Found {len(actions)} actions:")
        for act in actions:
            print(f"     - '{act.text()}' (objectName: {act.objectName()})")
        return False
    
    print(f"✓ Found action: '{action.text()}' (objectName: {action.objectName()})")
    
    # Trigger the action programmatically
    print("🚀 Triggering launch action...")
    action.trigger()
    print("✅ Launch action triggered!")
    
    return True

if __name__ == '__main__':
    app_class = sys.argv[1] if len(sys.argv) > 1 else "TiltGameApp"
    success = trigger_launch_via_action(app_class)
    sys.exit(0 if success else 1)


