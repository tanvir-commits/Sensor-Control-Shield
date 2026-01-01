# Better Automation Approaches

## Problem with GUI Automation (xdotool)
- ❌ Coordinate guessing
- ❌ VNC refresh issues
- ❌ Fragile and unreliable
- ❌ Hard to debug

## Better Approaches

### 1. Programmatic API (Recommended) ✅
Call functions directly instead of clicking:

```python
# On the Pi (where environment is set up)
from features.smart_suggestions.ui.suggestions_dialog import SuggestionsDialog
from hardware.hardware import Hardware

hardware = Hardware()
dialog = SuggestionsDialog(hardware)
dialog.scan_devices()
dialog.launch_app("TiltGameApp", devices)
```

**Usage:**
```bash
# SSH to Pi and run
ssh a@192.168.101 "cd ~/DeviceOps && python3 -c '
from features.smart_suggestions.ui.suggestions_dialog import SuggestionsDialog
from hardware.hardware import Hardware
hardware = Hardware()
dialog = SuggestionsDialog(hardware)
dialog.scan_devices()
# Get first suggestion and launch it
suggestions = dialog.engine.generate_suggestions(dialog.detector.scan_all_devices(hardware))
if suggestions:
    devices = dialog.detector.scan_all_devices(hardware)
    dialog.launch_app(suggestions[0].app_class, devices)
'"
```

### 2. Qt QTest Framework (For GUI Testing)
Proper way to test Qt applications:

```python
from PySide6.QtTest import QTest
from PySide6.QtCore import Qt

# Find widget by object name
button = dialog.findChild(QPushButton, "launchButton")
QTest.mouseClick(button, Qt.LeftButton)
```

### 3. Command-Line Interface
Add CLI flags to the main app:

```bash
python3 device_panel.py --launch-app tilt-game
python3 device_panel.py --list-suggestions
```

### 4. REST API / Web Interface
Expose app control via HTTP API for remote control.

## Recommendation

**Use the Programmatic API** - it's:
- ✅ Reliable
- ✅ Fast
- ✅ Easy to debug
- ✅ Works in tests
- ✅ No GUI dependencies


