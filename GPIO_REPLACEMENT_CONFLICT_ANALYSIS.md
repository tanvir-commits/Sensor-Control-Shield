# GPIO Replacement Conflict Analysis
## Replacing BCM5 in GPIO Bank with Alternative GPIO Pin

**Date:** 2025-01-XX  
**Purpose:** Verify that replacing BCM5 (pin 29) with an alternative GPIO pin maintains 4-pin GPIO bank without conflicts

---

## Current Pin Usage Summary

### Currently Used GPIO Pins

| BCM | Physical Pin | Current Usage | Status |
|-----|--------------|---------------|--------|
| BCM2 | Pin 3 | I2C1 SDA | ✅ Used |
| BCM3 | Pin 5 | I2C1 SCL | ✅ Used |
| BCM4 | Pin 7 | **NOT USED** | ✅ Available (for I2C3 SDA) |
| BCM5 | Pin 29 | GPIO bank pin 1 | ⚠️ Would become I2C3 SCL |
| BCM6 | Pin 31 | GPIO bank pin 2 | ✅ Used |
| BCM8 | Pin 24 | SPI CS0 | ✅ Used |
| BCM9 | Pin 21 | SPI MISO | ✅ Used |
| BCM10 | Pin 19 | SPI MOSI | ✅ Used |
| BCM11 | Pin 23 | SPI SCLK | ✅ Used |
| BCM12 | Pin 32 | GPIO bank pin 3 | ✅ Used |
| BCM13 | Pin 33 | GPIO bank pin 4 | ✅ Used |
| BCM14 | Pin 8 | UART TXD | ✅ Used |
| BCM15 | Pin 10 | UART RXD | ✅ Used |
| BCM16 | Pin 36 | LED1 | ✅ Used |
| BCM17 | Pin 11 | LED2 | ✅ Used |
| BCM22 | Pin 15 | LED4 | ✅ Used |
| BCM23 | Pin 16 | BTN1 | ✅ Used |
| BCM24 | Pin 18 | BTN2 | ✅ Used |
| BCM26 | Pin 37 | Sensor power EN | ✅ Used |
| BCM27 | Pin 13 | LED3 | ✅ Used |

---

## Candidate GPIO Pins for Replacement

### Available GPIO Pins on 40-Pin Header

| BCM | Physical Pin | Alt Functions | Boot Critical? | HAT EEPROM? | Status |
|-----|--------------|--------------|---------------|-------------|--------|
| BCM18 | Pin 12 | PWM0 | ❌ No | ❌ No | ✅ **AVAILABLE** |
| BCM19 | Pin 35 | PWM1 | ❌ No | ❌ No | ✅ **AVAILABLE** |
| BCM20 | Pin 38 | GPIO only | ❌ No | ❌ No | ✅ **AVAILABLE** |
| BCM21 | Pin 40 | GPIO only | ❌ No | ❌ No | ✅ **AVAILABLE** |
| BCM25 | Pin 22 | GPIO only | ❌ No | ❌ No | ✅ **AVAILABLE** |

**Note:** BCM0 (pin 27) and BCM1 (pin 28) are reserved for HAT EEPROM - NOT recommended.

---

## Detailed Pin Analysis

### BCM18 (Physical Pin 12)
- **Alt Functions:** PWM0 (optional)
- **Boot Mode:** ❌ No
- **HAT EEPROM:** ❌ No
- **Current Usage:** Not used
- **Pi 3/4/5 Compatible:** ✅ Yes
- **Conflict Check:** ✅ No conflicts
- **Verdict:** ✅ **SAFE TO USE**

### BCM19 (Physical Pin 35)
- **Alt Functions:** PWM1 (optional)
- **Boot Mode:** ❌ No
- **HAT EEPROM:** ❌ No
- **Current Usage:** Not used
- **Pi 3/4/5 Compatible:** ✅ Yes
- **Conflict Check:** ✅ No conflicts
- **Verdict:** ✅ **SAFE TO USE**

### BCM20 (Physical Pin 38)
- **Alt Functions:** GPIO only
- **Boot Mode:** ❌ No
- **HAT EEPROM:** ❌ No
- **Current Usage:** Not used
- **Pi 3/4/5 Compatible:** ✅ Yes
- **Conflict Check:** ✅ No conflicts
- **Verdict:** ✅ **SAFE TO USE**

### BCM21 (Physical Pin 40)
- **Alt Functions:** GPIO only
- **Boot Mode:** ❌ No
- **HAT EEPROM:** ❌ No
- **Current Usage:** Not used
- **Pi 3/4/5 Compatible:** ✅ Yes
- **Conflict Check:** ✅ No conflicts
- **Verdict:** ✅ **SAFE TO USE**

### BCM25 (Physical Pin 22)
- **Alt Functions:** GPIO only
- **Boot Mode:** ❌ No
- **HAT EEPROM:** ❌ No
- **Current Usage:** Not used
- **Pi 3/4/5 Compatible:** ✅ Yes
- **Conflict Check:** ✅ No conflicts
- **Verdict:** ✅ **SAFE TO USE**

---

## Recommended Replacement Pin

### ✅ **BCM18 (Physical Pin 12)** - RECOMMENDED

**Rationale:**
1. ✅ No conflicts with existing design
2. ✅ Standard GPIO pin (PWM0 is optional alt function)
3. ✅ Works on Pi 3, 4, and 5
4. ✅ Not boot-critical
5. ✅ Not reserved for HAT EEPROM
6. ✅ Physical pin 12 is easily accessible on 40-pin header

**Alternative Options (all safe):**
- BCM19 (pin 35) - Also good, has PWM1 alt function
- BCM20 (pin 38) - Good, GPIO only
- BCM21 (pin 40) - Good, GPIO only
- BCM25 (pin 22) - Good, GPIO only

---

## Updated Pinout with BCM18 Replacement

### GPIO Bank (J11) - 4 Pins (Maintained)

| Pin | BCM | Physical Pin | Function |
|-----|-----|--------------|----------|
| Pin 1 | BCM18 | Pin 12 | GPIO1 (replaces BCM5) |
| Pin 2 | BCM6 | Pin 31 | GPIO2 |
| Pin 3 | BCM12 | Pin 32 | GPIO3 |
| Pin 4 | BCM13 | Pin 33 | GPIO4 |

### I2C3 Bus (J16) - New

| Pin | BCM | Physical Pin | Function |
|-----|-----|--------------|----------|
| Pin 1 | - | - | SENS_3V3_SW |
| Pin 2 | - | - | GND |
| Pin 3 | BCM4 | Pin 7 | I2C3 SDA |
| Pin 4 | BCM5 | Pin 29 | I2C3 SCL |

---

## Conflict Verification Checklist

- [x] BCM18 not used by any existing function
- [x] BCM18 not boot-critical
- [x] BCM18 not reserved for HAT EEPROM
- [x] BCM18 compatible with Pi 3/4/5
- [x] BCM18 has no conflicts with I2C1, SPI0, UART0
- [x] BCM18 has no conflicts with LEDs, Buttons, ADC
- [x] BCM18 has no conflicts with sensor power control
- [x] Physical pin 12 is available on 40-pin header
- [x] PWM0 alt function is optional (doesn't conflict)
- [x] All other candidate pins (BCM19, 20, 21, 25) also safe

---

## Final Recommendation

✅ **Use BCM18 (pin 12) to replace BCM5 in GPIO bank**

**Result:**
- GPIO bank maintains 4 pins (BCM18, BCM6, BCM12, BCM13)
- I2C3 uses BCM4/BCM5 (pins 7/29)
- No functionality loss
- No conflicts detected
- Compatible with Pi 3, 4, and 5

---

## Implementation Notes

1. **Hardware:** Route BCM18 (pin 12) to J11 pin 1 instead of BCM5
2. **Software:** Update pin configuration to reflect BCM18 in GPIO bank
3. **Documentation:** Update pin mapping to show BCM18 in GPIO bank, BCM5 in I2C3

---

**Status:** ✅ **ALL CHECKS PASSED - NO CONFLICTS DETECTED**

