# UART Button Simulation

## Overview

The firmware now supports button simulation via UART commands. This allows testing the GUI without physical buttons connected.

## Command Format

Commands are sent over LPUART1 (115200 baud) in the format:
```
BTN:<BUTTON>:<ACTION>\n
```

Where:
- `<BUTTON>` is one of: `UP`, `DOWN`, `LEFT`, `RIGHT`, `PLAY`
- `<ACTION>` is either: `PRESS` or `RELEASE`

## Examples

Press UP button:
```
BTN:UP:PRESS
```

Release UP button:
```
BTN:UP:RELEASE
```

Press PLAY button:
```
BTN:PLAY:PRESS
```

## Using the Test Tool

A Python GUI test tool is available at `tools/gui_test_tool.py`:

```bash
python3 tools/gui_test_tool.py
```

The tool provides:
- **Connection tab**: Select serial port and connect
- **Inputs tab**: Visual button layout with 5 buttons:
  - UP, DOWN, LEFT, RIGHT buttons on the sides
  - PLAY button in the center
- **Log**: Shows sent commands and connection status

## Button Layout

```
        [UP]
        
[LEFT]  [PLAY]  [RIGHT]
        
        [DOWN]
```

## Integration

The button driver automatically handles UART-simulated buttons. When a button is simulated:
- Physical GPIO reading is bypassed
- Button state is set directly from UART command
- Works seamlessly with existing LVGL input handling

## Notes

- UART simulation takes priority over GPIO reading
- Commands must end with newline (`\n`)
- Maximum command length: 32 bytes
- Button state persists until RELEASE command is sent



