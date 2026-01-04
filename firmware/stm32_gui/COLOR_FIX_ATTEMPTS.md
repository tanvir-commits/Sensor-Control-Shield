# ST7789 Color Fix Attempts

## Issue
Colors are displayed incorrectly on the ST7789 display with SquareLine Studio UI.

## Changes Made

### 1. ST7789 Pixel Format
- **Changed**: COLMOD from 0x05 (RGB666) to 0x55 (RGB565)
- **Location**: `src/system/st7789_driver.c` line 271
- **Reason**: LVGL uses RGB565, so display should match

### 2. Byte Swapping
- **Current**: Removed manual byte swap in flush callback
- **Location**: `src/lvgl_port.c` 
- **Reason**: With `LV_COLOR_16_SWAP = 1`, LVGL already swaps bytes internally

### 3. LVGL Configuration
- **Current**: `LV_COLOR_16_SWAP = 1` in `lvgl/lv_conf.h`
- **Current**: `LV_COLOR_DEPTH = 16` (RGB565)

## Next Steps to Try

If colors are still wrong, try these in order:

### Option 1: Disable LV_COLOR_16_SWAP
```c
// In lvgl/lv_conf.h
#define LV_COLOR_16_SWAP 0
```
Then rebuild and test. If this fixes it, the display expects bytes in the order LVGL provides without swapping.

### Option 2: Re-enable Byte Swap in Flush Callback
If Option 1 doesn't work, the display might need bytes swapped even with LV_COLOR_16_SWAP=1.
Add back the byte swap in `src/lvgl_port.c` flush callback.

### Option 3: Check ST7789 COLMOD Setting
Some ST7789 variants might need 0x05 (RGB666) instead of 0x55 (RGB565).
Try reverting the COLMOD change if other options don't work.

## Resources Found
- SquareLine Studio board packages: https://github.com/yashmulgaonkar/SquareLineStudio_boardpackages
- ST7789 STM32 drivers: https://github.com/deividAlfa/ST7789-STM32-uGUI
- SquareLine Studio minimum requirement: https://github.com/PetitOursManu/SquareLine_Studio_Minimum_Requirement

## Current Status
- ST7789 set to RGB565 (0x55) ✓
- Byte swap removed from flush callback ✓
- LV_COLOR_16_SWAP = 1 ✓
- **Test this configuration first**



