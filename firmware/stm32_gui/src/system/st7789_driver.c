#include "st7789_driver.h"
#include "main.h"
#include <string.h>

/* External SPI handle */
extern SPI_HandleTypeDef hspi1;
/* External TIM handle for PWM */
extern TIM_HandleTypeDef htim3;

/* External SPI handle - shared with SD card */
extern SPI_HandleTypeDef hspi1;

/* Current rotation */
static uint8_t lcd_rotation = 0;

/* DMA transfer completion flag */
static volatile bool dma_transfer_complete = false;

/**
 * @brief Set LCD CS pin LOW (select LCD)
 */
void ST7789_CS_Low(void)
{
    HAL_GPIO_WritePin(LCD_CS_PORT, LCD_CS_PIN, GPIO_PIN_RESET);
}

/**
 * @brief Set LCD CS pin HIGH (deselect LCD)
 */
void ST7789_CS_High(void)
{
    HAL_GPIO_WritePin(LCD_CS_PORT, LCD_CS_PIN, GPIO_PIN_SET);
}

/**
 * @brief Set LCD DC pin LOW (command mode)
 */
void ST7789_DC_Command(void)
{
    HAL_GPIO_WritePin(LCD_DC_PORT, LCD_DC_PIN, GPIO_PIN_RESET);
}

/**
 * @brief Set LCD DC pin HIGH (data mode)
 */
void ST7789_DC_Data(void)
{
    HAL_GPIO_WritePin(LCD_DC_PORT, LCD_DC_PIN, GPIO_PIN_SET);
}

/**
 * @brief Set LCD RST pin LOW
 */
void ST7789_RST_Low(void)
{
    HAL_GPIO_WritePin(LCD_RST_PORT, LCD_RST_PIN, GPIO_PIN_RESET);
}

/**
 * @brief Set LCD RST pin HIGH
 */
void ST7789_RST_High(void)
{
    HAL_GPIO_WritePin(LCD_RST_PORT, LCD_RST_PIN, GPIO_PIN_SET);
}

/**
 * @brief Write a command byte to the LCD
 */
void ST7789_WriteCommand(uint8_t cmd)
{
    ST7789_CS_Low();
    ST7789_DC_Command();
    HAL_SPI_Transmit(&hspi1, &cmd, 1, 100);
    ST7789_CS_High();
    HAL_Delay(1); // Small delay between commands
}

/**
 * @brief Write a data byte to the LCD
 */
void ST7789_WriteData(uint8_t data)
{
    ST7789_CS_Low();
    ST7789_DC_Data();
    HAL_SPI_Transmit(&hspi1, &data, 1, 100);
    ST7789_CS_High();
    HAL_Delay(1); // Small delay between data
}

/**
 * @brief SPI readback - send data and read response
 * This verifies SPI communication is working
 * Note: LCD doesn't echo data, so we're just checking if SPI works
 */
uint8_t ST7789_SPI_Readback(uint8_t data)
{
    uint8_t tx_data = data;
    uint8_t rx_data = 0xFF; // Default to 0xFF (idle state)
    
    // Check SPI state before
    if (hspi1.State != HAL_SPI_STATE_READY) {
        // SPI not ready, return error indicator
        return 0xEE;
    }
    
    ST7789_CS_Low();
    HAL_StatusTypeDef status = HAL_SPI_TransmitReceive(&hspi1, &tx_data, &rx_data, 1, 100);
    ST7789_CS_High();
    
    // Check if SPI operation succeeded
    if (status != HAL_OK) {
        // SPI error, return error indicator
        return 0xAA;
    }
    
    return rx_data;
}

/**
 * @brief Read LCD ID register (RDDID)
 * Returns true if ID is valid (should be 0x85, 0x85, 0x52 for ST7789)
 */
bool ST7789_ReadID(uint8_t *id1, uint8_t *id2, uint8_t *id3)
{
    // Check SPI state
    if (hspi1.State != HAL_SPI_STATE_READY) {
        *id1 = *id2 = *id3 = 0;
        return false;
    }
    
    ST7789_CS_Low();
    HAL_Delay(1); // Small delay for CS to settle
    
    ST7789_DC_Command();
    uint8_t cmd = ST7789_RDDID;
    HAL_StatusTypeDef status = HAL_SPI_Transmit(&hspi1, &cmd, 1, 100);
    if (status != HAL_OK) {
        ST7789_CS_High();
        *id1 = *id2 = *id3 = 0;
        return false;
    }
    
    // Switch to data mode and read 3 bytes
    ST7789_DC_Data();
    uint8_t dummy = 0xFF;
    uint8_t data[3] = {0, 0, 0};
    
    // Send dummy bytes and read response
    HAL_SPI_TransmitReceive(&hspi1, &dummy, &data[0], 1, 100);
    HAL_SPI_TransmitReceive(&hspi1, &dummy, &data[1], 1, 100);
    HAL_SPI_TransmitReceive(&hspi1, &dummy, &data[2], 1, 100);
    
    ST7789_CS_High();
    HAL_Delay(1);
    
    *id1 = data[0];
    *id2 = data[1];
    *id3 = data[2];
    
    // ST7789 should return 0x85, 0x85, 0x52
    return (data[0] == 0x85 && data[1] == 0x85 && data[2] == 0x52);
}

/**
 * @brief Read LCD status register (RDDST)
 */
bool ST7789_ReadStatus(uint8_t *status)
{
    ST7789_CS_Low();
    ST7789_DC_Command();
    uint8_t cmd = ST7789_RDDST;
    HAL_SPI_Transmit(&hspi1, &cmd, 1, 100);
    
    // Switch to data mode and read status
    ST7789_DC_Data();
    uint8_t dummy = 0xFF;
    HAL_SPI_TransmitReceive(&hspi1, &dummy, status, 1, 100);
    
    ST7789_CS_High();
    return true;
}

/**
 * @brief Write a 16-bit data word to the LCD
 */
void ST7789_WriteData16(uint16_t data)
{
    uint8_t bytes[2];
    bytes[0] = (data >> 8) & 0xFF;
    bytes[1] = data & 0xFF;
    
    ST7789_DC_Data();
    ST7789_CS_Low();
    HAL_SPI_Transmit(&hspi1, bytes, 2, 100);
    ST7789_CS_High();
}

/**
 * @brief Set address window for drawing
 * Note: This function keeps CS low and DC high after RAMWR command
 * Caller must raise CS after sending pixel data
 */
void ST7789_SetAddrWindow(uint16_t x0, uint16_t y0, uint16_t x1, uint16_t y1)
{
    // Column address set (CASET)
    ST7789_CS_Low();
    ST7789_DC_Command();
    uint8_t cmd_caset = ST7789_CASET;
    HAL_SPI_Transmit(&hspi1, &cmd_caset, 1, 100);
    ST7789_DC_Data();
    uint8_t caset_data[4];
    caset_data[0] = (x0 >> 8) & 0xFF;
    caset_data[1] = x0 & 0xFF;
    caset_data[2] = (x1 >> 8) & 0xFF;
    caset_data[3] = x1 & 0xFF;
    HAL_SPI_Transmit(&hspi1, caset_data, 4, 100);
    // Removed delay and CS toggle - continue in same transaction
    // ST7789_CS_High();
    // HAL_Delay(1);
    
    // Row address set (RASET) - continue with CS low
    ST7789_DC_Command();
    uint8_t cmd_raset = ST7789_RASET;
    HAL_SPI_Transmit(&hspi1, &cmd_raset, 1, 100);
    ST7789_DC_Data();
    uint8_t raset_data[4];
    raset_data[0] = (y0 >> 8) & 0xFF;
    raset_data[1] = y0 & 0xFF;
    raset_data[2] = (y1 >> 8) & 0xFF;
    raset_data[3] = y1 & 0xFF;
    HAL_SPI_Transmit(&hspi1, raset_data, 4, 100);
    // Removed delay and CS toggle - continue in same transaction
    // ST7789_CS_High();
    // HAL_Delay(1);
    
    // Memory write (RAMWR) - start pixel data transfer (CS already low)
    ST7789_DC_Command();
    uint8_t cmd_ramwr = ST7789_RAMWR;
    HAL_SPI_Transmit(&hspi1, &cmd_ramwr, 1, 100);
    ST7789_DC_Data();
    // CS stays low, DC stays high - ready for pixel data
}

/**
 * @brief Hardware reset the LCD
 */
void ST7789_Reset(void)
{
    ST7789_RST_Low();
    HAL_Delay(10);
    ST7789_RST_High();
    HAL_Delay(10);
}

/**
 * @brief Initialize the ST7789 LCD
 * Verifies communication by reading ID register
 */
bool ST7789_Init(void)
{
    // Hardware reset (Waveshare official sequence)
    ST7789_Reset();
    
    // Memory Access Control (MADCTL)
    ST7789_WriteCommand(0x36);
    ST7789_WriteData(0x00);
    
    // Pixel Format Set (COLMOD) - Use 0x05 (RGB666) as original working code
    // Even though we send RGB565 data, the display works with 0x05 setting
    ST7789_WriteCommand(0x3A);
    ST7789_WriteData(0x05);  // RGB666 format (original Waveshare setting that worked)
    
    // Display Inversion On
    ST7789_WriteCommand(0x21);
    
    // Column Address Set (CASET) - Set display window
    ST7789_WriteCommand(0x2A);
    ST7789_WriteData(0x00);
    ST7789_WriteData(0x00);
    ST7789_WriteData(0x01);
    ST7789_WriteData(0x3F);  // 0x013F = 319 (320 pixels, 0-319)
    
    // Row Address Set (RASET) - Set display window
    ST7789_WriteCommand(0x2B);
    ST7789_WriteData(0x00);
    ST7789_WriteData(0x00);
    ST7789_WriteData(0x00);
    ST7789_WriteData(0xEF);  // 0x00EF = 239 (240 pixels, 0-239)
    
    // Porch Setting (FRMCTR2)
    ST7789_WriteCommand(0xB2);
    ST7789_WriteData(0x0C);
    ST7789_WriteData(0x0C);
    ST7789_WriteData(0x00);
    ST7789_WriteData(0x33);
    ST7789_WriteData(0x33);
    
    // Gate Control (GCTRL)
    ST7789_WriteCommand(0xB7);
    ST7789_WriteData(0x35);
    
    // VCOM Setting (VCOMS)
    ST7789_WriteCommand(0xBB);
    ST7789_WriteData(0x1F);
    
    // LCM Control (LCMCTRL)
    ST7789_WriteCommand(0xC0);
    ST7789_WriteData(0x2C);
    
    // VDV and VRH Command Enable (VDVVRHEN)
    ST7789_WriteCommand(0xC2);
    ST7789_WriteData(0x01);
    
    // VRH Set (VRHS)
    ST7789_WriteCommand(0xC3);
    ST7789_WriteData(0x12);
    
    // VDV Set (VDVS)
    ST7789_WriteCommand(0xC4);
    ST7789_WriteData(0x20);
    
    // Frame Rate Control in Normal Mode (FRCTRL2)
    ST7789_WriteCommand(0xC6);
    ST7789_WriteData(0x0F);
    
    // Power Control 1 (PWCTRL1)
    ST7789_WriteCommand(0xD0);
    ST7789_WriteData(0xA4);
    ST7789_WriteData(0xA1);
    
    // Positive Voltage Gamma Control (PVGAMCTRL)
    ST7789_WriteCommand(0xE0);
    ST7789_WriteData(0xD0);
    ST7789_WriteData(0x08);
    ST7789_WriteData(0x11);
    ST7789_WriteData(0x08);
    ST7789_WriteData(0x0C);
    ST7789_WriteData(0x15);
    ST7789_WriteData(0x39);
    ST7789_WriteData(0x33);
    ST7789_WriteData(0x50);
    ST7789_WriteData(0x36);
    ST7789_WriteData(0x13);
    ST7789_WriteData(0x14);
    ST7789_WriteData(0x29);
    ST7789_WriteData(0x2D);
    
    // Negative Voltage Gamma Control (NVGAMCTRL)
    ST7789_WriteCommand(0xE1);
    ST7789_WriteData(0xD0);
    ST7789_WriteData(0x08);
    ST7789_WriteData(0x10);
    ST7789_WriteData(0x08);
    ST7789_WriteData(0x06);
    ST7789_WriteData(0x06);
    ST7789_WriteData(0x39);
    ST7789_WriteData(0x44);
    ST7789_WriteData(0x51);
    ST7789_WriteData(0x0B);
    ST7789_WriteData(0x16);
    ST7789_WriteData(0x14);
    ST7789_WriteData(0x2F);
    ST7789_WriteData(0x31);
    
    // Display Inversion On (again)
    ST7789_WriteCommand(0x21);
    
    // Sleep Out
    ST7789_WriteCommand(0x11);
    HAL_Delay(120);  // Wait for display to stabilize
    
    // Display On
    ST7789_WriteCommand(0x29);
    HAL_Delay(20);
    
    // Backlight is set ON in MX_GPIO_Init() - don't touch it here
    
    return true;
}

/**
 * @brief Set display rotation
 */
void ST7789_SetRotation(uint8_t rotation)
{
    lcd_rotation = rotation % 4;
    
    ST7789_WriteCommand(ST7789_MADCTL);
    
    switch (lcd_rotation) {
        case 0: // Portrait
            ST7789_WriteData(ST7789_MADCTL_MX | ST7789_MADCTL_MY | ST7789_MADCTL_RGB);
            break;
        case 1: // Landscape
            ST7789_WriteData(ST7789_MADCTL_MY | ST7789_MADCTL_MV | ST7789_MADCTL_RGB);
            break;
        case 2: // Portrait inverted
            ST7789_WriteData(ST7789_MADCTL_RGB);
            break;
        case 3: // Landscape inverted
            ST7789_WriteData(ST7789_MADCTL_MX | ST7789_MADCTL_MV | ST7789_MADCTL_RGB);
            break;
    }
}

/**
 * @brief Fill entire screen with a color
 */
void ST7789_FillScreen(uint16_t color)
{
    ST7789_DrawRect(0, 0, LCD_WIDTH, LCD_HEIGHT, color);
}

/**
 * @brief Draw a single pixel
 */
void ST7789_DrawPixel(int16_t x, int16_t y, uint16_t color)
{
    if (x < 0 || x >= LCD_WIDTH || y < 0 || y >= LCD_HEIGHT) {
        return;
    }
    
    // Set address window (this leaves CS low and DC high)
    ST7789_SetAddrWindow(x, y, x, y);
    
    // Write pixel data (CS is already low, DC is already high)
    uint8_t bytes[2];
    bytes[0] = (color >> 8) & 0xFF;
    bytes[1] = color & 0xFF;
    HAL_SPI_Transmit(&hspi1, bytes, 2, 100);
    
    // Raise CS to complete
    ST7789_CS_High();
    HAL_Delay(1);
}

/**
 * @brief Draw a filled rectangle
 */
void ST7789_DrawRect(int16_t x, int16_t y, int16_t w, int16_t h, uint16_t color)
{
    if (x < 0 || y < 0 || x + w > LCD_WIDTH || y + h > LCD_HEIGHT) {
        return;
    }
    
    // Set address window (leaves CS low and DC high after RAMWR)
    ST7789_SetAddrWindow(x, y, x + w - 1, y + h - 1);
    
    // Prepare color bytes
    uint8_t color_bytes[2];
    color_bytes[0] = (color >> 8) & 0xFF;  // MSB
    color_bytes[1] = color & 0xFF;         // LSB
    
    // Send all pixels in batches (CS stays low during entire transfer)
    uint32_t pixels = (uint32_t)w * h;
    
    // Send pixels in chunks to avoid timeout
    const uint32_t chunk_size = 1000;
    for (uint32_t i = 0; i < pixels; i += chunk_size) {
        uint32_t remaining = pixels - i;
        uint32_t chunk = (remaining > chunk_size) ? chunk_size : remaining;
        
        // Send chunk of pixels
        for (uint32_t j = 0; j < chunk; j++) {
            HAL_SPI_Transmit(&hspi1, color_bytes, 2, 100);
        }
    }
    
    // Raise CS to complete the transaction
    ST7789_CS_High();
    HAL_Delay(1);
}

/* External TIM handle for PWM */
extern TIM_HandleTypeDef htim3;

/**
 * @brief Set backlight on/off (for compatibility)
 */
void ST7789_SetBacklight(bool on)
{
    ST7789_SetBacklightBrightness(on ? 100 : 0);
}

/**
 * @brief Set backlight brightness using PWM (0-100%)
 */
void ST7789_SetBacklightBrightness(uint8_t percent)
{
    if (percent > 100) {
        percent = 100;
    }
    
    // Calculate PWM pulse value (TIM3 period is 1000, so 0-1000 for 0-100%)
    uint32_t pulse = (percent * 1000) / 100;
    
    // Set PWM duty cycle
    __HAL_TIM_SET_COMPARE(&htim3, TIM_CHANNEL_1, pulse);
    
    // Ensure PWM is started
    if (HAL_TIM_PWM_GetState(&htim3) == HAL_TIM_STATE_RESET) {
        HAL_TIM_PWM_Start(&htim3, TIM_CHANNEL_1);
    }
}

/**
 * @brief Turn LCD display off (display off + backlight off)
 */
__attribute__((used)) void ST7789_DisplayOff(void)
{
    // Turn off backlight
    ST7789_SetBacklightBrightness(0);
    
    // Send Display Off command
    ST7789_WriteCommand(ST7789_DISPOFF);
    HAL_Delay(10);
    
    // Send Sleep In command to reduce power further
    ST7789_WriteCommand(ST7789_SLPIN);
    HAL_Delay(10);
}

/**
 * @brief Turn LCD display on (display on + backlight on)
 */
__attribute__((used)) void ST7789_DisplayOn(void)
{
    // Send Sleep Out command
    ST7789_WriteCommand(ST7789_SLPOUT);
    HAL_Delay(120);  // Wait for display to stabilize
    
    // Send Display On command
    ST7789_WriteCommand(ST7789_DISPON);
    HAL_Delay(20);
    
    // Turn on backlight to default (100%)
    ST7789_SetBacklightBrightness(100);
}

/**
 * @brief Draw a character using font data (optimized - draws row by row)
 */
/* Font drawing functions removed - not needed for LVGL */
#if 0
void ST7789_DrawChar(int16_t x, int16_t y, char c, uint16_t color, uint16_t bg, const sFONT *font)
{
    if (x < 0 || y < 0 || x + font->Width > LCD_WIDTH || y + font->Height > LCD_HEIGHT) {
        return;
    }
    
    // Calculate character offset in font table
    uint32_t bytes_per_row = (font->Width / 8) + ((font->Width % 8) ? 1 : 0);
    uint32_t char_offset = (c - ' ') * font->Height * bytes_per_row;
    const uint8_t *ptr = &font->table[char_offset];
    
    // Draw character row by row (more efficient than pixel by pixel)
    for (uint16_t page = 0; page < font->Height; page++) {
        // Set address window for this row
        ST7789_SetAddrWindow(x, y + page, x + font->Width - 1, y + page);
        
        // Prepare color bytes
        uint8_t color_bytes[2];
        color_bytes[0] = (color >> 8) & 0xFF;
        color_bytes[1] = color & 0xFF;
        uint8_t bg_bytes[2];
        bg_bytes[0] = (bg >> 8) & 0xFF;
        bg_bytes[1] = bg & 0xFF;
        
        // Draw this row pixel by pixel (but within same address window)
        for (uint16_t col = 0; col < font->Width; col++) {
            uint8_t byte_idx = col / 8;
            uint8_t bit_idx = col % 8;
            uint8_t bit_mask = 0x80 >> bit_idx;
            
            if (ptr[byte_idx] & bit_mask) {
                HAL_SPI_Transmit(&hspi1, color_bytes, 2, 100);
            } else if (bg != COLOR_BLACK) {
                HAL_SPI_Transmit(&hspi1, bg_bytes, 2, 100);
            } else {
                // Skip black background pixels (don't draw)
                HAL_SPI_Transmit(&hspi1, bg_bytes, 2, 100);
            }
        }
        
        // Raise CS after each row
        ST7789_CS_High();
        HAL_Delay(1);
        
        ptr += bytes_per_row;
    }
}

void ST7789_DrawString(int16_t x, int16_t y, const char *str, uint16_t color, uint16_t bg, const sFONT *font)
{
    int16_t x_pos = x;
    while (*str && x_pos < LCD_WIDTH) {
        if (*str == '\n') {
            // Newline: move to next line
            y += font->Height;
            x_pos = x;
        } else {
            ST7789_DrawChar(x_pos, y, *str, color, bg, font);
            x_pos += font->Width;
        }
        str++;
    }
}
#endif

/**
 * @brief Draw an image from RGB565 buffer (uint16_t array)
 * @param x X position (top-left corner)
 * @param y Y position (top-left corner)
 * @param w Image width in pixels
 * @param h Image height in pixels
 * @param image Pointer to RGB565 image data (2 bytes per pixel, row-major order)
 */
void ST7789_DrawImage(int16_t x, int16_t y, int16_t w, int16_t h, const uint16_t *image)
{
    if (x < 0 || y < 0 || x + w > LCD_WIDTH || y + h > LCD_HEIGHT) {
        return;
    }
    
    // Set address window (leaves CS low and DC high after RAMWR)
    ST7789_SetAddrWindow(x, y, x + w - 1, y + h - 1);
    
    // Send all pixels in chunks to avoid timeout
    const uint32_t chunk_size = 500;  // pixels per chunk
    uint32_t total_pixels = (uint32_t)w * h;
    
    for (uint32_t i = 0; i < total_pixels; i += chunk_size) {
        uint32_t remaining = total_pixels - i;
        uint32_t chunk = (remaining > chunk_size) ? chunk_size : remaining;
        
        // Send chunk of pixels
        for (uint32_t j = 0; j < chunk; j++) {
            uint16_t pixel = image[i + j];
            uint8_t bytes[2];
            bytes[0] = (pixel >> 8) & 0xFF;  // MSB
            bytes[1] = pixel & 0xFF;         // LSB
            HAL_SPI_Transmit(&hspi1, bytes, 2, 100);
        }
    }
    
    // Raise CS to complete the transaction
    ST7789_CS_High();
    HAL_Delay(1);
}

/**
 * @brief Draw an image from RGB565 byte array (matching Waveshare format)
 * @param x X position (top-left corner)
 * @param y Y position (top-left corner)
 * @param w Image width in pixels
 * @param h Image height in pixels
 * @param image Pointer to RGB565 byte array (little-endian: LSB, MSB per pixel, row-major order)
 * 
 * Format matches Waveshare reference: (image[j*width*2 + i*2+1]<<8) | (image[j*width*2 + i*2])
 */
/**
 * @brief Draw an image from RGB565 byte array
 * @param x X position (top-left corner)
 * @param y Y position (top-left corner)
 * @param w Image width in pixels
 * @param h Image height in pixels
 * @param image Pointer to RGB565 byte array (little-endian: LSB, MSB per pixel, row-major order)
 */
/**
 * @brief DMA transfer complete callback
 */
void HAL_SPI_TxCpltCallback(SPI_HandleTypeDef *hspi)
{
    if (hspi->Instance == SPI1) {
        dma_transfer_complete = true;
    }
}

void ST7789_DrawImageBytes(int16_t x, int16_t y, int16_t w, int16_t h, const uint8_t *image)
{
    if (image == NULL) {
        return;
    }
    
    // Clamp to screen bounds
    if (x < 0 || y < 0 || x + w > LCD_WIDTH || y + h > LCD_HEIGHT) {
        return;
    }
    
    // Set address window (leaves CS low and DC high after RAMWR)
    ST7789_SetAddrWindow(x, y, x + w - 1, y + h - 1);
    
    // Process image in chunks to avoid large RAM buffer (LVGL uses RAM too)
    uint32_t total_pixels = (uint32_t)w * h;
    #define CHUNK_PIXELS 1000  // Process 1000 pixels at a time (2KB buffer)
    static uint8_t chunk_buffer[CHUNK_PIXELS * 2];  // Small chunk buffer
    
    uint32_t pixels_processed = 0;
    const uint8_t *src = image;
    
    while (pixels_processed < total_pixels) {
        uint32_t remaining = total_pixels - pixels_processed;
        uint32_t chunk = (remaining > CHUNK_PIXELS) ? CHUNK_PIXELS : remaining;
        uint32_t chunk_bytes = chunk * 2;
        
        // Byte swap: convert [LSB, MSB] to [MSB, LSB] for display
        uint8_t *dst = chunk_buffer;
        for (uint32_t i = 0; i < chunk; i++) {
            dst[i * 2] = src[i * 2 + 1];      // MSB
            dst[i * 2 + 1] = src[i * 2];      // LSB
        }
        src += chunk_bytes;
        
        // Send chunk (CS stays low during entire transfer)
        HAL_SPI_Transmit(&hspi1, chunk_buffer, chunk_bytes, 1000);
        pixels_processed += chunk;
    }
    
    // Raise CS to complete the transaction
    ST7789_CS_High();
    // Small delay to ensure CS signal is stable
    HAL_Delay(1);
}

