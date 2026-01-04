# SquareLine Studio Setup Guide

## ✅ Installation Complete

SquareLine Studio has been extracted and is ready to use.

## Running SquareLine Studio

### Option 1: Direct Run
```bash
cd ~/SquareLine_Studio
./SquareLine_Studio-*.AppImage
```

### Option 2: Using Launcher (if created)
```bash
squareline
```

## Creating Your STM32 GUI Project

1. **Launch SquareLine Studio**

2. **Create New Project:**
   - Click "Create New Project"
   - **Project Name**: `STM32_GUI_Project`
   - **Display Resolution**: `240x320` (width x height)
   - **Color Depth**: `16-bit` (RGB565)
   - **Platform**: `STM32`
   - **LVGL Version**: `v9.1.0` (or latest v9.x)
   - Click "Create"

3. **Configure Export Settings:**
   - Go to: `File` → `Project Settings` → `Export` tab
   - **Output Folder**: `/home/a/projects/DeviceOps/firmware/stm32_gui/ui/`
   - **Export Format**: `C code`
   - **Export only changed files**: (your preference)

4. **Design Your GUI:**
   - Use the visual editor to design your interface
   - Add widgets, buttons, labels, etc.
   - Test the layout for 240x320 resolution

5. **Export UI:**
   - Click `File` → `Export UI` (or `Ctrl+E`)
   - Files will be generated in: `firmware/stm32_gui/ui/`

## Integrating Exported UI

After exporting, the UI files will be in `firmware/stm32_gui/ui/`. To use them:

1. **Include in main.c:**
   ```c
   #include "ui/ui.h"
   ```

2. **Initialize in main():**
   ```c
   lvgl_port_init();
   ui_init();  // Initialize SquareLine Studio UI
   ```

3. **Rebuild:**
   ```bash
   cd firmware/stm32_gui
   make
   ```

4. **Flash:**
   ```bash
   st-flash write build/stm32_gui.bin 0x08000000
   ```

## Project Structure

```
firmware/stm32_gui/
├── ui/                    # SquareLine Studio exports here
│   ├── ui.h
│   ├── ui.c
│   └── ...
├── src/
│   └── main.c            # Include ui/ui.h here
└── ...
```

## Notes

- The firmware is already set up and working
- Button simulation via UART is functional
- Display driver (ST7789) is configured
- LVGL v9.1 is integrated
- Just design your GUI and export!

## Troubleshooting

- **AppImage won't run**: Make sure it's executable: `chmod +x SquareLine_Studio-*.AppImage`
- **Export fails**: Check that the output folder path exists and is writable
- **UI doesn't appear**: Make sure `ui_init()` is called after `lvgl_port_init()`



