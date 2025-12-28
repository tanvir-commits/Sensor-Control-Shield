# Deployment Checklist - Raspberry Pi

## Pre-Deployment Verification

### ✅ Code Status
- [x] Hardware abstraction layer implemented
- [x] Platform detection working
- [x] GPIO manager (LEDs & buttons)
- [x] ADC manager (ADS1115)
- [x] I2C scanner
- [x] SPI tester
- [x] Power manager (sensor rail)
- [x] GUI fully functional
- [x] Error handling in place

### ✅ Testing Status
- [x] GUI launches successfully
- [x] LED buttons toggle (mock mode)
- [x] Button indicators update (mock mode)
- [x] I2C scanner works (real hardware on PC)
- [x] All UI sections functional
- [x] 10Hz update rate working

## Raspberry Pi Setup Steps

### 1. Transfer Code
```bash
# On your PC
cd /home/a/projects/DeviceOps
git add .
git commit -m "Ready for Pi deployment"
git push

# On Raspberry Pi
git clone https://github.com/tanvir-commits/Sensor-Control-Shield.git
cd Sensor-Control-Shield
```

### 2. Enable Hardware Interfaces
```bash
sudo raspi-config
# Interface Options > I2C > Enable
# Interface Options > SPI > Enable
sudo reboot
```

### 3. Run Setup Script
```bash
chmod +x setup_pi.sh
./setup_pi.sh
```

### 4. Verify Hardware Access
```bash
# Check I2C
i2cdetect -y 1
# Should show ADS1115 at 0x48

# Check groups
groups | grep -E 'gpio|i2c|spi'
# Should show: gpio i2c spi

# Check devices
ls -la /dev/i2c-* /dev/spidev*
```

### 5. Launch GUI
```bash
source venv/bin/activate
python3 device_panel.py
```

## Expected Behavior on Pi

### LEDs
- Clicking LED buttons should turn on/off actual LEDs
- LED state persists until toggled again
- Visual feedback: Green = ON, Grey = OFF

### Buttons
- Pressing physical buttons updates indicators
- Indicators show: Green = PRESSED, Grey = RELEASED
- Updates in real-time (10Hz polling)

### ADC (Analog Voltages)
- Shows real voltage readings from ADS1115
- 4 channels updating at 10Hz
- Color-coded by voltage level

### I2C Scanner
- Click "Scan I²C" to find devices
- Should show ADS1115 at 0x48
- May show other I2C sensors if connected

### SPI Tester
- Click "Run SPI Test" to verify SPI bus
- Shows SPI status and activity

### Sensor Power
- Status bar shows power state
- Controlled by GPIO26 (load switch)

## Troubleshooting

### LEDs Don't Work
- Check: `gpiozero` installed
- Check: User in `gpio` group
- Check: Physical connections

### Buttons Don't Work
- Check: Pull-up resistors configured
- Check: Button wiring (active LOW)
- Check: GPIO pins correct (BCM23, BCM24)

### ADC Not Reading
- Check: ADS1115 connected to I2C
- Check: Address is 0x48
- Check: I2C enabled and working
- Test: `i2cdetect -y 1` shows 0x48

### I2C Not Working
- Check: I2C enabled in `raspi-config`
- Check: User in `i2c` group
- Check: Reboot after enabling
- Test: `i2cdetect -y 1`

## Code Features

### Automatic Platform Detection
- Detects Raspberry Pi automatically
- Uses real hardware on Pi
- Falls back to mock on PC
- No code changes needed

### Error Handling
- Graceful degradation if hardware missing
- Clear error messages
- Continues running even if one component fails

### Real-Time Updates
- 10Hz update rate (100ms intervals)
- Non-blocking hardware access
- Thread-safe UI updates


