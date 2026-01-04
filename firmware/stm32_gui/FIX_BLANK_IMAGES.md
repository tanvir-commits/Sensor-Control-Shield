# Fix: Images Showing as Blank in SquareLine Studio

## Possible Causes & Solutions

### 1. Refresh Asset Panel
SquareLine Studio might not have detected the resized images:
- **Close and reopen SquareLine Studio**
- Or click "Refresh" in the Asset Panel
- The images should appear after refresh

### 2. Re-add Images to Assets
If refresh doesn't work:
1. In SquareLine Studio Asset Panel
2. Click **"ADD FILE INTO ASSETS"** button
3. Navigate to: `/home/a/projects/DeviceOps/firmware/stm32_gui/assets/`
4. Select all PNG files (1.png, 3.png, 4.png, etc.)
5. Click "Open"
6. Images will be added to the project

### 3. Check Image Path in Inspector
When you select an image component:
- **Inspector → Image → Asset**: Should show the image name (e.g., "10.png")
- **Path**: Should show `assets/10.png`
- If path is wrong, click the Asset dropdown and reselect the image

### 4. Verify Image Component Settings
In Inspector → Image section:
- **Asset**: Should be set to one of your images (1.png, 3.png, etc.)
- **Scale**: Try setting to `100` (not 256 or other large values)
- **Width/Height**: Should be "1 Content" or set to 240×320

### 5. Check Project Assets Folder
SquareLine Studio might be looking in a different location:
- Your images are at: `/home/a/projects/DeviceOps/firmware/stm32_gui/assets/`
- SquareLine Studio project is at: `/home/a/projects/DeviceOps/firmware/stm32_gui/STM32_GUI_Project.spj`
- Assets should be relative to project file: `assets/` folder in same directory

## Quick Fix Steps

1. **In SquareLine Studio:**
   - Go to Asset Panel (bottom bar)
   - Click **"ADD FILE INTO ASSETS"**
   - Navigate to: `/home/a/projects/DeviceOps/firmware/stm32_gui/assets/`
   - Select all PNG files
   - Click "Open"

2. **For existing image components:**
   - Select the image component
   - In Inspector → Image → Asset dropdown
   - Reselect the image file

3. **Verify settings:**
   - Width: 240 px (or "1 Content")
   - Height: 320 px (or "1 Content")  
   - Scale: 100

## Verification

All images are confirmed:
- ✅ All 11 images are readable
- ✅ All are 240×320 pixels
- ✅ All are valid PNG files
- ✅ Located in: `firmware/stm32_gui/assets/`

The issue is likely SquareLine Studio needs to refresh or re-add the assets.



