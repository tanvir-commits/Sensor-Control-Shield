# SquareLine Studio Manual Installation

## Status

The automatic download is failing due to network connectivity issues. Please install SquareLine Studio manually.

## Manual Installation Steps

1. **Download SquareLine Studio:**
   - Visit: https://squareline.studio/downloads
   - Download: `SquareLine_Studio_Linux_AppImage.tar.gz`
   - Save to: `~/SquareLine_Studio/` or `/opt/SquareLine_Studio/`

2. **Extract and Install:**
   ```bash
   cd ~/SquareLine_Studio
   tar -xzf SquareLine_Studio_Linux_AppImage.tar.gz
   chmod +x SquareLine_Studio-*.AppImage
   ```

3. **Run SquareLine Studio:**
   ```bash
   ./SquareLine_Studio-*.AppImage
   ```

4. **Create Project:**
   - Project Name: `STM32_GUI_Project`
   - Display Resolution: `240x320`
   - Color Depth: `16-bit` (RGB565)
   - Platform: `STM32`
   - LVGL Version: `v9.1.0`

5. **Export Settings:**
   - Output Folder: `/home/a/projects/DeviceOps/firmware/stm32_gui/ui/`
   - Export Format: `C code`

## Alternative: Use Install Script After Download

If you download the file manually, you can use the install script:

```bash
cd ~/SquareLine_Studio
# Place SquareLine_Studio_Linux_AppImage.tar.gz here
cd /home/a/projects/DeviceOps/firmware/stm32_gui
./install_squareline.sh
```

## Note

The firmware has been successfully flashed and is ready for testing. SquareLine Studio installation requires manual download due to network restrictions.



