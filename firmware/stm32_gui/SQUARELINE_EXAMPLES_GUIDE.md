# SquareLine Studio Examples and Assets Guide

## Accessing Example Projects (Easiest Way to Start!)

SquareLine Studio has built-in example projects that are ready to use:

1. **In SquareLine Studio Launcher:**
   - Click the **"Example"** tab (next to "Create" and "Open" tabs)
   - Browse the available example projects
   - Examples include:
     - Widget demos
     - UI patterns
     - Complete applications
   - Select an example you like
   - Click **"CREATE SELECTED EXAMPLE"** button

2. **Modify Example for Your Display:**
   - After opening the example, go to `File` → `Project Settings`
   - **Resolution**: Change to `240 x 320`
   - **Color depth**: Set to `16 bit` (RGB565)
   - **LVGL version**: Select `9.1.0` or latest v9.x
   - **Export path**: `/home/a/projects/DeviceOps/firmware/stm32_gui/ui/`

3. **Export and Use:**
   - The example is already designed and working
   - Just export it (`File` → `Export UI`)
   - It will work with your firmware!

## Adding Assets (Images and Fonts)

### Method 1: Using Asset Panel (Recommended)

1. **In SquareLine Studio:**
   - Find the **Asset Panel** (usually on the left sidebar)
   - Click the **"Add file into Assets"** button (looks like a folder with +)
   - Select PNG, JPG images or TTF font files from your computer
   - Assets automatically appear in the panel

2. **Using Assets in Your UI:**
   - Drag images from Asset Panel onto your screen
   - Select fonts from the font dropdown when editing text widgets

### Method 2: Manual Copy to Project Folder

1. **For Images:**
   ```bash
   # Copy images to your project's assets folder
   cp your_image.png /home/a/projects/DeviceOps/firmware/stm32_gui/assets/
   ```
   - SquareLine Studio will auto-detect them
   - Refresh Asset Panel if needed

2. **For Fonts:**
   ```bash
   # Copy fonts to Fonts subfolder
   cp your_font.ttf /home/a/projects/DeviceOps/firmware/stm32_gui/assets/Fonts/
   ```
   - Fonts will appear in font selection dropdowns

### Asset Locations

- **Project Assets**: `firmware/stm32_gui/assets/`
- **Images**: `firmware/stm32_gui/assets/*.png` or `*.jpg`
- **Fonts**: `firmware/stm32_gui/assets/Fonts/*.ttf`

## Quick Start: Use an Example Project

**Fastest way to get a working UI:**

1. Open SquareLine Studio
2. Click **"Example"** tab
3. Pick any example (they're all good starting points)
4. Click **"CREATE SELECTED EXAMPLE"**
5. Modify resolution to 240x320 in Project Settings
6. Export to `firmware/stm32_gui/ui/`
7. Build and flash - you'll have a working UI immediately!

## Why Examples Are Better Than Starting from Scratch

- ✅ Already designed and tested
- ✅ Shows best practices
- ✅ Demonstrates widget usage
- ✅ Includes proper event handling
- ✅ Ready to modify for your needs
- ✅ Saves hours of design time

## Next Steps After Using Example

1. Study the example code structure
2. Modify colors, text, and layout
3. Add your own widgets
4. Customize event handlers
5. Export and integrate with your firmware



