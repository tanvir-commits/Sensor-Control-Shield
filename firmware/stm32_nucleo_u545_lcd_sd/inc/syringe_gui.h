#ifndef SYRINGE_GUI_H
#define SYRINGE_GUI_H

#include "main.h"
#include <stdint.h>
#include <stdbool.h>

/* Screen types */
typedef enum {
    SCREEN_DELIVERY_STATUS = 0,
    SCREEN_CASSETTE_LOW = 1,
    SCREEN_COUNT
} screen_type_t;

/* Function prototypes */
void GUI_Init(void);
void GUI_DrawScreen(screen_type_t screen);
void GUI_ProcessButton(void);
screen_type_t GUI_GetCurrentScreen(void);
void GUI_NextScreen(void);

/* Drawing functions */
void GUI_DrawHeader(const char* text, uint16_t bg_color);
void GUI_DrawBatteryIcon(int16_t x, int16_t y, uint8_t percent);
void GUI_DrawSyringe(int16_t x, int16_t y, uint8_t fill_percent);
void GUI_DrawText(int16_t x, int16_t y, const char* text, uint16_t color, uint16_t bg, uint8_t size);
void GUI_DrawLargeNumber(int16_t x, int16_t y, const char* number, uint16_t color);

#endif /* SYRINGE_GUI_H */

