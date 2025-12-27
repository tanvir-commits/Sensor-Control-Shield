# Device Panel - Raspberry Pi Hardware Control GUI

A PySide6-based desktop application for monitoring and controlling hardware interfaces on a Raspberry Pi expansion board.

## Features

- **Analog Voltage Monitoring**: Real-time display of 4 ADC channels (10Hz update rate)
- **LED Control**: Toggle 4 LED outputs with visual feedback
- **Button Monitoring**: Live indicators for 2 button inputs
- **I²C Bus Scanning**: Scan and display connected I²C devices
- **SPI Testing**: Verify SPI bus functionality
- **Status Bar**: System health indicators (power, buses, IP address)

## Project Structure

```
DeviceOps/
├── device_panel.py          # Main entry point
├── requirements.txt         # Python dependencies
├── ui/                      # UI components
│   ├── main_window.py      # Main window
│   ├── status_bar.py       # Status bar widget
│   └── sections/           # UI sections
│       ├── analog_section.py
│       ├── led_section.py
│       ├── button_section.py
│       ├── i2c_section.py
│       └── spi_section.py
└── mock/                    # Mock hardware (for UI design)
    └── mock_hardware.py
```

## Setup

### 1. Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate  # On Linux/Mac
# or
venv\Scripts\activate  # On Windows
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Run the Application

```bash
python3 device_panel.py
```

## Current Status

✅ **UI Design Phase Complete**
- All UI sections implemented
- Mock hardware data generators for design iteration
- 10Hz update rate implemented
- Status bar with all indicators

🚧 **Next Steps**
- Replace mock hardware with real hardware managers
- Add GPIO/I2C/SPI hardware libraries
- Implement real hardware interfaces
- Add error handling and graceful degradation

## Development Notes

This project follows a **UI-first approach**:
1. Design UI with mock data
2. Refine look and feel
3. Replace mock with real hardware

The mock hardware generators allow you to design and iterate on the UI without needing physical hardware connected.

## Hardware Specifications

- **LEDs**: 4 outputs (BCM16, 17, 27, 22)
- **Buttons**: 2 inputs (BCM23, 24) with pull-ups
- **ADC**: ADS1115 at I2C address 0x48, 4 channels
- **I²C**: I2C1 bus (BCM2/3)
- **SPI**: SPI0 bus
- **Sensor Power**: GPIO26 (BCM26) controlled load switch

## License

[Add your license here]

