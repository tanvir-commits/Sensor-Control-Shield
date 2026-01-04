# SquareLine Studio Integration - Ready!

## Status: ✅ Integration Code Prepared

The firmware is now ready to automatically use SquareLine Studio UI when you export it!

## How It Works

### Automatic Detection
- **Before Export**: Firmware uses a simple test screen (shows "LVGL GUI Ready!")
- **After Export**: Firmware automatically detects `ui/ui.h` and uses your SquareLine Studio UI instead

### No Manual Code Changes Needed
- Makefile automatically includes `ui/ui.c` when it exists
- `main.c` automatically calls `ui_init()` when UI is available
- Just export from SquareLine Studio and rebuild!

## Quick Start Guide

### Step 1: Get an Example Project (Easiest!)

1. **Open SquareLine Studio**
2. **Click "Example" tab** (not "Create"!)
3. **Select any example** that looks interesting
4. **Click "CREATE SELECTED EXAMPLE"**
5. **Modify Project Settings:**
   - Go to `File` → `Project Settings`
   - **Resolution**: `240 x 320`
   - **Color depth**: `16 bit`
   - **LVGL version**: `9.1.0` (or latest v9.x)
   - **Export path**: `/home/a/projects/DeviceOps/firmware/stm32_gui/ui/`

### Step 2: Export UI

1. In SquareLine Studio: `File` → `Export UI` (or `Ctrl+E`)
2. Files will be created in `firmware/stm32_gui/ui/`:
   - `ui.h` - UI header
   - `ui.c` - UI implementation
   - Assets folder (if you used images/fonts)

### Step 3: Build and Flash

```bash
cd firmware/stm32_gui
make
st-flash write build/stm32_gui.bin 0x08000000
```

That's it! Your SquareLine Studio UI will appear on the display.

## Adding Assets

### Images
1. In SquareLine Studio Asset Panel, click "Add file into Assets"
2. Select PNG or JPG images
3. Drag them onto your UI design
4. Export - images are automatically included

### Fonts
1. Copy TTF font files to: `firmware/stm32_gui/assets/Fonts/`
2. Or use Asset Panel "Add file" button
3. Select font in text widget properties
4. Export - fonts are automatically included

## What Happens Automatically

1. **Makefile** detects `ui/ui.c` and compiles it
2. **main.c** detects `UI_H` define and includes `ui/ui.h`
3. **main.c** calls `ui_init()` instead of creating test screen
4. Your SquareLine Studio UI appears on the display!

## Testing

1. **Before exporting UI**: You'll see the test screen
2. **After exporting UI**: You'll see your SquareLine Studio design
3. **Button navigation**: Works automatically with exported UI (if you set up groups in SquareLine Studio)

## Troubleshooting

- **UI doesn't appear**: Make sure you exported to `firmware/stm32_gui/ui/`
- **Build errors**: Check that LVGL version matches (v9.1.0)
- **Buttons don't work**: Make sure you created a group in SquareLine Studio and assigned it to the input device

## Next Steps

1. Open SquareLine Studio
2. Click "Example" tab
3. Pick an example
4. Modify for 240x320
5. Export
6. Build and flash
7. Enjoy your UI!



