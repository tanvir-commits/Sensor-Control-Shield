# SD Card Testing Guide

## Prerequisites

1. **Hardware Setup:**
   - STM32 NUCLEO-U545RE-Q board powered
   - USB-UART adapter connected to PC0 (RX) and PC1 (TX)
   - SD card shield connected:
     - PB12 → CS
     - PB13 → SCK  
     - PB14 → MISO
     - PB15 → MOSI
     - 3.3V → VCC
     - GND → GND

2. **Firmware:**
   - New firmware with SD card support must be flashed
   - Build: `cd firmware/stm32_nucleo_u545_lcd_sd && make`
   - Flash: `make flash` (or use STM32CubeProgrammer)

## Quick Test

Run the automated test script:

```bash
cd firmware/stm32_nucleo_u545_lcd_sd
python3 test_sd_card.py [port] [baud_rate]
```

Example:
```bash
python3 test_sd_card.py /dev/ttyUSB2 115200
```

## Manual Testing

### 1. Connect via Serial Terminal

```bash
screen /dev/ttyUSB2 115200
# or
minicom -D /dev/ttyUSB2 -b 115200
```

### 2. Test Commands

Send these commands (press Enter after each):

```
TASK 1
```
**Expected:** `OK LED blinked 3 times`

```
TASK 2
```
**Expected:** `OK SysClk: 4 MHz, HCLK: 4 MHz, VScale: Scale4`

```
TASK 6
```
**Expected:** `OK SD card initialized: Initialized`
**OR:** `ERR SD card init failed: [error message]`

```
TASK 7
```
**Expected:** `OK Block 0 read OK, first bytes: [hex data]`
**OR:** `ERR SD card not initialized`

```
TASK 8
```
**Expected:** `OK Block 0 written`
**OR:** `ERR SD card not initialized`

### 3. Verify Write

After `TASK 8`, run `TASK 7` again. The first bytes should show the test pattern:
- Expected: `000102030405060708090A0B0C0D0E0F` (incremental pattern)

## Expected Results

### Success Case

```
TASK 6
OK SD card initialized: Initialized

TASK 7
OK Block 0 read OK, first bytes: [some hex data]

TASK 8
OK Block 0 written

TASK 7
OK Block 0 read OK, first bytes: 000102030405060708090A0B0C0D0E0F
```

### Failure Cases

**SD Card Not Connected:**
```
TASK 6
ERR SD card init failed: CMD0 failed
```

**SD Card Not Initialized:**
```
TASK 7
ERR SD card not initialized
```

**Old Firmware:**
```
TASK 6
ERR Task not registered
```

## Troubleshooting

### Board Not Responding

1. Check power - LED should be blinking
2. Check UART wiring (PC0/PC1)
3. Check baud rate (115200)
4. Try power cycling the board

### SD Card Not Initializing

1. **Check Connections:**
   - Verify all 6 wires are connected correctly
   - Check for loose connections
   - Verify 3.3V power (not 5V)

2. **Check SD Card:**
   - Try a different SD card
   - Ensure card is formatted (FAT32)
   - Check card capacity (should work with most sizes)

3. **Check SPI:**
   - Verify SPI pins are correct (PB12/13/14/15)
   - Check for pin conflicts

### Task Not Registered

- Firmware not flashed or wrong firmware
- Flash new firmware: `make flash`

## Code Verification

The SD card implementation includes:

- ✓ SPI2 configuration (PB13/14/15)
- ✓ SD card CS pin (PB12)
- ✓ SD card initialization sequence (CMD0, CMD8, ACMD41)
- ✓ Block read/write functions (512 bytes)
- ✓ QA Agent tasks (6, 7, 8)
- ✓ Error handling and status messages

All code is implemented and ready for testing once firmware is flashed and hardware is connected.

