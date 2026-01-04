# SquareLine Studio Installation Status

## Current Status: ⚠️ **NOT INSTALLED**

The existing tar.gz files appear to be corrupted or incomplete. SquareLine Studio needs to be downloaded fresh.

## Installation Options

### Option 1: Manual Download (Recommended)
1. Visit: **https://squareline.studio/downloads**
2. Download: `SquareLine_Studio_Linux_AppImage.tar.gz`
3. Extract:
   ```bash
   cd ~/SquareLine_Studio
   tar -xzf ~/Downloads/SquareLine_Studio_Linux_AppImage.tar.gz
   chmod +x SquareLine_Studio-*.AppImage
   ```
4. Run:
   ```bash
   ~/SquareLine_Studio/SquareLine_Studio-*.AppImage
   ```

### Option 2: Direct AppImage (if available)
Some distributions provide a direct AppImage download without tar.gz.

## Project Settings for SquareLine Studio

When creating a new project:
- **Project Name**: `STM32_GUI_Project`
- **Display Resolution**: `240x320`
- **Color Depth**: `16-bit` (RGB565)
- **Platform**: `STM32`
- **LVGL Version**: `v9.1.0`

## Export Settings

- **Output Folder**: `/home/a/projects/DeviceOps/firmware/stm32_gui/ui/`
- **Export Format**: `C code`

## Note

The firmware is ready and working. SquareLine Studio is only needed for GUI design - the current firmware works with the test interface.



