# STM32U545 LCD + SD Card Pin Assignments

## Current Pin Usage

| Pin | Function | Notes |
|-----|----------|-------|
| PC0 | LPUART1_RX | UART receive (CN7 pin 38) |
| PC1 | LPUART1_TX | UART transmit (CN7 pin 36) |
| PA5 | LED (LD2) | On-board LED |

## Proposed Pin Assignments for LCD + SD Card

### Option 1: Shared SPI Bus (Recommended)
Both SD card and LCD share the same SPI bus but use different CS pins.

**SPI2 Configuration:**
| Signal | STM32 Pin | CN7 Pin | Function |
|--------|-----------|--------|----------|
| SPI2_SCK | PB13 | 30 | SPI Clock (shared) |
| SPI2_MISO | PB14 | 28 | SPI MISO (shared) |
| SPI2_MOSI | PB15 | 26 | SPI MOSI (shared) |

**SD Card Control Pins:**
| Signal | STM32 Pin | CN7 Pin | Function |
|--------|-----------|--------|----------|
| SD_CS | PB12 | 32 | SD Card Chip Select |
| SD_CD | PB11 | 34 | SD Card Detect (optional) |

**LCD Control Pins:**
| Signal | STM32 Pin | CN7 Pin | Function |
|--------|-----------|--------|----------|
| LCD_CS | PB10 | 36 | LCD Chip Select |
| LCD_DC | PB1 | 38 | LCD Data/Command |
| LCD_RST | PB0 | 40 | LCD Reset |
| LCD_BL | PB2 | 42 | LCD Backlight (optional) |

**Power:**
- VCC: 3.3V (CN7 pin 1 or CN8 pin 1)
- GND: GND (any GND pin on CN7/CN8)

### Option 2: Separate SPI Buses
Use SPI2 for SD card and SPI3 for LCD (if available).

**SPI2 for SD Card:**
- PB13: SCK
- PB14: MISO  
- PB15: MOSI
- PB12: CS

**SPI3 for LCD:**
- PC10: SCK
- PC11: MISO
- PC12: MOSI
- PB10: CS
- PB1: DC
- PB0: RST

## Notes

- All pins are on CN7 connector (Arduino-compatible header)
- SPI2 is a good choice as it doesn't conflict with LPUART1 or LED
- Both devices can share SPI bus with different CS pins (most common approach)
- Verify LCD controller type to ensure correct driver/library

## Next Steps

1. Verify LCD controller chip (ILI9341, ST7735, etc.)
2. Configure SPI2 in code
3. Add FatFS library for SD card
4. Add LCD driver library
5. Implement initialization functions
6. Add QA Agent tasks for LCD/SD operations

