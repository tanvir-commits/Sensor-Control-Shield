# Hardware Documentation V2

This folder contains the V2 hardware specifications with the following changes from V1:

## Files

- `pin_mapping_V2_UART3_I2C3_GPIO18.csv` - Complete pin mapping for V2
- `V1_TO_V2_CHANGES.md` - Summary of changes from V1 to V2

## Key V2 Features

1. **4-pin GPIO Bank** - Restored using BCM18 to replace BCM5
2. **Second I2C Bus** - I2C3 on BCM4/BCM5 (J16 connector)
3. **No Functionality Loss** - All V1 features maintained

## Quick Reference

**GPIO Bank (J11):**
- Pin 1: BCM18 (pin 12)
- Pin 2: BCM6 (pin 31)
- Pin 3: BCM12 (pin 32)
- Pin 4: BCM13 (pin 33)

**I2C3 Bus (J16):**
- SDA: BCM4 (pin 7)
- SCL: BCM5 (pin 29)

See `V1_TO_V2_CHANGES.md` for detailed change summary.

