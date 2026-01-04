# SquareLine Studio Setup

## Installation

1. **Download SquareLine Studio:**
   - Visit: https://squareline.studio/downloads
   - Download the **Linux AppImage** version
   - Save it to `~/Downloads/`

2. **Install using the script:**
   ```bash
   cd firmware/stm32_gui
   ./install_squareline.sh
   ```

   Or manually:
   ```bash
   chmod +x ~/Downloads/SquareLine_Studio_*.AppImage
   mkdir -p ~/.local/bin
   ln -s ~/Downloads/SquareLine_Studio_*.AppImage ~/.local/bin/squareline-studio
   ```

3. **Run SquareLine Studio:**
   ```bash
   squareline-studio
   ```

## Creating a New Project

1. **Launch SquareLine Studio**
2. **Create New Project:**
   - Click "New Project"
   - Select **STM32** platform
   - Display settings:
     - Width: **240**
     - Height: **320**
     - Color depth: **16-bit (RGB565)**
   - Click "Create"

3. **Export Settings:**
   - Go to **File > Export**
   - Export path: `firmware/stm32_gui/ui/`
   - Format: **C Code**
   - Click "Export"

## Opening Existing Project

If you have an existing SquareLine Studio project:

1. **File > Open Project**
2. Navigate to `firmware/stm32_gui/ui/`
3. Select your project file

## Integration with Build System

After exporting from SquareLine Studio:

1. The UI files will be in `firmware/stm32_gui/ui/`
2. Include in your code:
   ```c
   #include "ui/ui.h"
   ```
3. Initialize in `main.c`:
   ```c
   ui_init();  // Call after lvgl_port_init()
   ```

## Notes

- SquareLine Studio projects are stored in the `ui/` directory
- After making changes in SquareLine Studio, re-export to update the C code
- The project is configured for 240x320 RGB565 display (ST7789)



