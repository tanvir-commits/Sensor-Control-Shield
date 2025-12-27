# Setup Instructions

## Quick Start

### 1. Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Test GUI (No Display Needed)

```bash
python3 test_gui.py
```

This runs the GUI in "offscreen" mode to verify everything works without needing a display.

### 4. Launch GUI (Requires Display)

On a machine with a display (Raspberry Pi with monitor):

```bash
python3 device_panel.py
```

Or use the launch script:
```bash
./run_gui.sh
```

## Troubleshooting

### Missing X11 Libraries

If you get an error about `xcb-cursor0` or `libxcb-cursor0`, install it:

```bash
sudo apt-get update
sudo apt-get install libxcb-cursor0
```

Or on some systems:
```bash
sudo apt-get install libxcb-cursor-dev
```

### Virtual Display (For Testing Without Monitor)

If you want to test the GUI without a physical monitor, you can use Xvfb:

```bash
sudo apt-get install xvfb
Xvfb :99 -screen 0 1024x768x24 &
export DISPLAY=:99
python3 device_panel.py
```

## Current Status

✅ **GUI is fully functional and tested**
- All UI components work
- Mock hardware provides realistic data
- 10Hz update rate implemented
- Ready for UI design iteration

The GUI has been tested and verified to work correctly. You can now:
1. Launch it on a Raspberry Pi with a monitor
2. Iterate on the UI design (colors, spacing, layout)
3. Once satisfied, we'll replace mock hardware with real hardware

