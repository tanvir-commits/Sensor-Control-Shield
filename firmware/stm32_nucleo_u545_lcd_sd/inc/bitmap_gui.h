#ifndef BITMAP_GUI_H
#define BITMAP_GUI_H

#include "main.h"
#include "st7789.h"
#include <stdint.h>
#include <stdbool.h>

/* Bitmap entry structure */
typedef struct {
    const uint8_t *data;      // Pointer to bitmap data
    uint16_t width;            // Bitmap width
    uint16_t height;           // Bitmap height
    const char *name;          // Bitmap name (for display)
} bitmap_entry_t;

/* Bitmap gallery mode */
typedef enum {
    BITMAP_MODE_NORMAL = 0,    // Normal GUI mode (existing screens)
    BITMAP_MODE_GALLERY = 1    // Bitmap gallery/test mode
} bitmap_mode_t;

/* Function prototypes */
void BitmapGUI_Init(void);
void BitmapGUI_SetMode(bitmap_mode_t mode);
bitmap_mode_t BitmapGUI_GetMode(void);
void BitmapGUI_RegisterBitmap(const uint8_t *data, uint16_t width, uint16_t height, const char *name);
void BitmapGUI_NextBitmap(void);
void BitmapGUI_PreviousBitmap(void);
void BitmapGUI_ShowCurrentBitmap(void);
void BitmapGUI_ShowBitmapInfo(void);
uint8_t BitmapGUI_GetBitmapCount(void);
uint8_t BitmapGUI_GetCurrentIndex(void);

#endif /* BITMAP_GUI_H */

