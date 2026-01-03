# SD Card Shield Wiring Guide

## Shield Stacking

✅ **The Arduino SD Card Shield CAN stack directly on the NUCLEO-U545RE-Q board!**  
The NUCLEO-U545RE-Q has Arduino Uno V3-compatible headers (CN7), so the shield plugs directly in.

## Automatic Connections (via Stacking)

When the shield is stacked on CN7, these pins connect automatically:

| Shield Pin | Signal | STM32 Pin | Notes |
|------------|--------|-----------|-------|
| D13 | SD_CLK (Clock) | PA5 | SPI1_SCK (Arduino D13) |
| D12 | SD_OUT (MISO) | PA6 | SPI1_MISO (Arduino D12) |
| D11 | SD_IN (MOSI) | PA7 | SPI1_MOSI (Arduino D11) |
| D10 | SD_CS (Chip Select) | **PC9** | Arduino D10 (per UM3062 user manual) |
| VCC | Power | 3.3V | **Set shield switch to 3.3V!** |
| GND | Ground | GND | Connected via header |

## Voltage Setting

**CRITICAL:** The shield has a voltage selection switch/jumper.  
**Set it to 3.3V** (not 5V) because STM32U545 operates at 3.3V logic levels.

## Current Code Configuration

- **CS Pin:** PC9 (Arduino D10 per user manual UM3062)
- **SPI:** SPI1
- **Clock Speed:** Very slow (prescaler 128) for initialization

## Changing the CS Pin

If you wired D10 to a different GPIO pin, edit `inc/sd_card.h`:

```c
#define SD_CS_PIN          GPIO_PIN_X  // Change X to your pin number
#define SD_CS_PORT         GPIOY      // Change Y to your port (GPIOA, GPIOB, etc.)
```

Then update `src/main.c` in `MX_GPIO_Init()` to configure that pin as output.

## Setup Checklist

1. **Stack shield on CN7** - Should align with Arduino header
2. **Set voltage switch to 3.3V** - CRITICAL for STM32U545 (not 5V!)
3. **Insert TF card** - Fully insert into shield slot
4. **Verify D10 pin mapping** - Code uses PB6, but verify this matches your board

## Pin Mapping Verification

Since the TF card is warm, **power (VCC/GND) is connected correctly.**

Automatic connections via stacking:
- ✅ VCC → 3.3V (card is warm = power working)
- ✅ GND → GND
- ✅ D13 (SCK) → PA5 (SPI1_SCK)
- ✅ D12 (MISO) → PA6 (SPI1_MISO)
- ✅ D11 (MOSI) → PA7 (SPI1_MOSI)
- ✅ D10 (CS) → PC9 (confirmed from user manual UM3062)

## Troubleshooting

If the card doesn't respond:
1. **Check voltage switch** - Must be set to 3.3V (not 5V!)
2. **Verify shield is fully seated** - All pins should make contact
3. **Verify D10 pin mapping** - Code uses PB6, but D10 might map to a different pin on NUCLEO-U545RE-Q
4. **Check SPI configuration** - Verify SPI1 is correctly initialized
5. **Verify card is inserted** - TF card must be fully inserted in shield
6. **Try different CS pin** - If PB6 doesn't work, D10 might map to a different GPIO

## Alternative: SDMMC Interface

The STM32U545 has a built-in SDMMC peripheral that can be faster than SPI.  
Consider using an SDMMC-compatible module for better performance.

