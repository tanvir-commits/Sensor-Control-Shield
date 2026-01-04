#ifndef GUI_CONFIG_H
#define GUI_CONFIG_H

#include "lvgl.h"
#include <stdint.h>

/* Theme color definitions */
#define GUI_COLOR_PRIMARY_HEX      0x007AFF
#define GUI_COLOR_SECONDARY_HEX    0x5856D6
#define GUI_COLOR_BACKGROUND_HEX   0x000000
#define GUI_COLOR_TEXT_HEX         0xFFFFFF
#define GUI_COLOR_SUCCESS_HEX      0x34C759
#define GUI_COLOR_WARNING_HEX      0xFF9500
#define GUI_COLOR_ERROR_HEX        0xFF3B30

/* Theme structure */
typedef struct {
    lv_color_t color_primary;
    lv_color_t color_secondary;
    lv_color_t color_background;
    lv_color_t color_text;
    lv_color_t color_success;
    lv_color_t color_warning;
    lv_color_t color_error;
    const lv_font_t *font_normal;
    const lv_font_t *font_large;
    const lv_font_t *font_small;
} gui_config_theme_t;

/* Function prototypes */
void gui_config_init(void);
void gui_config_set_theme(const gui_config_theme_t *theme);
void gui_config_set_color_primary(lv_color_t color);
void gui_config_set_color_background(lv_color_t color);
lv_color_t gui_config_get_color_primary(void);
lv_color_t gui_config_get_color_background(void);
const lv_font_t *gui_config_get_font_normal(void);
const lv_font_t *gui_config_get_font_large(void);

/* Get current theme */
const gui_config_theme_t *gui_config_get_theme(void);

#endif /* GUI_CONFIG_H */



