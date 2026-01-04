# STM32 GUI Project with LVGL

GUI project for STM32U545RE-Q with Waveshare 2-inch ST7789 display (240x320) using LVGL and SquareLine Studio.

## Hardware

- **MCU**: STM32U545RE-Q (Cortex-M33, 512KB Flash, 272KB RAM)
- **Display**: Waveshare 2-inch LCD with ST7789V controller
  - Resolution: 240x320 pixels (portrait)
  - Interface: SPI
  - Color: RGB565 (16-bit)
- **Input**: 5 buttons (Up, Down, Left, Right, Play)
  - GPIO inputs with pull-up resistors
  - Software debouncing (50ms)

## Project Structure

```
firmware/stm32_gui/
├── src/
│   ├── main.c                    # Main application
│   ├── lvgl_port.c               # LVGL hardware port (display/input)
│   ├── gui_config.c              # GUI configuration system
│   ├── system/
│   │   ├── st7789_driver.c       # ST7789 LCD driver
│   │   └── button_driver.c       # Button input driver
│   ├── gui_screens/              # Screen definitions (for custom screens)
│   └── gui_widgets/              # Reusable widget components
├── inc/
│   ├── lvgl_port.h
│   ├── st7789_driver.h
│   ├── button_driver.h
│   └── gui_config.h
├── config/
│   └── gui_config.h               # Programmatic configuration
├── ui/                            # SquareLine Studio generated UI files
│   └── ui.h                       # Generated header
├── lvgl/                          # LVGL library (v9.1)
│   └── lv_conf.h                  # LVGL configuration
└── Makefile
```

## SquareLine Studio Integration

### Setup

1. **Install SquareLine Studio** from https://squareline.studio
2. **Create new project**:
   - Display: 240x320
   - Color depth: 16-bit (RGB565)
   - Platform: STM32
3. **Export settings**:
   - Export path: `firmware/stm32_gui/ui/`
   - Export format: C code

### Workflow

1. Design UI in SquareLine Studio
2. Export to `ui/` directory
3. Include `ui/ui.h` in your code
4. Call `ui_init()` in `main()` after LVGL initialization

### Generated Files

SquareLine Studio generates:
- `ui/ui.h` - UI definitions and initialization
- `ui/ui.c` - UI implementation (if needed)

## Building

```bash
cd firmware/stm32_gui
make clean
make
```

## Flashing

```bash
# Using OpenOCD
make flash

# Using STM32CubeProgrammer
make flash-stm32prog
```

## Configuration

### Button Pins

Update pin definitions in `inc/button_driver.h`:

```c
#define BUTTON_UP_PIN       GPIO_PIN_X
#define BUTTON_UP_PORT      GPIOX
// ... etc
```

### Display Settings

Display configuration in `lvgl/lv_conf.h`:
- Width: 240
- Height: 320
- Color depth: 16-bit (RGB565)
- Buffer size: Partial (1/10 screen)

## Design Rules

See `DESIGN_RULES.md` for:
- Code organization
- Naming conventions
- Configuration system
- Best practices

## Dependencies

- LVGL v9.1 (included as submodule/copy)
- STM32 HAL drivers
- SquareLine Studio (for UI design)

## License

Same as parent project.



