# Device Panel - Raspberry Pi Setup Guide

## Quick Start

### 1. Enable I2C and SPI

```bash
sudo raspi-config
```

Navigate to:
- **Interface Options > I2C > Enable**
- **Interface Options > SPI > Enable**

Or manually edit `/boot/config.txt`:
```
dtparam=i2c_arm=on
dtparam=spi=on
```

Then reboot:
```bash
sudo reboot
```

### 2. Run Setup Script

```bash
chmod +x setup_pi.sh
./setup_pi.sh
```

This will:
- Add you to `gpio`, `i2c`, `spi` groups
- Install system packages
- Create virtual environment
- Install Python dependencies

### 3. Log Out and Back In

Groups only take effect after logging out/in:
```bash
# Log out and back in, or:
newgrp gpio
```

### 4. Launch GUI

```bash
source venv/bin/activate
python3 device_panel.py
```

Or use the launch script:
```bash
./run_gui.sh
```

## Manual Setup

If you prefer manual setup:

### Install System Packages
```bash
sudo apt-get update
sudo apt-get install -y python3-pip python3-venv i2c-tools
```

### Add User to Groups
```bash
sudo usermod -aG gpio,i2c,spi $USER
# Log out and back in
```

### Create Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate
```

### Install Python Packages
```bash
pip install --upgrade pip
pip install -r requirements_pi.txt
```

## Verify Hardware Access

### Test I2C
```bash
i2cdetect -y 1
```

Should show your ADS1115 at address `0x48` if connected.

### Test GPIO (optional)
```bash
python3 -c "from gpiozero import LED; led = LED(16); led.on(); import time; time.sleep(1); led.off()"
```

## Troubleshooting

### Permission Denied Errors
- Make sure you're in the groups: `groups | grep -E 'gpio|i2c|spi'`
- Log out and back in after adding to groups
- Or run with `sudo` (not recommended for GUI)

### I2C Not Found
- Enable I2C in `raspi-config`
- Reboot after enabling
- Check: `ls -la /dev/i2c-*`

### SPI Not Found
- Enable SPI in `raspi-config`
- Reboot after enabling
- Check: `ls -la /dev/spidev*`

### GUI Won't Launch
- Make sure display is connected
- Check: `echo $DISPLAY`
- Try: `export DISPLAY=:0`

## Hardware Connections

Make sure your Sensor Control Shield is properly connected:
- 40-pin header seated correctly
- Power LED on shield should be on
- I2C devices (ADS1115) should appear at 0x48

## Features

Once running on Pi:
- ✅ **Real GPIO** - LEDs and buttons work with actual hardware
- ✅ **Real ADC** - ADS1115 reads actual voltages
- ✅ **Real I2C** - Scans actual I2C bus
- ✅ **Real SPI** - Tests actual SPI bus
- ✅ **Power Control** - GPIO26 controls sensor power rail


