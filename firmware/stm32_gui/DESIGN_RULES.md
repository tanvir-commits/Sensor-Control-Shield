# GUI Design Rules and Coding Standards

## Architecture

```
┌─────────────────────────────────────┐
│         Application Layer           │
│    (gui_screens/, gui_widgets/)     │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│         LVGL Library                │
│         (lvgl/)                     │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│         Port Layer                  │
│    (lvgl_port.c - display/input)    │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│      Hardware Drivers               │
│  (st7789_driver.c, button_driver.c) │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│         HAL Layer                   │
│    (STM32 HAL Drivers)              │
└─────────────────────────────────────┘
```

## Naming Conventions

### Functions
- **Format**: `gui_<module>_<action>()`
- **Examples**:
  - `gui_screen_home_create()`
  - `gui_widget_button_create()`
  - `gui_config_set_theme()`

### Variables
- **Format**: `gui_<module>_<name>`
- **Examples**:
  - `gui_screen_home_obj`
  - `gui_config_theme`
  - `gui_widget_button_style`

### Constants
- **Format**: `GUI_<MODULE>_<NAME>`
- **Examples**:
  - `GUI_SCREEN_HOME_ID`
  - `GUI_COLOR_PRIMARY`
  - `GUI_FONT_SIZE_LARGE`

### Files
- **Format**: `gui_<module>_<name>.c/h`
- **Examples**:
  - `gui_screen_home.c/h`
  - `gui_widget_button.c/h`
  - `gui_config.c/h`

## Code Organization

### One Screen Per File
Each screen gets its own `.c/.h` file pair:
```
gui_screens/
├── screen_home.c
├── screen_home.h
├── screen_settings.c
└── screen_settings.h
```

### Widget Components
Reusable widgets in `gui_widgets/`:
```
gui_widgets/
├── widget_button.c
├── widget_button.h
└── widget_panel.c
```

### Separation of Concerns
- **Display driver**: Only hardware communication (ST7789)
- **Port layer**: LVGL ↔ Hardware translation
- **GUI logic**: Screen/widget creation and management
- **Configuration**: Theme, colors, fonts (programmatic)

## Human-Readable Code Rules

### 1. Self-Documenting Names
```c
// Good
void gui_screen_home_create(void);
lv_obj_t *gui_widget_button_create(lv_obj_t *parent, const char *text);

// Bad
void create_home(void);
lv_obj_t *btn(lv_obj_t *p, const char *t);
```

### 2. Minimal Comments
Code should read like documentation:
```c
// Good - self-explanatory
lv_obj_t *button = gui_widget_button_create(parent, "OK");
gui_widget_button_set_color(button, GUI_COLOR_PRIMARY);

// Bad - comments explain what code should make obvious
// Create a button
lv_obj_t *button = lv_btn_create(parent);  // Makes a button
lv_obj_set_style_bg_color(button, lv_color_hex(0x123456), 0);  // Sets color
```

### 3. Consistent Structure
All screens follow the same pattern:
```c
// screen_home.c
lv_obj_t *gui_screen_home_obj = NULL;

lv_obj_t *gui_screen_home_create(void) {
    gui_screen_home_obj = lv_obj_create(NULL);
    // ... screen setup ...
    return gui_screen_home_obj;
}

void gui_screen_home_show(void) {
    lv_scr_load(gui_screen_home_obj);
}
```

## Programmatic Configuration

### Central Config System
All GUI settings in `gui_config.c/h`:
```c
// gui_config.h
typedef struct {
    lv_color_t color_primary;
    lv_color_t color_secondary;
    lv_color_t color_background;
    lv_color_t color_text;
    const lv_font_t *font_normal;
    const lv_font_t *font_large;
} gui_config_theme_t;

void gui_config_set_theme(const gui_config_theme_t *theme);
void gui_config_set_color_primary(lv_color_t color);
lv_color_t gui_config_get_color_primary(void);
```

### Runtime Changes
Configuration can be modified programmatically:
```c
// Change theme at runtime
gui_config_theme_t dark_theme = {
    .color_primary = lv_color_hex(0x00FF00),
    .color_background = lv_color_hex(0x000000),
    // ...
};
gui_config_set_theme(&dark_theme);
```

## LVGL Integration Rules

### Port Layer Abstraction
- All LVGL hardware interaction through `lvgl_port.c`
- Application code never directly calls ST7789 or button driver
- Port layer handles display flush and input reading

### No Direct LVGL Calls in App
Use wrapper functions:
```c
// Good - use wrapper
lv_obj_t *button = gui_widget_button_create(parent, "OK");

// Avoid - direct LVGL calls in application code
lv_obj_t *button = lv_btn_create(parent);
lv_obj_set_size(button, 100, 40);
lv_obj_set_style_bg_color(button, ...);
```

## SquareLine Studio Integration

### Generated Code Location
- SquareLine Studio exports to `ui/` directory
- Generated files: `ui/ui.h`, `ui/ui.c` (if needed)

### Workflow
1. Design UI in SquareLine Studio
2. Export to `ui/` directory
3. Include `ui/ui.h` in code
4. Call `ui_init()` after LVGL initialization

### Customization
- Generated code can be modified, but re-exporting overwrites
- Keep custom logic separate from generated UI code
- Use `gui_config.c` for programmatic theme changes

## Memory Management

### Display Buffer
- **Strategy**: Partial buffer (1/10 of screen)
- **Size**: 240 × 32 = 7680 pixels = 15360 bytes
- **Location**: SRAM (static arrays in `lvgl_port.c`)
- **Double buffering**: Two buffers for smooth updates

### LVGL Memory
- **Size**: 64KB (configurable in `lv_conf.h`)
- **Location**: SRAM
- **Management**: LVGL's built-in memory manager

## Button Input

### Mapping
- **Up** → `LV_KEY_UP`
- **Down** → `LV_KEY_DOWN`
- **Left** → `LV_KEY_LEFT`
- **Right** → `LV_KEY_RIGHT`
- **Play** → `LV_KEY_ENTER`

### Navigation
- Use LVGL groups for keyboard navigation
- Focus management handled by LVGL
- Button debouncing: 50ms (configurable)

## Best Practices

### Do's
✅ Use wrapper functions for widgets
✅ Keep screens/widgets modular
✅ Use configuration system for themes
✅ Follow naming conventions
✅ Separate generated code from custom code

### Don'ts
❌ Direct hardware calls in application code
❌ Magic numbers (use config constants)
❌ Hardcoded colors/fonts
❌ Mixing generated and custom code
❌ Direct LVGL calls without abstraction

## ThreadX Migration Path

### Current (Baremetal)
- LVGL tick: SysTick interrupt or HAL tick
- Button polling: Main loop or timer interrupt

### Future (ThreadX)
- LVGL tick: ThreadX thread with periodic timer
- Button polling: Separate thread or timer callback
- Port layer abstracts tick source (easy to switch)

## File Structure Template

### Screen File
```c
// gui_screen_home.h
#ifndef GUI_SCREEN_HOME_H
#define GUI_SCREEN_HOME_H
#include "lvgl.h"
lv_obj_t *gui_screen_home_create(void);
void gui_screen_home_show(void);
#endif

// gui_screen_home.c
#include "gui_screen_home.h"
#include "gui_config.h"

static lv_obj_t *screen_obj = NULL;

lv_obj_t *gui_screen_home_create(void) {
    screen_obj = lv_obj_create(NULL);
    // ... setup ...
    return screen_obj;
}

void gui_screen_home_show(void) {
    lv_scr_load(screen_obj);
}
```

### Widget File
```c
// gui_widget_button.h
#ifndef GUI_WIDGET_BUTTON_H
#define GUI_WIDGET_BUTTON_H
#include "lvgl.h"
lv_obj_t *gui_widget_button_create(lv_obj_t *parent, const char *text);
#endif

// gui_widget_button.c
#include "gui_widget_button.h"
#include "gui_config.h"

lv_obj_t *gui_widget_button_create(lv_obj_t *parent, const char *text) {
    lv_obj_t *btn = lv_btn_create(parent);
    // ... setup using gui_config ...
    return btn;
}
```



