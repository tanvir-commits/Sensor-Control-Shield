# Quick Start: SquareLine Studio Examples

## The Easiest Way to Get Started!

**You don't need to create a project from scratch!** SquareLine Studio has ready-to-use examples.

## Step-by-Step: Use an Example Project

### 1. Open SquareLine Studio
```bash
squareline
```

### 2. Click "Example" Tab
- **NOT** the "Create" tab
- Click the **"Example"** tab at the top
- This shows all available example projects

### 3. Select an Example
- Browse the examples (they're all good!)
- Examples include:
  - Widget demos
  - UI patterns  
  - Complete applications
- Click on any example you like

### 4. Create the Example
- Click **"CREATE SELECTED EXAMPLE"** button
- The example project opens in SquareLine Studio

### 5. Modify for Your Display
- Go to: `File` → `Project Settings`
- Change these settings:
  - **Resolution**: `240` × `320` (width × height)
  - **Color depth**: `16 bit` (RGB565)
  - **LVGL version**: `9.1.0` (or latest v9.x available)
  - **Export path**: `/home/a/projects/DeviceOps/firmware/stm32_gui/ui/`

### 6. Export UI
- Click: `File` → `Export UI` (or press `Ctrl+E`)
- Files are created in `firmware/stm32_gui/ui/`

### 7. Build and Flash
```bash
cd firmware/stm32_gui
make
st-flash write build/stm32_gui.bin 0x08000000
```

**Done!** Your example UI is now running on your STM32!

## Why Examples Are Better

✅ **Already designed** - No blank screen  
✅ **Working code** - Tested and functional  
✅ **Best practices** - Shows proper widget usage  
✅ **Learn by example** - See how things should be done  
✅ **Save time** - Hours of design work already done  

## Adding Assets (Images/Fonts)

### In SquareLine Studio:
1. Find the **Asset Panel** (left sidebar)
2. Click **"Add file into Assets"** button
3. Select PNG/JPG images or TTF fonts
4. Drag assets onto your UI design
5. Export - assets are automatically included!

### Manual Method:
```bash
# Copy images
cp my_image.png firmware/stm32_gui/assets/

# Copy fonts  
cp my_font.ttf firmware/stm32_gui/assets/Fonts/
```

SquareLine Studio will auto-detect them.

## What Happens Automatically

The firmware is **already configured** to:
- ✅ Detect when you export UI files
- ✅ Automatically compile `ui/ui.c`
- ✅ Automatically call `ui_init()`
- ✅ Use your SquareLine Studio UI instead of test screen

**No manual code changes needed!**

## Next Steps After Example Works

1. **Study the example** - See how it's structured
2. **Modify it** - Change colors, text, layout
3. **Add widgets** - Try different UI elements
4. **Customize** - Make it your own!

## Troubleshooting

- **Can't find Example tab?** Make sure you're in the launcher window (not inside a project)
- **Example resolution wrong?** Modify in Project Settings before exporting
- **UI doesn't appear?** Check export path is correct: `/home/a/projects/DeviceOps/firmware/stm32_gui/ui/`
- **Build errors?** Make sure LVGL version matches (v9.1.0)

## Summary

**Fastest path to working UI:**
1. Open SquareLine Studio → "Example" tab
2. Pick any example → "CREATE SELECTED EXAMPLE"
3. Set resolution to 240x320
4. Export
5. Build and flash
6. Done! 🎉



