# LCD + SD Card Integration Plan

## Hardware Components

1. **SD Card Shield**: HiLetgo Stackable SD Card Shield (Arduino-compatible)
   - Interface: SPI
   - Typical pins: CS, SCK, MISO, MOSI, VCC, GND

2. **LCD Display**: Amazon B081NBBRWS
   - Interface: Likely SPI (need to verify controller chip)
   - Typical pins: CS, DC, RST, SCK, MISO, MOSI, VCC, GND, BL (backlight)

## Pin Assignment Plan

### Current Pin Usage
- PC0: LPUART1_RX (UART)
- PC1: LPUART1_TX (UART)  
- PA5: LED (LD2)

### Proposed Pin Assignments

**SPI2 Bus (Shared between SD Card and LCD):**
- PB13: SPI2_SCK (Clock)
- PB14: SPI2_MISO (Master In Slave Out)
- PB15: SPI2_MOSI (Master Out Slave In)

**SD Card Control:**
- PB12: SD_CS (Chip Select)
- PB11: SD_CD (Card Detect - optional)

**LCD Control:**
- PB10: LCD_CS (Chip Select)
- PB1: LCD_DC (Data/Command)
- PB0: LCD_RST (Reset)
- PB2: LCD_BL (Backlight - optional)

**Power:**
- 3.3V: CN7 pin 1 or CN8 pin 1
- GND: Any GND pin on CN7/CN8

## Implementation Steps

### Phase 1: SPI Configuration
1. Add SPI2 HAL driver to Makefile
2. Configure SPI2 in CubeMX or manually
3. Initialize SPI2 in main.c
4. Test SPI communication

### Phase 2: SD Card Integration
1. Add FatFS library (or use HAL SD card driver)
2. Implement SD card initialization
3. Implement file read/write functions
4. Add QA Agent tasks for SD card operations

### Phase 3: LCD Integration
1. Identify LCD controller chip (ILI9341, ST7735, etc.)
2. Add LCD driver library
3. Implement LCD initialization
4. Implement display functions (text, graphics)
5. Add QA Agent tasks for LCD operations

### Phase 4: Combined Functionality
1. Display SD card file list on LCD
2. Read file from SD card and display on LCD
3. Create demo applications

## Libraries Needed

1. **FatFS** - For SD card file system
   - Source: STM32CubeU5 Middlewares/FatFs
   - Or: Use HAL SD card driver

2. **LCD Driver** - Depends on controller chip
   - ILI9341: Use existing STM32 libraries
   - ST7735: Use existing STM32 libraries
   - Or: Generic SPI LCD driver

## QA Agent Tasks to Add

- TASK 3: LCD_INIT - Initialize LCD display
- TASK 4: LCD_CLEAR - Clear LCD screen
- TASK 5: LCD_TEXT - Display text on LCD
- TASK 6: SD_INIT - Initialize SD card
- TASK 7: SD_READ - Read file from SD card
- TASK 8: SD_WRITE - Write file to SD card
- TASK 9: SD_LIST - List files on SD card
- TASK 10: LCD_SD_DEMO - Combined demo (read file, display on LCD)

## Next Steps

1. Verify LCD controller chip type
2. Confirm pin assignments work with hardware
3. Start with SPI2 configuration
4. Add SD card support first (simpler)
5. Then add LCD support
6. Finally integrate both

