# Quick Start: Loading Bitmaps for Testing

## Step 1: Convert Your Image

```bash
cd firmware/stm32_nucleo_u545_lcd_sd
./scripts/convert_bitmap.sh images/my_image.png my_bitmap
```

This automatically:
- Converts PNG/JPG to RGB565 C array
- Resizes to 320x240 (LCD size)
- Creates `src/gui_images_my_bitmap.c` and `inc/gui_images_my_bitmap.h`

## Step 2: Add to Build

Edit `Makefile`, add to C_SOURCES (around line 39):
```makefile
src/gui_images_my_bitmap.c \
```

## Step 3: Include Header

Edit `inc/gui_images.h`, add:
```c
#include "gui_images_my_bitmap.h"
```

## Step 4: Register Bitmap

Edit `src/syringe_gui.c`, in `GUI_Init()` function, add:
```c
BitmapGUI_RegisterBitmap(
    gImage_my_bitmap,
    GIMAGE_MY_BITMAP_WIDTH,
    GIMAGE_MY_BITMAP_HEIGHT,
    "My Bitmap"
);
```

## Step 5: Build & Flash

```bash
make clean && make && make flash
```

## Step 6: Test!

**Enable Gallery Mode:**
```python
from hardware.uart_manager import UARTManager
uart = UARTManager()
uart.open('/dev/ttyACM0', 115200)
uart.send_task(15)  # Enable bitmap gallery
```

**Then press the button on the board** to cycle through all bitmaps!

## That's It!

Your bitmaps are now loaded and ready to test. The system automatically:
- Centers bitmaps if smaller than screen
- Cycles through all registered bitmaps
- Shows clean display (no overlays)

## Example: Test with Existing Images

The project already has 2 bitmaps registered:
- `gImage_delivery_screen` - "Delivery Screen"
- `gImage_alert_screen` - "Alert Screen"

Just enable gallery mode (task 15) and press the button to see them!

