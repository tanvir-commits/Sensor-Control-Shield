#include "syringe_gui.h"
#include "bitmap_gui.h"
#include "st7789.h"
#include "fonts/fonts.h"
#include "gui_images.h"
#include "main.h"  // For hlpuart1
#include <string.h>

/* Button definitions - PC13 (User button on Nucleo) */
#define BUTTON_PIN         GPIO_PIN_13
#define BUTTON_PORT        GPIOC
#define BUTTON_PRESSED     GPIO_PIN_SET  // Button pressed = HIGH (with pull-down)

/* Current screen */
static screen_type_t current_screen = SCREEN_DELIVERY_STATUS;

/* Button debouncing */
static uint32_t last_button_time = 0;
static bool last_button_state = false;
#define BUTTON_DEBOUNCE_MS 5  // Reduced for faster response

/**
 * @brief Initialize GUI system
 */
void GUI_Init(void)
{
    current_screen = SCREEN_DELIVERY_STATUS;
    
    // Initialize bitmap GUI system
    BitmapGUI_Init();
    
    // Register bitmaps (order: 8, 12, 4)
    BitmapGUI_RegisterBitmap(
        gImage_8,
        GIMAGE_8_WIDTH,
        GIMAGE_8_HEIGHT,
        "Image 8"
    );
    
    BitmapGUI_RegisterBitmap(
        gImage_12,
        GIMAGE_12_WIDTH,
        GIMAGE_12_HEIGHT,
        "Image 12"
    );
    
    BitmapGUI_RegisterBitmap(
        gImage_4,
        GIMAGE_4_WIDTH,
        GIMAGE_4_HEIGHT,
        "Image 4"
    );
}

/**
 * @brief Get current screen
 */
screen_type_t GUI_GetCurrentScreen(void)
{
    return current_screen;
}

/**
 * @brief Switch to next screen (wrap around)
 */
void GUI_NextScreen(void)
{
    current_screen = (screen_type_t)((current_screen + 1) % SCREEN_COUNT);
}

/**
 * @brief Process button input with debouncing
 */
void GUI_ProcessButton(void)
{
    GPIO_PinState button_state = HAL_GPIO_ReadPin(BUTTON_PORT, BUTTON_PIN);
    uint32_t now = HAL_GetTick();
    
    // Check if button is pressed (active LOW)
    bool pressed = (button_state == BUTTON_PRESSED);
    
    // Debounce: only trigger on button press (not release)
    if (pressed && !last_button_state) {
        // Check debounce time
        if ((now - last_button_time) > BUTTON_DEBOUNCE_MS) {
            // Check if in bitmap gallery mode
            if (BitmapGUI_GetMode() == BITMAP_MODE_GALLERY) {
                // Switch to next bitmap
                BitmapGUI_NextBitmap();
            } else {
                // Normal mode - switch to next screen
                GUI_NextScreen();
                GUI_DrawScreen(current_screen);
            }
            last_button_time = now;
        }
    }
    
    last_button_state = pressed;
}

/**
 * @brief Draw text using font
 */
void GUI_DrawText(int16_t x, int16_t y, const char* text, uint16_t color, uint16_t bg, uint8_t size)
{
    const sFONT *font = (size >= 2) ? &Font24 : &Font16;
    ST7789_DrawString(x, y, text, color, bg, font);
}

/**
 * @brief Draw large number
 */
void GUI_DrawLargeNumber(int16_t x, int16_t y, const char* number, uint16_t color)
{
    ST7789_DrawString(x, y, number, color, COLOR_BLACK, &Font24);
}

/**
 * @brief Draw header bar with text
 */
void GUI_DrawHeader(const char* text, uint16_t bg_color)
{
    // Draw header bar (full width, ~40 pixels tall)
    ST7789_DrawRect(0, 0, LCD_WIDTH, 40, bg_color);
    
    // Draw text in header (centered, white text)
    // Calculate text width for centering (approximate: Font16 width is 11 pixels per char)
    int16_t text_x = (LCD_WIDTH - (strlen(text) * 11)) / 2;
    if (text_x < 0) text_x = 10;
    ST7789_DrawString(text_x, 12, text, COLOR_WHITE, bg_color, &Font16);
}

/**
 * @brief Draw battery icon with percentage
 */
void GUI_DrawBatteryIcon(int16_t x, int16_t y, uint8_t percent)
{
    // Battery outline (20x12 pixels)
    ST7789_DrawRect(x, y, 20, 12, COLOR_WHITE);
    // Battery terminal (3x6 pixels on right)
    ST7789_DrawRect(x + 20, y + 3, 3, 6, COLOR_WHITE);
    
    // Battery fill based on percentage
    uint8_t fill_width = (percent * 18) / 100;
    if (fill_width > 0) {
        uint16_t fill_color = (percent > 20) ? COLOR_GREEN : COLOR_RED;
        ST7789_DrawRect(x + 1, y + 1, fill_width, 10, fill_color);
    }
}

/**
 * @brief Draw syringe icon with fill level
 */
void GUI_DrawSyringe(int16_t x, int16_t y, uint8_t fill_percent)
{
    // Syringe body (rectangle, 30x80 pixels)
    ST7789_DrawRect(x, y, 30, 80, COLOR_WHITE);
    
    // Syringe plunger (top, 30x10 pixels)
    ST7789_DrawRect(x, y, 30, 10, COLOR_WHITE);
    
    // Syringe needle (bottom, 5x15 pixels)
    ST7789_DrawRect(x + 12, y + 80, 5, 15, COLOR_WHITE);
    
    // Fill level (liquid inside syringe)
    if (fill_percent > 0) {
        uint8_t fill_height = (fill_percent * 70) / 100;  // 70 pixels max (80 - 10 for plunger)
        int16_t fill_y = y + 10 + (70 - fill_height);
        uint16_t fill_color = (fill_percent > 20) ? COLOR_BLUE : COLOR_RED;
        ST7789_DrawRect(x + 2, fill_y, 26, fill_height, fill_color);
    }
}

/**
 * @brief Draw Delivery Status screen
 */
static void GUI_DrawDeliveryStatus(void)
{
    // Draw background bitmap image (using Image 8)
    ST7789_DrawImageBytes(0, 0, 
                         GIMAGE_8_WIDTH, 
                         GIMAGE_8_HEIGHT, 
                         gImage_8);
}

/**
 * @brief Draw Cassette Low screen
 */
static void GUI_DrawCassetteLow(void)
{
    // Draw background bitmap image (using Image 12)
    ST7789_DrawImageBytes(0, 0, 
                         GIMAGE_12_WIDTH, 
                         GIMAGE_12_HEIGHT, 
                         gImage_12);
    
    // Overlay dynamic text if needed (e.g., for changing values)
    // The bitmap already contains the static layout
}

/**
 * @brief Draw specified screen
 */
void GUI_DrawScreen(screen_type_t screen)
{
    switch (screen) {
        case SCREEN_DELIVERY_STATUS:
            GUI_DrawDeliveryStatus();
            break;
        case SCREEN_CASSETTE_LOW:
            GUI_DrawCassetteLow();
            break;
        default:
            break;
    }
}

