# Task Testing Guide

## Expected Task Responses

### TASK 1: LED Blink
- **Command**: `TASK 1`
- **Expected Response**: `OK LED blinked 3 times, now ON`
- **Behavior**: Blinks LED (PA5) 3 times, then keeps it ON

### TASK 2: LCD OFF
- **Command**: `TASK 2`
- **Expected Response**: `OK LCD off`
- **Behavior**: Turns off LCD backlight and puts display in sleep mode

### TASK 3: LCD ON
- **Command**: `TASK 3`
- **Expected Response**: `OK LCD on`
- **Behavior**: Wakes LCD display and turns on backlight to 100%

### TASK 4: LCD Toggle (Bitmap Gallery)
- **Command**: `TASK 4`
- **Expected Response**: 
  - First call: `OK Gallery: 3 bitmaps, showing 1` (switches to gallery mode)
  - Second call: `OK Normal GUI mode` (switches back to normal mode)
- **Behavior**: Toggles between normal GUI mode and bitmap gallery mode

## Testing

Run the test script:
```bash
python3 test_tasks.py
```

Or manually test with:
```bash
# Using screen or minicom
screen /dev/ttyACM0 115200

# Then send commands:
TASK 1
TASK 2
TASK 3
TASK 4
```

## Troubleshooting

If tasks don't respond:
1. **Reset the board** after flashing
2. **Check UART connection** - ensure cable is connected
3. **Verify correct port** - try `/dev/ttyACM0` or `/dev/ttyUSB0`
4. **Check heartbeat** - board should send `HEARTBEAT` messages every 2 seconds
5. **Verify firmware** - ensure latest firmware is flashed

## Known Issues

- Task 1 tries to blink LED on PA5, which was set to LOW for power measurement. This should still work (it toggles the pin).
- If no heartbeat messages are received, the board may not be running or UART is not initialized.

