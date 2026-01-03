# LCD (ST7789) Implementation

## Overview

LCD driver for Waveshare 2-inch LCD module with ST7789V controller (240x320 pixels).

## Pin Configuration

Based on Arduino wiring diagram:

| LCD Pin | Signal | Arduino Pin | STM32 Pin | Notes |
|---------|--------|-------------|-----------|-------|
| VCC | Power | VCC | 3.3V | Power supply |
| GND | Ground | GND | GND | Ground |
| DIN | MOSI | D11 | PA7 | SPI1_MOSI |
| CLK | SCK | D13 | PA5 | SPI1_SCK |
| CS | Chip Select | D10 | **PC9** | ⚠️ **CONFLICTS with SD card CS!** |
| DC | Data/Command | D8 | **PA9** | Tentative - need to verify |
| RST | Reset | D7 | PA8 | Confirmed from user manual |
| BL | Backlight | D6 | PB10 | Confirmed from user manual |

## CS Pin Conflict

**CRITICAL ISSUE:** Both SD card and LCD use D10 (PC9) for Chip Select!

- SD card shield uses D10 (PC9) for CS
- LCD also uses D10 (PC9) for CS
- Both share SPI1 bus (PA5/PA6/PA7)
- **They cannot both use the same CS pin simultaneously**

### Solutions

1. **Use different CS pins** (recommended):
   - Keep SD card on PC9 (D10)
   - Use a different GPIO for LCD CS (e.g., PB0, PB1, or another available pin)
   - Requires modifying LCD wiring (use a different pin instead of D10)

2. **Use one device at a time**:
   - Only initialize/use SD card OR LCD at a time
   - Not practical for most applications

3. **Use separate SPI buses**:
   - Move one device to SPI2 or SPI3
   - Requires significant code changes

## Implementation Status

✅ **Completed:**
- LCD driver header (`st7789.h`)
- LCD driver implementation (`st7789.c`)
- GPIO configuration for LCD pins
- LCD initialization in `main()`
- QA Agent tasks:
  - TASK 9: LCD Initialize
  - TASK 10: LCD Test (draws test patterns)

⚠️ **Needs Verification:**
- D8 (DC pin) mapping - currently set to PA9, needs verification from user manual
- CS pin conflict resolution

## QA Agent Tasks

- **TASK 9**: `task_9_lcd_init()` - Re-initializes the LCD
- **TASK 10**: `task_10_lcd_test()` - Draws test patterns (red, green, blue, white fills + colored rectangles)

## Usage

```c
// Initialize LCD
ST7789_Init();

// Fill screen with color
ST7789_FillScreen(COLOR_RED);

// Draw rectangle
ST7789_DrawRect(10, 10, 100, 50, COLOR_GREEN);

// Set backlight
ST7789_SetBacklight(true);

// Set rotation
ST7789_SetRotation(0); // 0, 1, 2, or 3
```

## Next Steps

1. **Verify D8 pin mapping** - Check user manual for actual D8 → GPIO mapping
2. **Resolve CS conflict** - Choose solution (different CS pin, separate SPI, or one-at-a-time)
3. **Test LCD** - Flash firmware and test with TASK 9 and TASK 10
4. **Add font support** - Implement proper character rendering (currently placeholder)

## Notes

- LCD shares SPI1 with SD card (PA5/PA6/PA7)
- LCD uses software CS (not hardware NSS)
- Backlight control is optional but recommended
- Display supports 16-bit color (RGB565 format)

