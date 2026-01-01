# Qt Automation Best Practices

## Current Issues
- Buttons are created inline with lambda functions
- Hard to find buttons programmatically
- No way to trigger actions without clicking

## Best Practices

### 1. Use QAction for All Interactive Elements ✅
**Why:**
- Actions can be triggered programmatically: `action.trigger()`
- Reusable across menus, toolbars, buttons
- Can be enabled/disabled centrally
- Supports keyboard shortcuts
- Works with Qt's accessibility framework

**Example:**
```python
# Create action
launch_action = QAction("Launch", self)
launch_action.setObjectName("launch_tilt_game_action")
launch_action.triggered.connect(lambda: self.launch_app("TiltGameApp", devices))

# Use in button
launch_button = QPushButton()
launch_button.setDefaultAction(launch_action)  # Button uses action

# Trigger programmatically
launch_action.trigger()  # Works from anywhere!
```

### 2. Object Names for All Widgets ✅
- Already implemented
- Use consistent naming: `{widget_type}_{purpose}_{identifier}`

### 3. Public API Methods ✅
- Already have `launch_app()` method
- Keep UI and logic separate
- Methods should be callable without UI

### 4. Qt Test Framework
```python
from PySide6.QtTest import QTest
button = dialog.findChild(QPushButton, "launch_button_TiltGameApp")
QTest.mouseClick(button, Qt.LeftButton)
```

### 5. Accessibility Support
- Set accessible names: `button.setAccessibleName("Launch Tilt Game")`
- Use roles: `button.setAccessibleRole(QAccessible.Button)`

## Recommended Architecture

### Option A: QAction-Based (Best for Automation)
```python
class SuggestionsDialog(QDialog):
    def __init__(self, hardware, parent=None):
        # ...
        self.launch_actions = {}  # Store actions
    
    def _create_suggestion_widget(self, suggestion, devices):
        # Create action
        action = QAction("Launch", self)
        action.setObjectName(f"launch_{suggestion.app_class}_action")
        action.triggered.connect(lambda: self.launch_app(suggestion.app_class, devices))
        self.launch_actions[suggestion.app_class] = action
        
        # Use in button
        button = QPushButton()
        button.setDefaultAction(action)
```

**Benefits:**
- `action.trigger()` works programmatically
- Can find by object name: `dialog.findChild(QAction, "launch_TiltGameApp_action")`
- Reusable in menus/toolbars

### Option B: Keep Current + Add Trigger Methods
```python
def trigger_launch(self, app_class_name: str):
    """Programmatically trigger launch for an app."""
    devices = self.detector.scan_all_devices(self.hardware)
    self.launch_app(app_class_name, devices)
```

**Benefits:**
- Minimal changes
- Direct method call
- Works immediately

## Recommendation

**Use QAction-based architecture** because:
1. ✅ Qt best practice
2. ✅ Works with Qt Test Framework
3. ✅ Supports accessibility
4. ✅ Can trigger programmatically
5. ✅ Reusable across UI
6. ✅ Future-proof

