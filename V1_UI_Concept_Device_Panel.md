# V1 UI Concept — Single-Screen Device Panel

## Purpose
A single, always-on screen that gives instant visual confirmation that:
- the 4 analog channels are reading correctly,
- the LED output ports toggle correctly,
- the button input ports are being detected,
- I²C devices are present (or the bus has a wiring/power issue),
- SPI is enabled and basic activity/test feedback is available.

This is intentionally **simple** and **honest**: it’s a live control/diagnostics panel, not a workflow builder.

---

## Screen Layout Overview
One window. No tabs required. Everything important is visible at once.

### A) Top Status Bar (always visible)
Shows quick health + context:
- **Sensor Power:** `ON / OFF`
- **I²C:** `OK / NO DEVICES / ERROR`
- **SPI:** `OK / NOT VERIFIED / ERROR`
- **UART:** `OK / NOT CONFIGURED` *(optional status only)*
- **IP Address:** `xxx.xxx.xxx.xxx` *(optional but useful)*

---

## Main Panel Sections (always visible)

### 1) Analog Voltages (4 channels, always updating)
A fixed 4-row readout (large and clear):
- `ADC0: 1.234 V`
- `ADC1: 3.301 V`
- `ADC2: 0.012 V`
- `ADC3: 5.002 V`

**Visual states:**
- Normal reading: neutral/standard color
- Not reading / disconnected: greyed
- Error state: red

---

### 2) LED Output Ports (4 toggles)
Four independent ON/OFF controls that reflect current state:
- `LED1 [ON/OFF]`
- `LED2 [ON/OFF]`
- `LED3 [ON/OFF]`
- `LED4 [ON/OFF]`

**Visual states:**
- ON: green-highlight
- OFF: grey

---

### 3) Button Input Ports (2 indicators)
Two live indicators corresponding to the button headers on the board:
- `BTN1: PRESSED / RELEASED`
- `BTN2: PRESSED / RELEASED`

**Visual states:**
- PRESSED: green
- RELEASED: grey

---

### 4) I²C Tools (scan + results + health feedback)
- A single action: **Scan I²C**
- A results list box:
  - displays found device addresses (e.g. `0x48`, `0x68`)
- A clear status message:
  - **Devices found** (count)
  - **No devices found**
  - **Bus error** (wiring/power/pull-up issue)

---

### 5) SPI Tools (basic test + feedback)
Because SPI is not “scannable” like I²C, this section provides basic, honest feedback:
- A single action: **Run SPI Test**
- A result panel that shows:
  - **SPI enabled**
  - **Clock/MOSI activity detected** (if applicable)
  - **MISO response detected / not detected**
  - A plain “not verified” state if no test conditions exist (e.g., no loopback/device)

---

## Widget Hierarchy Sketch (structure only)

```
MainWindow
└── RootContainer (vertical)
    ├── StatusBar (horizontal)
    │   ├── SensorPowerStatus
    │   ├── I2CStatus
    │   ├── SPIStatus
    │   ├── UARTStatus (optional)
    │   └── IPAddress (optional)
    │
    ├── ContentArea (vertical)
    │   ├── AnalogSection
    │   │   ├── SectionTitle: "Analog Voltages"
    │   │   └── AnalogReadoutGrid (4 rows)
    │   │       ├── ADC0_Row (Label + Value)
    │   │       ├── ADC1_Row (Label + Value)
    │   │       ├── ADC2_Row (Label + Value)
    │   │       └── ADC3_Row (Label + Value)
    │   │
    │   ├── DigitalSectionRow (horizontal)
    │   │   ├── LEDSection
    │   │   │   ├── SectionTitle: "LED Outputs"
    │   │   │   └── LEDToggleGrid (2x2 or 1x4)
    │   │   │       ├── LED1_Toggle
    │   │   │       ├── LED2_Toggle
    │   │   │       ├── LED3_Toggle
    │   │   │       └── LED4_Toggle
    │   │   │
    │   │   └── ButtonSection
    │   │       ├── SectionTitle: "Buttons"
    │   │       └── ButtonIndicatorStack
    │   │           ├── BTN1_Indicator
    │   │           └── BTN2_Indicator
    │   │
    │   ├── BusToolsRow (horizontal)
    │   │   ├── I2CSection
    │   │   │   ├── SectionTitle: "I²C"
    │   │   │   ├── ScanI2C_Button
    │   │   │   ├── I2C_ResultsList
    │   │   │   └── I2C_StatusMessage
    │   │   │
    │   │   └── SPISection
    │   │       ├── SectionTitle: "SPI"
    │   │       ├── RunSPI_Button
    │   │       └── SPI_ResultPanel
    │   │
    │   └── FooterHints (optional)
    │       └── Short help text
```

---

## Copy/Label Guidance (what the UI should say)
Use short, direct language:

- **I²C**
  - “Scan I²C”
  - “Found N device(s)”
  - “No devices found”
  - “Bus error (check wiring/power/pull-ups)”

- **SPI**
  - “Run SPI Test”
  - “SPI enabled”
  - “MISO response not detected”
  - “Not verified” if no reliable test condition exists

---

## V1 Scope Boundaries (kept minimal on purpose)
This UI is **one screen** and focuses on confirmation + basic interaction:
- No workflow builder
- No scripting editor
- No cloud
- No device identification promises beyond address presence
