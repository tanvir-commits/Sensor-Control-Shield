# STM32 Nucleo U545RE-Q Pin Mapping for LCD

## LCD Pin Assignments (Waveshare 2-inch LCD Module)

### SPI1 Pins (Arduino D11-D13)
- **D13 (SCK/Clock)**: `PA5` - SPI1_SCK
- **D12 (MISO)**: `PA6` - SPI1_MISO (not used for LCD, LCD is write-only)
- **D11 (MOSI)**: `PA7` - SPI1_MOSI

### LCD Control Pins
- **D10 (CS/Chip Select)**: `PC9` - LCD_CS_PIN
- **D9 (BL/Backlight)**: `PC6` - LCD_BL_PIN (TIM3_CH1/PWM capable)
- **D8 (RST/Reset)**: `PC7` - LCD_RST_PIN
- **D7 (DC/Data-Command)**: `PA8` - LCD_DC_PIN

## Summary Table

| Arduino Pin | Function | STM32 Pin | Port | Notes |
|-------------|----------|-----------|------|-------|
| D13 | SCK | PA5 | GPIOA | SPI1 Clock |
| D12 | MISO | PA6 | GPIOA | SPI1 MISO (not used) |
| D11 | MOSI | PA7 | GPIOA | SPI1 MOSI |
| D10 | CS | PC9 | GPIOC | LCD Chip Select |
| D9 | BL | PC6 | GPIOC | Backlight (PWM capable) |
| D8 | RST | PC7 | GPIOC | LCD Reset |
| D7 | DC | PA8 | GPIOA | Data/Command Select |

## Power Pins
- **VCC**: 3.3V (from Nucleo board)
- **GND**: Ground (from Nucleo board)

## Notes
- LCD is write-only (no MISO connection needed)
- CS pin (PC9) conflicts with SD card shield if both are used simultaneously
- Backlight (PC6) can be controlled via GPIO or PWM (TIM3_CH1)
- All pins are configured as output except MISO (PA6) which is not used

