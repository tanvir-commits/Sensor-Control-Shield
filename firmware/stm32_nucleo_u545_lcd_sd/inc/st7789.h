#ifndef ST7789_H
#define ST7789_H

#include "main.h"
#include "fonts/fonts.h"
#include <stdint.h>
#include <stdbool.h>

/* ST7789 LCD Pin Definitions - Arduino wiring */
/* Note: CS (D10/PC9) conflicts with SD card - they share SPI1 but use different CS */
#define LCD_CS_PIN          GPIO_PIN_9   // D10 (PC9) - CONFLICTS with SD card CS!
#define LCD_CS_PORT         GPIOC
#define LCD_DC_PIN          GPIO_PIN_8   // D7 (PA8) - per datasheet
#define LCD_DC_PORT         GPIOA
#define LCD_RST_PIN         GPIO_PIN_7   // D8 (PC7) - per datasheet D8=PC7
#define LCD_RST_PORT        GPIOC
#define LCD_BL_PIN          GPIO_PIN_6   // D9 (PC6) - TIM3_CH1/PWM
#define LCD_BL_PORT         GPIOC

/* ST7789 uses SPI1 (shared with SD card) */
#define LCD_SPI             SPI1

/* ST7789 Display Parameters */
#define LCD_WIDTH           240
#define LCD_HEIGHT          320
#define LCD_ROTATION_0      0
#define LCD_ROTATION_90     1
#define LCD_ROTATION_180    2
#define LCD_ROTATION_270    3

/* ST7789 Command Definitions */
#define ST7789_NOP          0x00
#define ST7789_SWRESET      0x01
#define ST7789_RDDID        0x04
#define ST7789_RDDST        0x09
#define ST7789_SLPIN        0x10
#define ST7789_SLPOUT       0x11
#define ST7789_PTLON        0x12
#define ST7789_NORON        0x13
#define ST7789_INVOFF       0x20
#define ST7789_INVON        0x21
#define ST7789_DISPOFF      0x28
#define ST7789_DISPON       0x29
#define ST7789_CASET        0x2A
#define ST7789_RASET        0x2B
#define ST7789_RAMWR        0x2C
#define ST7789_RAMRD        0x2E
#define ST7789_PTLAR        0x30
#define ST7789_COLMOD       0x3A
#define ST7789_MADCTL       0x36
#define ST7789_MADCTL_MY    0x80
#define ST7789_MADCTL_MX    0x40
#define ST7789_MADCTL_MV    0x20
#define ST7789_MADCTL_ML    0x10
#define ST7789_MADCTL_RGB   0x00
#define ST7789_MADCTL_MH    0x04
#define ST7789_RDID1        0xDA
#define ST7789_RDID2        0xDB
#define ST7789_RDID3        0xDC
#define ST7789_RDID4        0xDD
#define ST7789_FRMCTR1      0xB1
#define ST7789_FRMCTR2      0xB2
#define ST7789_FRMCTR3      0xB3
#define ST7789_INVCTR       0xB4
#define ST7789_DISSET5      0xB6
#define ST7789_PWCTR1       0xC0
#define ST7789_PWCTR2       0xC1
#define ST7789_PWCTR3       0xC2
#define ST7789_PWCTR4       0xC3
#define ST7789_PWCTR5       0xC4
#define ST7789_VMCTR1       0xC5
#define ST7789_GMCTRP1      0xE0
#define ST7789_GMCTRN1      0xE1
#define ST7789_PWCTR6       0xFC

/* Color Definitions (RGB565 format) */
#define COLOR_BLACK         0x0000
#define COLOR_WHITE         0xFFFF
#define COLOR_RED           0xF800
#define COLOR_GREEN         0x07E0
#define COLOR_BLUE          0x001F
#define COLOR_YELLOW        0xFFE0
#define COLOR_CYAN          0x07FF
#define COLOR_MAGENTA      0xF81F

/* Function Prototypes */
bool ST7789_Init(void);
void ST7789_Reset(void);
void ST7789_SetRotation(uint8_t rotation);
void ST7789_FillScreen(uint16_t color);
void ST7789_DrawPixel(int16_t x, int16_t y, uint16_t color);
void ST7789_DrawRect(int16_t x, int16_t y, int16_t w, int16_t h, uint16_t color);
void ST7789_DrawChar(int16_t x, int16_t y, char c, uint16_t color, uint16_t bg, const sFONT *font);
void ST7789_DrawString(int16_t x, int16_t y, const char *str, uint16_t color, uint16_t bg, const sFONT *font);
void ST7789_DrawImage(int16_t x, int16_t y, int16_t w, int16_t h, const uint16_t *image);
void ST7789_DrawImageBytes(int16_t x, int16_t y, int16_t w, int16_t h, const uint8_t *image);
void ST7789_SetBacklight(bool on);
void ST7789_SetBacklightBrightness(uint8_t percent);

/* Internal Functions */
void ST7789_WriteCommand(uint8_t cmd);
void ST7789_WriteData(uint8_t data);
void ST7789_WriteData16(uint16_t data);
void ST7789_SetAddrWindow(uint16_t x0, uint16_t y0, uint16_t x1, uint16_t y1);
void ST7789_CS_Low(void);
void ST7789_CS_High(void);
void ST7789_DC_Command(void);
void ST7789_DC_Data(void);
void ST7789_RST_Low(void);
void ST7789_RST_High(void);

#endif /* ST7789_H */

