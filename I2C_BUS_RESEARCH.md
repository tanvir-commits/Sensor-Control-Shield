# Second I2C Bus Research Summary

## Research Completed: I2C Bus Options for Shield Design

**Date:** 2025-01-XX  
**Purpose:** Evaluate options for adding a second I2C bus connector to the shield

---

## Current Shield State

**I2C1 (Bus 1) - Currently Used:**
- SDA: BCM2 (pin 3)
- SCL: BCM3 (pin 5)
- Used by: ADC (on-board) + J12/J13 I2C connectors

**GPIO Bank (J11) - Currently Available:**
- Pin 1: BCM5 (pin 29)
- Pin 2: BCM6 (pin 31)
- Pin 3: BCM12 (pin 32)
- Pin 4: BCM13 (pin 33)

**Other Pins in Use:**
- BCM8-11: SPI0 (J15 connector)
- BCM14-15: UART0 (J14 connector)
- BCM16, 17, 22, 27: LEDs
- BCM23, 24: Buttons
- BCM26: Sensor power control

---

## Available I2C Bus Options

### I2C3 Device Tree Overlay Options

Based on research, I2C3 can be configured with these pin pairs:

1. **`pins_4_5`**: GPIO4 (BCM4, pin 7) / GPIO5 (BCM5, pin 29)
2. **`pins_6_7`**: GPIO6 (BCM6, pin 31) / GPIO7 (BCM7, pin 26)
3. **`pins_8_9`**: GPIO8 (BCM8, pin 24) / GPIO9 (BCM9, pin 21)
4. **`pins_10_11`**: GPIO10 (BCM10, pin 19) / GPIO11 (BCM11, pin 23)

**Configuration:** Add to `/boot/config.txt`:
```
dtoverlay=i2c3,pins_4_5
```

---

## Pin Availability Analysis

| BCM | Physical Pin | Current Usage | Available for I2C3? |
|-----|--------------|---------------|---------------------|
| BCM4 | Pin 7 | **NOT USED** | ✅ **YES** |
| BCM5 | Pin 29 | GPIO bank pin 1 | ⚠️ If we sacrifice GPIO bank |
| BCM6 | Pin 31 | GPIO bank pin 2 | ⚠️ If we sacrifice GPIO bank |
| BCM7 | Pin 26 | Unknown (need verify) | ❓ Need to verify |
| BCM8 | Pin 24 | SPI CS0 | ❌ NO (SPI in use) |
| BCM9 | Pin 21 | SPI MISO | ❌ NO (SPI in use) |
| BCM10 | Pin 19 | SPI MOSI | ❌ NO (SPI in use) |
| BCM11 | Pin 23 | SPI SCLK | ❌ NO (SPI in use) |
| BCM12 | Pin 32 | GPIO bank pin 3 | ⚠️ If we sacrifice GPIO bank |
| BCM13 | Pin 33 | GPIO bank pin 4 | ⚠️ If we sacrifice GPIO bank |

---

## Option Evaluation

### ✅ Option 1: I2C3 on GPIO4/GPIO5 (BCM4/BCM5) - **RECOMMENDED**

**Configuration:**
- SDA: BCM4 (pin 7) - ✅ **Completely free, no conflicts**
- SCL: BCM5 (pin 29) - ⚠️ Currently GPIO bank pin 1
- Device tree: `dtoverlay=i2c3,pins_4_5`
- Works on: Pi 3, 4, 5

**Pros:**
- ✅ BCM4 is completely unused (no conflicts)
- ✅ Only loses 1 GPIO bank pin (acceptable trade-off)
- ✅ Standard, well-documented configuration
- ✅ Works across all Pi models (3/4/5)
- ✅ No conflicts with existing peripherals
- ✅ Minimal hardware changes

**Cons:**
- ⚠️ GPIO bank reduced from 4 to 3 pins
- ⚠️ Requires device tree overlay (standard practice)

**GPIO Bank Impact:**
- Before: 4 pins (BCM5, BCM6, BCM12, BCM13)
- After: 3 pins (BCM6, BCM12, BCM13)

**Verdict:** ✅ **BEST OPTION** - Minimal impact, maximum compatibility

---

### ⚠️ Option 2: I2C3 on GPIO6/GPIO7 (BCM6/BCM7)

**Configuration:**
- SDA: BCM6 (pin 31) - ⚠️ Currently GPIO bank pin 2
- SCL: BCM7 (pin 26) - ❓ Need to verify availability
- Device tree: `dtoverlay=i2c3,pins_6_7`

**Pros:**
- ✅ Uses different pins than Option 1
- ✅ If BCM7 is available, similar trade-off

**Cons:**
- ⚠️ Still loses 1 GPIO bank pin (BCM6)
- ❓ BCM7 availability unclear (physical pin 26 is GND, but BCM7 may be different)
- ⚠️ Requires device tree overlay

**Verdict:** ⚠️ **NEEDS VERIFICATION** - Check if BCM7 is actually available

**Note:** Physical pin 26 is GND, but BCM7 may be accessible through a different physical pin. Need to verify Raspberry Pi pinout.

---

### ❌ Option 3: I2C3 on GPIO8/GPIO9 or GPIO10/GPIO11

**Configuration:**
- Would use SPI pins (BCM8-11)
- Device tree: `dtoverlay=i2c3,pins_8_9` or `pins_10_11`

**Verdict:** ❌ **NOT VIABLE** - All pins are used for SPI0 (J15 connector)

---

### ⚠️ Option 4: Pi 5 Native I2C6/I2C7 (Bus 13/14)

**Configuration:**
- Native hardware buses on Pi 5
- Appear as `/dev/i2c-13` and `/dev/i2c-14`
- **Status:** GPIO pin assignments not clearly documented in research

**Pros:**
- ✅ No device tree overlay needed on Pi 5
- ✅ Native hardware support
- ✅ Potentially better performance

**Cons:**
- ❌ Pi 5 only (not available on Pi 3/4)
- ❌ GPIO pin assignments unclear from research
- ⚠️ Would require fallback to I2C3 on older Pis
- ⚠️ May conflict with existing pins

**Verdict:** ⚠️ **NEEDS FURTHER RESEARCH** - Check official Pi 5 documentation for pin assignments

**Next Steps:**
- Check official Raspberry Pi 5 GPIO pinout documentation
- Verify which physical pins I2C6/I2C7 use
- Determine if pins are available on our shield

---

### ❌ Option 5: Repurpose Entire GPIO Bank

**Configuration:**
- Convert GPIO bank (J11) to I2C3
- Use BCM5/BCM6 or BCM12/BCM13 for I2C3
- Remove GPIO bank connector entirely

**Verdict:** ❌ **NOT RECOMMENDED** - Loses all 4 GPIO bank pins, too much functionality loss

---

## Recommendation

### ✅ **Option 1: I2C3 on GPIO4/GPIO5 (BCM4/BCM5)**

**Rationale:**
1. **Minimal Impact:** Only loses 1 GPIO bank pin (BCM5)
2. **No Conflicts:** BCM4 is completely unused
3. **Universal Compatibility:** Works on Pi 3, 4, and 5
4. **Standard Configuration:** Well-documented and supported
5. **Clean Implementation:** Simple device tree overlay

**Implementation Plan:**
1. Add J16: I2C_PORT_C (4-pin connector)
   - Pin 1: SENS_3V3_SW
   - Pin 2: GND
   - Pin 3: SDA (I2C3) → BCM4 (pin 7)
   - Pin 4: SCL (I2C3) → BCM5 (pin 29)

2. Update GPIO bank (J11) to 3 pins:
   - Pin 1: (removed - now I2C3 SCL)
   - Pin 2: BCM6 (GPIO2)
   - Pin 3: BCM12 (GPIO3)
   - Pin 4: BCM13 (GPIO4)

3. Software updates:
   - Add `dtoverlay=i2c3,pins_4_5` to boot config
   - Update I2C scanner to support bus 3
   - Update GUI to show/select I2C bus

---

## Outstanding Questions

1. **Pi 5 I2C6/I2C7 Pin Assignments:**
   - Need to check official Pi 5 GPIO pinout documentation
   - Verify which physical pins bus 13/14 use
   - Determine if they're available on our shield

2. **BCM7 Availability:**
   - Physical pin 26 is GND, but BCM7 may be accessible elsewhere
   - Need to verify Raspberry Pi pinout for BCM7

3. **GPIO Bank Usage:**
   - Assess how critical 4-pin GPIO bank is vs 3-pin
   - Determine if users would prefer 3 GPIO pins + 1 I2C bus vs 4 GPIO pins

---

## Next Steps

1. ✅ Research complete for I2C3 options
2. ⚠️ Verify Pi 5 I2C6/I2C7 pin assignments (if considering native buses)
3. ⚠️ Verify BCM7 availability (if considering Option 2)
4. ✅ Make final design decision based on research
5. Update pin mapping CSV
6. Update software and documentation

---

## References

- Raspberry Pi I2C documentation
- Device tree overlay documentation
- GPIO pinout references
- Multiple I2C bus configuration guides

