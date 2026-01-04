# SquareLine Studio Export Path

## Export Folder

**Use this exact path in SquareLine Studio:**

```
/home/a/projects/DeviceOps/firmware/stm32_gui/ui/
```

## How to Set Export Path

1. In SquareLine Studio, go to: `File` → `Project Settings`
2. Click the **"Export"** tab
3. In **"Output Folder"** field, enter:
   ```
   /home/a/projects/DeviceOps/firmware/stm32_gui/ui/
   ```
4. Or click the folder icon and navigate to:
   - `firmware/stm32_gui/ui/`
5. Click **"OK"** to save

## What Gets Exported

When you click `File` → `Export UI`, these files are created:
- `ui/ui.h` - UI header file
- `ui/ui.c` - UI implementation
- `ui/assets/` - Images and fonts (if used)

## Images Location

Your images (1.png, 2.png, etc.) are now in:
```
/home/a/projects/DeviceOps/firmware/stm32_gui/assets/
```

SquareLine Studio will find them automatically when you:
- Use Asset Panel "Add file into Assets" button
- Or they're already in the project's assets folder

## Quick Reference

- **Project folder**: `/home/a/projects/DeviceOps/firmware/stm32_gui/`
- **Assets folder**: `/home/a/projects/DeviceOps/firmware/stm32_gui/assets/`
- **Export folder**: `/home/a/projects/DeviceOps/firmware/stm32_gui/ui/`



