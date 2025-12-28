#!/bin/bash
# Setup script to run ON the Raspberry Pi
# This configures a fresh Pi OS installation for Device Panel

set -e

echo "=========================================="
echo "Device Panel - Pi Setup Script"
echo "=========================================="
echo

# Check if running on Raspberry Pi
if ! grep -q "Raspberry Pi" /proc/cpuinfo 2>/dev/null; then
    echo "⚠️  Warning: This doesn't appear to be a Raspberry Pi"
    read -p "Continue anyway? (y/n): " confirm
    if [ "$confirm" != "y" ]; then
        exit 1
    fi
fi

# Step 1: Enable I2C and SPI
echo "Step 1: Enabling I2C and SPI..."
if command -v raspi-config &> /dev/null; then
    echo "   Run: sudo raspi-config"
    echo "   Navigate to: Interface Options > I2C > Enable"
    echo "   Navigate to: Interface Options > SPI > Enable"
    read -p "   Press Enter after enabling I2C/SPI and rebooting..."
else
    # Manual config.txt edit
    echo "   Editing /boot/config.txt manually..."
    sudo sed -i 's/#dtparam=i2c_arm=on/dtparam=i2c_arm=on/' /boot/config.txt
    sudo sed -i 's/#dtparam=spi=on/dtparam=spi=on/' /boot/config.txt
    if ! grep -q "dtparam=i2c_arm=on" /boot/config.txt; then
        echo "dtparam=i2c_arm=on" | sudo tee -a /boot/config.txt
    fi
    if ! grep -q "dtparam=spi=on" /boot/config.txt; then
        echo "dtparam=spi=on" | sudo tee -a /boot/config.txt
    fi
    echo "   ✓ I2C/SPI enabled (reboot required)"
    read -p "   Reboot now? (y/n): " reboot_now
    if [ "$reboot_now" = "y" ]; then
        sudo reboot
    fi
fi

# Step 2: Update system
echo
echo "Step 2: Updating system..."
sudo apt-get update
sudo apt-get upgrade -y

# Step 3: Install system packages
echo
echo "Step 3: Installing system packages..."
sudo apt-get install -y python3-pip python3-venv i2c-tools git

# Step 4: Add user to groups
echo
echo "Step 4: Adding user to hardware groups..."
sudo usermod -aG gpio,i2c,spi $USER
echo "   ✓ Added to gpio, i2c, spi groups"
echo "   ⚠️  You may need to log out and back in"

# Step 5: Install Python dependencies
echo
echo "Step 5: Installing Python dependencies..."
pip3 install --break-system-packages \
    pyside6 \
    gpiozero \
    adafruit-circuitpython-ads1x15 \
    smbus2 \
    spidev \
    pyserial

# Step 6: Install Device Panel
echo
echo "Step 6: Installing Device Panel..."
if [ ! -d "/opt/device-panel" ]; then
    sudo mkdir -p /opt/device-panel
    if [ -d "$(dirname $0)/../device_panel.py" ]; then
        # Copy from current location
        sudo cp -r $(dirname $0)/../* /opt/device-panel/ 2>/dev/null || true
        sudo rm -rf /opt/device-panel/pi-image-build 2>/dev/null || true
    else
        # Clone from GitHub
        sudo git clone https://github.com/tanvir-commits/Sensor-Control-Shield.git /opt/device-panel
    fi
    sudo chown -R $USER:$USER /opt/device-panel
    echo "   ✓ Device Panel installed to /opt/device-panel"
else
    echo "   ⚠️  /opt/device-panel already exists, skipping"
fi

# Step 7: Enable SSH
echo
echo "Step 7: Enabling SSH..."
sudo systemctl enable ssh
sudo systemctl start ssh
sudo touch /boot/ssh
echo "   ✓ SSH enabled"

# Step 8: Configure auto-start
echo
echo "Step 8: Configuring auto-start..."
if [ -f "config/device-panel.service" ]; then
    sudo cp config/device-panel.service /etc/systemd/system/
    sudo systemctl daemon-reload
    sudo systemctl enable device-panel.service
    echo "   ✓ Auto-start configured"
else
    echo "   ⚠️  Service file not found, creating manually..."
    sudo tee /etc/systemd/system/device-panel.service > /dev/null << 'EOF'
[Unit]
Description=Device Panel GUI Application
After=graphical.target network-online.target
Wants=graphical.target

[Service]
Type=simple
User=pi
Group=pi
Environment=DISPLAY=:0
Environment=XAUTHORITY=/home/pi/.Xauthority
WorkingDirectory=/opt/device-panel
ExecStart=/usr/bin/python3 /opt/device-panel/device_panel.py
Restart=on-failure
RestartSec=5

[Install]
WantedBy=graphical.target
EOF
    sudo systemctl daemon-reload
    sudo systemctl enable device-panel.service
    echo "   ✓ Auto-start configured"
fi

# Step 9: Verify
echo
echo "Step 9: Verifying installation..."
echo "   I2C: $(ls /dev/i2c-* 2>/dev/null | wc -l) device(s) found"
echo "   SPI: $(ls /dev/spidev* 2>/dev/null | wc -l) device(s) found"
echo "   SSH: $(sudo systemctl is-active ssh)"
echo "   Device Panel: $(test -f /opt/device-panel/device_panel.py && echo 'Installed' || echo 'Missing')"

echo
echo "=========================================="
echo "Setup Complete!"
echo "=========================================="
echo
echo "Next steps:"
echo "1. Reboot: sudo reboot"
echo "2. After reboot, Device Panel should start automatically"
echo "3. To test manually: python3 /opt/device-panel/device_panel.py"
echo "4. To create image: See BUILD_INSTRUCTIONS.md"
echo


