# Device Panel - Raspberry Pi Sensor Control Shield

> **📋 [PROJECT OVERVIEW - See All Branches, Agents, and Status →](PROJECT_OVERVIEW.md)**

## Overview

This shield provides a clean, professional interface for connecting sensors, LEDs, buttons, and other peripherals to a Raspberry Pi. It includes:

1. **4-channel ADC** (ADS1015) for analog voltage measurement
2. **Switched sensor power rail** (SY6280AAC load switch, 200mA limit)
3. **4 LED outputs** (current-limited, 220Ω resistors)
4. **2 button inputs** (with internal pull-ups)
5. **Standard bus connectors** (I2C, SPI, UART)
6. **GPIO bank** (4 additional GPIO pins)

**Key Features:**
- All connections via JST-GH connectors (professional, reliable)
- Sensor power rail: ON by default, jumper to force OFF, software control via GPIO26
- Current-limited outputs (LEDs protected)
- Shared ground plane across all connectors
- Surface-mount connectors on bottom side

---

## Quick Links

- **[📊 PROJECT OVERVIEW](PROJECT_OVERVIEW.md)** - All branches, agents, RPi assignments, and status
- **[🚀 AGENT QUICK START](AGENT_QUICK_START.md)** - Get started quickly as a new agent
- **[📝 DEVELOPMENT GUIDELINES](DEVELOPMENT.md)** - Overall development rules and structure
- **[🌿 BRANCH STRATEGY](BRANCH_STRATEGY.md)** - Branch workflow and merge process
- **[🤝 AGENT COMMUNICATION](AGENT_COMMUNICATION.md)** - How agents coordinate
- **[🧪 TESTING WORKFLOW](TESTING_WORKFLOW.md)** - Ubuntu first, then RPi testing
- **[📌 RPi ASSIGNMENTS](RPI_ASSIGNMENTS.md)** - RPi connection details and deployment

### Current Branches

```
prod (production)
  └── dev (development)
      ├── feature/power-profiler      [Active - Agent: power-profiler]
      ├── feature/test-sequences      [Not started]
      └── feature/smart-suggestions   [Active - Agent: smart-suggestions]
```

See [PROJECT_OVERVIEW.md](PROJECT_OVERVIEW.md) for complete branch details, RPi assignments, and status.

---

## Block Diagram

```
Raspberry Pi 40-Pin Header
    ├── 3.3V ───────────────> Load Switch (SY6280AAC) ──> SENS_3V3_SW
    │                              │
    │                              └──> Power LED (330Ω)
    │
    ├── I2C1 (SDA/SCL) ────> ADC (ADS1015) + I2C Connectors (J12, J13)
    │
    ├── SPI0 ───────────────> SPI Connector (J15)
    │
    ├── UART ───────────────> UART Connector (J14)
    │
    ├── GPIO ───────────────> LED Connectors (J1-J4), Button Connectors (J5-J6), GPIO Bank (J11)
    │
    └── GPIO26 ─────────────> Load Switch EN (via 100Ω series resistor)
```

---

## Circuit Blocks

### 1. ADC Circuit (ADS1015)

| RefDes | Part | Value | Package | Notes |
|--------|------|-------|---------|------|
| U_ADC | ADS1015IDGST | - | VSSOP-10 | I2C address 0x48 (ADDR to GND) |
| C_ADC | Capacitor | 0.1µF | 0402/0603 | Decoupling at VDD pin |

**Connections:**
- VDD → 3V3_IN
- GND → Ground
- SDA → I2C1 SDA (BCM2, pin 3)
- SCL → I2C1 SCL (BCM3, pin 5)
- ADDR → GND (sets address to 0x48)
- AIN0-AIN3 → ADC connectors J7-J10

**Schematic Reference:**

![ADS1015 Typical Application Circuit](images/ADS1015.jpg)

*Figure 1: ADS1015 Typical Application Circuit - Shows power connections, analog inputs (AIN0-AIN3), I2C interface (SDA/SCL), address configuration, and decoupling capacitor placement.*

---

### 2. Load Switch Circuit (SY6280AAC) - Power Control

| RefDes | Part | Value | Package | Notes |
|--------|------|-------|---------|-------|
| U_SENS_SW | SY6280AAC | - | SOT-23-5 | Load switch, 200mA limit |
| RSET1 | Resistor | 34.0kΩ 1% | 0603 | Sets 200mA current limit |
| REN_PU | Resistor | 100kΩ | 0603 | Pull-up for default ON |
| REN_SER | Resistor | 100Ω | 0603 | Series resistor on EN pin |
| SJ_OFF | Solder Jumper | 2-pad | - | Optional: close to force OFF |
| CIN | Capacitor | 10µF 6.3V+ X5R/X7R | 0805/1206 | Input decoupling |
| COUT | Capacitor | 10µF 6.3V+ X5R/X7R | 0805/1206 | Output decoupling |

**Pin Connections:**
- Pin 1 (IN) → 3V3_IN
- Pin 2 (GND) → Ground
- Pin 3 (EN) → GPIO26 (via REN_SER 100Ω), pulled HIGH by REN_PU 100kΩ
- Pin 4 (ILIM) → Ground via RSET1 (34.0kΩ)
- Pin 5 (OUT) → SENS_3V3_SW

**Configuration:**
- **Default State:** ON (EN pulled HIGH via REN_PU)
- **Jumper SJ_OFF:** Close to force OFF (pulls EN LOW)
- **Current Limit:** Fixed at 200mA (RSET = 34.0kΩ)

**Schematic Reference:**

![SY6280AAC Typical Application Circuit](images/Powe_chip.png)

*Figure 2: SY6280AAC Typical Application Circuit (200mA current limit)*

![SY6280AAC PCB Layout](images/Power_chip_layout.png)

*Figure 3: SY6280AAC PCB Layout - Recommended component placement*

---

### 3. Power Indicator LED

| RefDes | Part | Value | Package | Notes |
|--------|------|-------|---------|-------|
| R_PWR_LED | Resistor | 330Ω | 0603 | Current limit for power indicator LED |
| LED_PWR | LED | Standard 3mm/5mm LED | - | Sensor power rail indicator (on-board, not user-installed) |

**Connections:**
- SENS_3V3_SW → R_PWR_LED (330Ω) → LED_PWR anode
- LED_PWR cathode → GND
- **Note:** Indicates when sensor power rail (SENS_3V3_SW) is ON. LED is on-board component, not user-installed.

---

### 4. LED Output Circuits (4x)

| RefDes | Part | Value | Package | Notes |
|--------|------|-------|---------|-------|
| R_LED1 | Resistor | 220Ω | 0603 | Current limit for LED1 |
| R_LED2 | Resistor | 220Ω | 0603 | Current limit for LED2 |
| R_LED3 | Resistor | 220Ω | 0603 | Current limit for LED3 |
| R_LED4 | Resistor | 220Ω | 0603 | Current limit for LED4 |

**Connections:**
- LED1: GPIO16 (BCM16, pin 36) → R_LED1 (220Ω) → J1 pin 1
- LED2: GPIO17 (BCM17, pin 11) → R_LED2 (220Ω) → J2 pin 1
- LED3: GPIO27 (BCM27, pin 13) → R_LED3 (220Ω) → J3 pin 1
- LED4: GPIO22 (BCM22, pin 15) → R_LED4 (220Ω) → J4 pin 1
- All LED connectors: Pin 2 → GND

---

### 5. Button Input Circuits (2x)

**Connections:**
- BTN1: GPIO23 (BCM23, pin 16) → J5 pin 1 (use internal pull-up)
- BTN2: GPIO24 (BCM24, pin 18) → J6 pin 1 (use internal pull-up)
- Both: Pin 2 → GND
- **Note:** Configure GPIO with internal pull-up, pressed = GND

---

### 6. ADC Input Connectors (4x)

**Connections:**
- J7 (ADC0): Pin 1 → ADS1015 AIN0, Pin 2 → GND
- J8 (ADC1): Pin 1 → ADS1015 AIN1, Pin 2 → GND
- J9 (ADC2): Pin 1 → ADS1015 AIN2, Pin 2 → GND
- J10 (ADC3): Pin 1 → ADS1015 AIN3, Pin 2 → GND

**Design Note:** Keep analog routing quiet, away from digital signals.

---

### 7. GPIO Bank Connector (1x)

**Connections:**
- J11 pin 1 → GPIO5 (BCM5, pin 29)
- J11 pin 2 → GPIO6 (BCM6, pin 31)
- J11 pin 3 → GPIO12 (BCM12, pin 32)
- J11 pin 4 → GPIO13 (BCM13, pin 33)
- **Note:** No GND on this connector, use GND from other connectors

---

### 8. I2C Port Connectors (2x)

**Connections:**
- J12 (I2C_PORT_A):
  - Pin 1 → SENS_3V3_SW
  - Pin 2 → GND
  - Pin 3 → I2C1 SDA (BCM2, pin 3)
  - Pin 4 → I2C1 SCL (BCM3, pin 5)

- J13 (I2C_PORT_B):
  - Pin 1 → SENS_3V3_SW
  - Pin 2 → GND
  - Pin 3 → I2C1 SDA (BCM2, pin 3)
  - Pin 4 → I2C1 SCL (BCM3, pin 5)

---

### 9. UART Connector (1x)

**Connections:**
- J14 (UART0):
  - Pin 1 → GND
  - Pin 2 → TXD (BCM14, pin 8)
  - Pin 3 → RXD (BCM15, pin 10)

---

### 10. SPI Connector (1x)

**Connections:**
- J15 (SPI0):
  - Pin 1 → SENS_3V3_SW
  - Pin 2 → GND
  - Pin 3 → SCLK (BCM11, pin 23)
  - Pin 4 → MOSI (BCM10, pin 19)
  - Pin 5 → MISO (BCM9, pin 21)
  - Pin 6 → CS0 (BCM8, pin 24)

---

## Connector Specifications

**All JST-GH Connectors:**
- **2-pin, 4-pin, 6-pin:** LCSC C22436166 (Hong Cheng HC-PM254-8.5H-2x20PS)
- **3-pin:** LCSC C161691 (JST BM03B-GHS-TBT(LF)(SN))
- **Type:** 2.54mm pitch, SMD receptacle
- **Placement:** Edge-mounted, SMT on bottom side

---

## Raspberry Pi 40-Pin Header Connections

| Pi Pin | BCM | Signal | Destination |
|--------|-----|--------|-------------|
| 1 | - | 3.3V | 3V3_IN (to load switch, ADC) |
| 2 | - | 5V | Not used |
| 3 | BCM2 | SDA (I2C1) | ADC SDA, J12 pin 3, J13 pin 3 |
| 5 | BCM3 | SCL (I2C1) | ADC SCL, J12 pin 4, J13 pin 4 |
| 6 | - | GND | Ground plane |
| 8 | BCM14 | TXD | J14 pin 2 |
| 10 | BCM15 | RXD | J14 pin 3 |
| 11 | BCM17 | GPIO17 | LED2 (via 220Ω) |
| 13 | BCM27 | GPIO27 | LED3 (via 220Ω) |
| 15 | BCM22 | GPIO22 | LED4 (via 220Ω) |
| 16 | BCM23 | GPIO23 | BTN1 |
| 18 | BCM24 | GPIO24 | BTN2 |
| 19 | BCM10 | MOSI | J15 pin 4 |
| 21 | BCM9 | MISO | J15 pin 5 |
| 23 | BCM11 | SCLK | J15 pin 3 |
| 24 | BCM8 | CS0 | J15 pin 6 |
| 29 | BCM5 | GPIO5 | J11 pin 1 |
| 31 | BCM6 | GPIO6 | J11 pin 2 |
| 32 | BCM12 | GPIO12 | J11 pin 3 |
| 33 | BCM13 | GPIO13 | J11 pin 4 |
| 36 | BCM16 | GPIO16 | LED1 (via 220Ω) |
| 37 | BCM26 | GPIO26 | Load switch EN (via 100Ω) |
| All GND pins | - | GND | Ground plane |

---

## PCB Layout Guidelines

1. **Load Switch Section:**
   - Place U_SENS_SW near power input
   - CIN immediately adjacent to IN pin
   - COUT immediately adjacent to OUT pin
   - RSET1, REN_PU, REN_SER close to IC

2. **ADC Section:**
   - Place U_ADC in analog island (isolated from digital)
   - C_ADC at VDD pin
   - Route ADC channels (AIN0-AIN3) away from digital signals

3. **Connectors:**
   - Place all connectors along board edges
   - SMT connectors on bottom side
   - Group related connectors together

4. **Power Routing:**
   - 3V3_IN: Minimum 0.5mm trace width
   - SENS_3V3_SW: Minimum 0.5mm trace width
   - Ground: Continuous ground plane

5. **LED Resistors:**
   - Place 220Ω resistors between GPIO and connector pins
   - Standard 0603 package

---

## Complete BOM Summary

| Category | Count | Components |
|----------|-------|------------|
| ICs | 2 | ADS1015IDGST, SY6280AAC |
| Resistors | 8 | 1x 330Ω (power LED), 4x 220Ω (LEDs), 34.0kΩ (current limit), 100kΩ (pull-up), 100Ω (series) |
| Capacitors | 3 | 2x 10µF (load switch), 1x 0.1µF (ADC) |
| Connectors - 2-pin | 10 | J1-J4 (LEDs), J5-J6 (Buttons), J7-J10 (ADC) - LCSC C22436166 |
| Connectors - 3-pin | 1 | J14 (UART) - LCSC C161691 |
| Connectors - 4-pin | 3 | J11 (GPIO), J12-J13 (I2C) - LCSC C22436166 |
| Connectors - 6-pin | 1 | J15 (SPI) - LCSC C22436166 |
| Header | 1 | 40-pin Raspberry Pi header |
| Jumper | 1 | 2-pad solder jumper (optional) |

---

## Key Design Decisions (FINALIZED)

- **ADC:** ADS1015IDGST (12-bit, I2C address 0x48)
- **Load Switch:** SY6280AAC (200mA limit, ON by default)
- **LED Current Limit:** 220Ω resistors (all LEDs)
- **Load Switch Default:** ON (pull-up resistor, jumper to force OFF)
- **Current Limit:** Fixed at 200mA (34.0kΩ resistor)

---

## References

- ADS1015 Datasheet: [Texas Instruments](https://www.ti.com/product/ADS1015)
- SY6280AAC Datasheet: [Silergy](https://www.silergy.com/)
- ADS1015 Schematic: [images/ADS1015.jpg](images/ADS1015.jpg)
- SY6280AAC Schematic: [images/Powe_chip.png](images/Powe_chip.png)
- SY6280AAC Layout: [images/Power_chip_layout.png](images/Power_chip_layout.png)

## Design Files

**Bill of Materials (BOM):**
- [blocks_bom_sensor_switch_adc_GPIO26.csv](blocks_bom_sensor_switch_adc_GPIO26.csv) - Complete component list with LCSC part numbers

**Pin Mapping:**
- [pin_mapping_FINAL_UART3_with_JLC_and_SENSrail_GPIO26.csv](pin_mapping_FINAL_UART3_with_JLC_and_SENSrail_GPIO26.csv) - Complete pin mapping and connector assignments

---

**End of Document**
