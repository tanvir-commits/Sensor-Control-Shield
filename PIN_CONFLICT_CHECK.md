# Raspberry Pi Pin Conflict Check
## DeviceOps Shield Pin Assignment Analysis

**Date:** 2024  
**Purpose:** Verify all GPIO pin assignments don't conflict with Raspberry Pi 4/5 reserved functions

---

## Pin Usage Summary

| Physical Pin | BCM GPIO | Function | Our Usage | Pi 4/5 Status |
|--------------|----------|----------|-----------|---------------|
| 1 | - | 3.3V Power | 3V3_IN (to load switch, ADC) | ✅ Safe - Power pin |
| 2 | - | 5V Power | Not used | ✅ Safe - Not connected |
| 3 | BCM2 | SDA (I2C1) | ADC SDA, I2C Ports | ✅ Safe - Standard I2C1 |
| 5 | BCM3 | SCL (I2C1) | ADC SCL, I2C Ports | ✅ Safe - Standard I2C1 |
| 6 | - | GND | Ground plane | ✅ Safe - Ground |
| 8 | BCM14 | TXD (UART0) | UART Connector J14 | ✅ Safe - Standard UART |
| 10 | BCM15 | RXD (UART0) | UART Connector J14 | ✅ Safe - Standard UART |
| 11 | BCM17 | GPIO17 | LED2 (via 220Ω) | ⚠️ CHECK - May have alt function |
| 13 | BCM27 | GPIO27 | LED3 (via 220Ω) | ⚠️ CHECK - May have alt function |
| 15 | BCM22 | GPIO22 | LED4 (via 220Ω) | ⚠️ CHECK - May have alt function |
| 16 | BCM23 | GPIO23 | BTN1 | ⚠️ CHECK - May have alt function |
| 18 | BCM24 | GPIO24 | BTN2 | ⚠️ CHECK - May have alt function |
| 19 | BCM10 | MOSI (SPI0) | SPI Connector J15 | ✅ Safe - Standard SPI0 |
| 21 | BCM9 | MISO (SPI0) | SPI Connector J15 | ✅ Safe - Standard SPI0 |
| 23 | BCM11 | SCLK (SPI0) | SPI Connector J15 | ✅ Safe - Standard SPI0 |
| 24 | BCM8 | CS0 (SPI0) | SPI Connector J15 | ✅ Safe - Standard SPI0 |
| 29 | BCM5 | GPIO5 | GPIO Bank J11 | ⚠️ CHECK - May have alt function |
| 31 | BCM6 | GPIO6 | GPIO Bank J11 | ⚠️ CHECK - May have alt function |
| 32 | BCM12 | GPIO12 | GPIO Bank J11 | ⚠️ CHECK - May have alt function |
| 33 | BCM13 | GPIO13 | GPIO Bank J11 | ⚠️ CHECK - May have alt function |
| 36 | BCM16 | GPIO16 | LED1 (via 220Ω) | ⚠️ CHECK - May have alt function |
| 37 | BCM26 | GPIO26 | Load Switch EN | ⚠️ CHECK - May have alt function |

---

## Standard Bus Pins (Confirmed Safe)

✅ **I2C1 Bus:**
- BCM2 (pin 3): SDA - Standard I2C1 data line
- BCM3 (pin 5): SCL - Standard I2C1 clock line
- **Status:** Safe - These are the standard I2C1 pins, no conflicts

✅ **SPI0 Bus:**
- BCM8 (pin 24): CS0 - Standard SPI0 chip select
- BCM9 (pin 21): MISO - Standard SPI0 master in
- BCM10 (pin 19): MOSI - Standard SPI0 master out
- BCM11 (pin 23): SCLK - Standard SPI0 clock
- **Status:** Safe - These are the standard SPI0 pins, no conflicts

✅ **UART0:**
- BCM14 (pin 8): TXD - Standard UART0 transmit
- BCM15 (pin 10): RXD - Standard UART0 receive
- **Status:** Safe - These are the standard UART0 pins, no conflicts

---

## GPIO Pins to Verify

**LED Outputs:**
- BCM16 (pin 36): LED1
- BCM17 (pin 11): LED2
- BCM27 (pin 13): LED3
- BCM22 (pin 15): LED4

**Button Inputs:**
- BCM23 (pin 16): BTN1
- BCM24 (pin 18): BTN2

**GPIO Bank:**
- BCM5 (pin 29): GPIO1
- BCM6 (pin 31): GPIO2
- BCM12 (pin 32): GPIO3
- BCM13 (pin 33): GPIO4

**Load Switch Control:**
- BCM26 (pin 37): Load Switch EN

---

## Potential Issues to Check

1. **Boot Mode Pins (Pi 4/5):**
   - Some GPIOs may be used for boot mode selection
   - Need to verify if any of our pins are boot-critical

2. **EEPROM Pins (HAT detection):**
   - GPIO0 (ID_SD) and GPIO1 (ID_SC) are used for HAT EEPROM
   - We're not using these, so no conflict

3. **Alt Functions:**
   - Some GPIOs have alternate functions (PWM, etc.)
   - Need to verify our GPIOs don't interfere with critical functions

4. **Pi 5 Specific:**
   - Pi 5 may have different pin functions than Pi 4
   - Need to verify compatibility

---

## Recommendations

1. Verify each GPIO pin's alternate functions
2. Check if any pins are used for boot mode on Pi 4/5
3. Ensure no pins conflict with Pi's internal functions
4. Document any warnings for users

---

**Note:** This is a preliminary check. Full verification requires checking official Raspberry Pi 4/5 pinout documentation.

