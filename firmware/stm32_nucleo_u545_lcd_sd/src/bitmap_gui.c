#include "bitmap_gui.h"
#include "fonts/fonts.h"
#include <string.h>
#include <stdio.h>

/* Maximum number of bitmaps in gallery */
#define MAX_BITMAPS 16

/* Bitmap gallery storage */
static bitmap_entry_t bitmap_gallery[MAX_BITMAPS];
static uint8_t bitmap_count = 0;
static uint8_t current_bitmap_index = 0;
static bitmap_mode_t current_mode = BITMAP_MODE_NORMAL;

/**
 * @brief Initialize bitmap GUI system
 */
void BitmapGUI_Init(void)
{
    bitmap_count = 0;
    current_bitmap_index = 0;
    current_mode = BITMAP_MODE_NORMAL;
    memset(bitmap_gallery, 0, sizeof(bitmap_gallery));
}

/**
 * @brief Set GUI mode (normal or gallery)
 */
void BitmapGUI_SetMode(bitmap_mode_t mode)
{
    current_mode = mode;
    if (mode == BITMAP_MODE_GALLERY && bitmap_count > 0) {
        current_bitmap_index = 0;
        BitmapGUI_ShowCurrentBitmap();
    }
}

/**
 * @brief Get current GUI mode
 */
bitmap_mode_t BitmapGUI_GetMode(void)
{
    return current_mode;
}

/**
 * @brief Register a bitmap in the gallery
 * @param data Pointer to RGB565 bitmap data (little-endian byte array)
 * @param width Bitmap width in pixels
 * @param height Bitmap height in pixels
 * @param name Display name for the bitmap
 */
void BitmapGUI_RegisterBitmap(const uint8_t *data, uint16_t width, uint16_t height, const char *name)
{
    if (bitmap_count >= MAX_BITMAPS || data == NULL) {
        return;
    }
    
    bitmap_gallery[bitmap_count].data = data;
    bitmap_gallery[bitmap_count].width = width;
    bitmap_gallery[bitmap_count].height = height;
    bitmap_gallery[bitmap_count].name = (name != NULL) ? name : "Unnamed";
    bitmap_count++;
}

/**
 * @brief Switch to next bitmap in gallery
 */
void BitmapGUI_NextBitmap(void)
{
    if (bitmap_count == 0) {
        return;
    }
    
    current_bitmap_index = (current_bitmap_index + 1) % bitmap_count;
    BitmapGUI_ShowCurrentBitmap();
}

/**
 * @brief Switch to previous bitmap in gallery
 */
void BitmapGUI_PreviousBitmap(void)
{
    if (bitmap_count == 0) {
        return;
    }
    
    if (current_bitmap_index == 0) {
        current_bitmap_index = bitmap_count - 1;
    } else {
        current_bitmap_index--;
    }
    BitmapGUI_ShowCurrentBitmap();
}

/**
 * @brief Display current bitmap
 */
void BitmapGUI_ShowCurrentBitmap(void)
{
    if (bitmap_count == 0 || current_bitmap_index >= bitmap_count) {
        // No bitmaps - show black screen
        ST7789_FillScreen(COLOR_BLACK);
        return;
    }
    
    bitmap_entry_t *bitmap = &bitmap_gallery[current_bitmap_index];
    
    // Clear screen first
    ST7789_FillScreen(COLOR_BLACK);
    
    // For rotation 3 (landscape inverted), screen is effectively 320x240
    // Bitmaps are 320x240, so draw at (0,0) - full screen
    // Draw bitmap at top-left corner (full screen fill)
    ST7789_DrawImageBytes(0, 0, bitmap->width, bitmap->height, bitmap->data);
}

/**
 * @brief Show bitmap information overlay
 */
void BitmapGUI_ShowBitmapInfo(void)
{
    if (bitmap_count == 0 || current_bitmap_index >= bitmap_count) {
        return;
    }
    
    bitmap_entry_t *bitmap = &bitmap_gallery[current_bitmap_index];
    
    // Draw semi-transparent info bar at bottom (make it taller for bigger font)
    ST7789_DrawRect(0, LCD_HEIGHT - 35, LCD_WIDTH, 35, COLOR_BLACK);
    
    // Show bitmap name and index
    char info[64];
    snprintf(info, sizeof(info), "%d/%d: %s", 
             current_bitmap_index + 1, bitmap_count, bitmap->name);
    
    // Truncate if too long (fewer chars for bigger font)
    if (strlen(info) > 15) {
        info[12] = '.';
        info[13] = '.';
        info[14] = '.';
        info[15] = '\0';
    }
    
    // Use Font24 for bigger text
    ST7789_DrawString(5, LCD_HEIGHT - 30, info, COLOR_WHITE, COLOR_BLACK, &Font24);
}

/**
 * @brief Get number of registered bitmaps
 */
uint8_t BitmapGUI_GetBitmapCount(void)
{
    return bitmap_count;
}

/**
 * @brief Get current bitmap index
 */
uint8_t BitmapGUI_GetCurrentIndex(void)
{
    return current_bitmap_index;
}

