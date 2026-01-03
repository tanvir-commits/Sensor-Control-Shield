# Bitmap GUI System

A clean, simple bitmap-based GUI system for the STM32 LCD display. Perfect for loading and testing bitmap images.

## Quick Start

### 1. Convert Your Images

Use the conversion script to convert PNG/JPG images to C arrays:

```bash
cd firmware/stm32_nucleo_u545_lcd_sd
./scripts/convert_bitmap.sh images/my_image.png my_bitmap
```

This creates:
- `src/gui_images_my_bitmap.c` - C source with image data
- `inc/gui_images_my_bitmap.h` - Header file

### 2. Add to Build System

Add the new C file to `Makefile`:

```makefile
src/gui_images_my_bitmap.c \
```

### 3. Include in Project

Add to `inc/gui_images.h`:

```c
#include "gui_images_my_bitmap.h"
```

### 4. Register Bitmap

In `src/syringe_gui.c`, add to `GUI_Init()`:

```c
BitmapGUI_RegisterBitmap(
    gImage_my_bitmap,
    GIMAGE_MY_BITMAP_WIDTH,
    GIMAGE_MY_BITMAP_HEIGHT,
    "My Bitmap"
);
```

### 5. Test Bitmap Gallery

Flash the firmware and use QA Agent task 15:

```python
from hardware.uart_manager import UARTManager

uart = UARTManager()
uart.open('/dev/ttyACM0', 115200)
uart.send_task(15)  # Enable bitmap gallery mode
```

Then press the button on the board to cycle through bitmaps!

## Features

- **Simple bitmap loading** - Just convert images and register them
- **Gallery mode** - Cycle through all registered bitmaps with button press
- **Automatic centering** - Bitmaps smaller than screen are centered
- **Clean display** - No overlays unless you enable them
- **Easy to extend** - Add new bitmaps in minutes

## Image Requirements

- **Format**: PNG or JPG
- **Size**: Will be auto-resized to 320x240 (landscape) or 240x320 (portrait)
- **Color**: RGB565 format (16-bit color)
- **Recommended**: Design at 320x240 for best results

## Usage

### Normal Mode (Default)
- Shows your application screens
- Button cycles through application screens

### Gallery Mode
- Shows only bitmaps
- Button cycles through registered bitmaps
- Enable with QA Agent task 15

### Switching Modes

**Via QA Agent:**
```python
uart.send_task(15)  # Toggle between normal and gallery mode
```

**In Code:**
```c
BitmapGUI_SetMode(BITMAP_MODE_GALLERY);  // Enable gallery
BitmapGUI_SetMode(BITMAP_MODE_NORMAL);    // Back to normal
```

## Example: Adding a Test Bitmap

1. Create or find a 320x240 PNG image
2. Convert it:
   ```bash
   ./scripts/convert_bitmap.sh test_image.png test
   ```
3. Add to Makefile (line 39):
   ```makefile
   src/gui_images_test.c \
   ```
4. Include in `inc/gui_images.h`:
   ```c
   #include "gui_images_test.h"
   ```
5. Register in `src/syringe_gui.c` in `GUI_Init()`:
   ```c
   BitmapGUI_RegisterBitmap(
       gImage_test,
       GIMAGE_TEST_WIDTH,
       GIMAGE_TEST_HEIGHT,
       "Test Image"
   );
   ```
6. Rebuild and flash:
   ```bash
   make clean && make && make flash
   ```
7. Test:
   ```python
   uart.send_task(15)  # Enable gallery mode
   # Press button to cycle through bitmaps
   ```

## API Reference

### BitmapGUI_Init()
Initialize the bitmap GUI system. Called automatically by `GUI_Init()`.

### BitmapGUI_RegisterBitmap(data, width, height, name)
Register a bitmap in the gallery.

### BitmapGUI_SetMode(mode)
Set GUI mode: `BITMAP_MODE_NORMAL` or `BITMAP_MODE_GALLERY`

### BitmapGUI_NextBitmap()
Switch to next bitmap (used by button handler)

### BitmapGUI_ShowCurrentBitmap()
Display the current bitmap

## Tips

- **Memory**: Each 320x240 bitmap uses ~150KB of flash memory
- **Performance**: Bitmaps are stored in flash, drawing is fast
- **Design**: Use GIMP or Inkscape to create 320x240 images
- **Testing**: Use gallery mode to quickly test all your bitmaps

## Troubleshooting

**Bitmap doesn't appear:**
- Check it's registered in `GUI_Init()`
- Verify image was converted correctly
- Check Makefile includes the .c file

**Wrong size:**
- Images are auto-resized to 320x240
- Design at exact size for best quality

**Gallery mode not working:**
- Make sure you called task 15 to enable gallery mode
- Check that bitmaps are registered (count > 0)

