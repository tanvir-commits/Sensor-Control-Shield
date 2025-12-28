# V1 to V2 Hardware Changes Summary

## Overview

V2 adds a second I2C bus (I2C3) while maintaining the 4-pin GPIO bank by replacing BCM5 with BCM18.

---

## What Changed

### 1. GPIO Bank (J11) - Restored to 4 Pins

| Item | V1 | V2 | Change |
|------|----|----|--------|
| Connector Type | 3-pin | 4-pin | +1 pin |
| Pin 1 | BCM6 (pin 31) | **BCM18 (pin 12)** | Changed |
| Pin 2 | BCM12 (pin 32) | BCM6 (pin 31) | Shifted |
| Pin 3 | BCM13 (pin 33) | BCM12 (pin 32) | Shifted |
| Pin 4 | - | BCM13 (pin 33) | Added |

**Result:** GPIO bank restored from 3 pins to 4 pins.

---

### 2. New I2C3 Bus (J16) - Added

| Item | V1 | V2 | Change |
|------|----|----|--------|
| I2C Connectors | 2 (J12, J13) | 3 (J12, J13, J16) | +1 connector |
| I2C Buses | 1 (I2C1) | 2 (I2C1 + I2C3) | +1 bus |
| J16 SDA | - | BCM4 (pin 7) | New |
| J16 SCL | - | BCM5 (pin 29) | New |

**Result:** Second I2C bus added on separate pins.

---

## Pin Changes Summary

| Pin | V1 Usage | V2 Usage | Change |
|-----|----------|---------|--------|
| BCM4 (pin 7) | Unused | I2C3 SDA | New function |
| BCM5 (pin 29) | GPIO bank pin 1 | I2C3 SCL | Function changed |
| BCM18 (pin 12) | Unused | GPIO bank pin 1 | New function |

---

## What Stayed the Same

- All LEDs (J1-J4): No change
- All Buttons (J5-J6): No change
- All ADC channels (J7-J10): No change
- I2C1 Ports (J12, J13): No change
- UART0 (J14): No change
- SPI0 (J15): No change
- Sensor Power Control (BCM26): No change

---

## Configuration Required

**Software:** Add to `/boot/config.txt`:
```
dtoverlay=i2c3,pins_4_5
```

This enables I2C3 on BCM4 (SDA) and BCM5 (SCL).

---

## Benefits

1. **4-pin GPIO bank maintained** - No functionality loss
2. **Second I2C bus** - Allows separate I2C device chains
3. **No conflicts** - All changes verified safe
4. **Backward compatible** - Existing I2C1 devices unchanged

---

## Hardware Impact

- **Connector change:** J11 changes from 3-pin to 4-pin connector
- **Routing change:** BCM18 (pin 12) routes to J11 pin 1 instead of BCM5
- **New connector:** J16 added for I2C3 bus

---

**Status:** ✅ All changes verified, no conflicts detected

