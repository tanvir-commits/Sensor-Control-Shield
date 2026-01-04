#include "gui_config.h"
#include "lvgl.h"

/* Default theme */
static gui_config_theme_t current_theme = {
    .color_primary = LV_COLOR_MAKE(0x00, 0x7A, 0xFF),
    .color_secondary = LV_COLOR_MAKE(0x58, 0x56, 0xD6),
    .color_background = LV_COLOR_MAKE(0x00, 0x00, 0x00),
    .color_text = LV_COLOR_MAKE(0xFF, 0xFF, 0xFF),
    .color_success = LV_COLOR_MAKE(0x34, 0xC7, 0x59),
    .color_warning = LV_COLOR_MAKE(0xFF, 0x95, 0x00),
    .color_error = LV_COLOR_MAKE(0xFF, 0x3B, 0x30),
    .font_normal = &lv_font_montserrat_14,
    .font_large = &lv_font_montserrat_14,  /* TODO: Enable LV_FONT_MONTSERRAT_24 in lv_conf.h */
    .font_small = &lv_font_montserrat_14,  /* TODO: Enable LV_FONT_MONTSERRAT_12 in lv_conf.h */
};

/**
 * @brief Initialize GUI configuration system
 */
void gui_config_init(void)
{
    /* Configuration is initialized with defaults */
    /* User can call gui_config_set_theme() to change */
}

/**
 * @brief Set theme
 */
void gui_config_set_theme(const gui_config_theme_t *theme)
{
    if (theme != NULL) {
        current_theme = *theme;
    }
}

/**
 * @brief Set primary color
 */
void gui_config_set_color_primary(lv_color_t color)
{
    current_theme.color_primary = color;
}

/**
 * @brief Set background color
 */
void gui_config_set_color_background(lv_color_t color)
{
    current_theme.color_background = color;
}

/**
 * @brief Get primary color
 */
lv_color_t gui_config_get_color_primary(void)
{
    return current_theme.color_primary;
}

/**
 * @brief Get background color
 */
lv_color_t gui_config_get_color_background(void)
{
    return current_theme.color_background;
}

/**
 * @brief Get normal font
 */
const lv_font_t *gui_config_get_font_normal(void)
{
    return current_theme.font_normal;
}

/**
 * @brief Get large font
 */
const lv_font_t *gui_config_get_font_large(void)
{
    return current_theme.font_large;
}

/**
 * @brief Get current theme
 */
const gui_config_theme_t *gui_config_get_theme(void)
{
    return &current_theme;
}

