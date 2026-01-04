# Image Scaling Guide for 240x320 Display

## The Problem

Your images are **1024x1536 pixels**, but your display is only **240x320 pixels**!

That's why they appear zoomed - the images are **4.27x larger** than your screen.

## Solution: Scale Images in SquareLine Studio

### In the Inspector Panel:

1. **Select your image** (Image3 in your case)

2. **In the "Transform" section:**
   - **Width**: Change from "1 Content" to a fixed pixel value
   - **Height**: Change from "1 Content" to a fixed pixel value
   - For a full-screen image: Set to `240` × `320` pixels
   - For a smaller image: Use proportionally smaller values

3. **In the "Image" section:**
   - **Scale**: Currently shows "256" - this is way too high!
   - **Set Scale to**: `100` (or lower if needed)
   - Scale of 100 = 1:1 ratio
   - Scale of 50 = half size
   - Scale of 25 = quarter size

## Recommended Settings for Your Display

### For Full-Screen Image:
- **Width**: `240 px`
- **Height**: `320 px`
- **Scale**: `100` (or adjust to fit)
- **Align**: `CENTER`

### For Scaled-Down Image:
If you want the image smaller:
- **Width**: `120 px` (half width)
- **Height**: `160 px` (half height)
- **Scale**: `100`
- **Align**: `CENTER`

## Quick Fix Steps

1. **Select the image** in SquareLine Studio
2. **In Inspector → Transform:**
   - Click on "Width" field
   - Type: `240` and press Enter
   - Click on "Height" field
   - Type: `320` and press Enter
3. **In Inspector → Image:**
   - Find "Scale" field
   - Change from `256` to `100` (or `25` for quarter size)
4. **Check the preview** - image should now fit properly!

## Understanding the Numbers

- **Your display**: 240 × 320 pixels
- **Your image (8.png)**: 1024 × 1536 pixels
- **Ratio**: Image is 4.27× larger than display
- **To fit**: Scale down to ~23.4% (or use 240×320 size)

## Alternative: Resize Images Before Import

If you want to optimize:
```bash
# Resize images to fit 240x320 (maintains aspect ratio)
# Using ImageMagick (if installed):
convert assets/8.png -resize 240x320 assets/8_resized.png
```

But it's easier to just set the size in SquareLine Studio!

## Pro Tip

For best performance on STM32:
- Use images sized close to your display resolution (240×320)
- Or scale them down in SquareLine Studio
- Large images waste memory and slow down rendering



