# Flashing Instructions

## Build Output

The build produces:
- `build/stm32_gui.hex` - Intel HEX format (686KB)
- `build/stm32_gui.bin` - Binary format (244KB)
- `build/stm32_gui.elf` - ELF format (for debugging)

## Flashing with st-flash

1. **Connect the STM32 board via USB**
2. **Flash the firmware:**
   ```bash
   cd firmware/stm32_gui
   st-flash write build/stm32_gui.bin 0x08000000
   ```

   Or using HEX format:
   ```bash
   st-flash --format ihex write build/stm32_gui.hex
   ```

3. **Verify the flash:**
   ```bash
   st-flash read build/verify.bin 0x08000000 0x3D000
   ```

## Flashing with OpenOCD

If you prefer OpenOCD:

```bash
openocd -f interface/stlink.cfg -f target/stm32u5x.cfg \
  -c "program build/stm32_gui.elf verify reset exit"
```

## Expected Behavior

After flashing:
1. The display should initialize (backlight on)
2. You should see "LVGL GUI Ready!" label on the screen
3. Buttons should be functional (when properly connected)

## Troubleshooting

- **Board not detected:** Check USB connection, try different USB port
- **Flash fails:** Make sure no other program is using the ST-Link
- **Display blank:** Check LCD connections, verify backlight is on
- **No response:** Check button GPIO pins in `inc/button_driver.h`

## Button Pin Configuration

Update `inc/button_driver.h` with your actual GPIO pins:
- BUTTON_UP_PIN / BUTTON_UP_PORT
- BUTTON_DOWN_PIN / BUTTON_DOWN_PORT  
- BUTTON_LEFT_PIN / BUTTON_LEFT_PORT
- BUTTON_RIGHT_PIN / BUTTON_RIGHT_PORT
- BUTTON_PLAY_PIN / BUTTON_PLAY_PORT



