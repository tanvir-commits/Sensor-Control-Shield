#!/bin/bash
# Setup script for Raspberry Pi

echo "=========================================="
echo "Device Panel - Raspberry Pi Setup"
echo "=========================================="
echo

# Check if running on Raspberry Pi
if ! grep -q "Raspberry Pi" /proc/cpuinfo 2>/dev/null; then
    echo "⚠️  Warning: This doesn't appear to be a Raspberry Pi"
    echo "   Continuing anyway..."
    echo
fi

# Enable I2C and SPI
echo "1. Enabling I2C and SPI interfaces..."
if command -v raspi-config &> /dev/null; then
    echo "   Run: sudo raspi-config"
    echo "   Navigate to: Interface Options > I2C > Enable"
    echo "   Navigate to: Interface Options > SPI > Enable"
    echo
else
    echo "   raspi-config not found. Enable I2C/SPI manually in /boot/config.txt"
    echo
fi

# Add user to groups
echo "2. Adding user to hardware groups..."
sudo usermod -aG gpio,i2c,spi $USER
echo "   ✓ Added to gpio, i2c, spi groups"
echo "   ⚠️  You may need to log out and back in for groups to take effect"
echo

# Install system packages
echo "3. Installing system packages..."
sudo apt-get update
sudo apt-get install -y python3-pip python3-venv i2c-tools
echo "   ✓ System packages installed"
echo

# Create virtual environment
echo "4. Setting up Python virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "   ✓ Virtual environment created"
else
    echo "   ✓ Virtual environment already exists"
fi

source venv/bin/activate

# Install Python packages
echo "5. Installing Python packages..."
pip install --upgrade pip
pip install -r requirements_pi.txt
echo "   ✓ Python packages installed"
echo

echo "=========================================="
echo "Setup Complete!"
echo "=========================================="
echo
echo "Next steps:"
echo "1. Log out and back in (for group changes)"
echo "2. Enable I2C/SPI: sudo raspi-config"
echo "3. Run: source venv/bin/activate"
echo "4. Run: python3 device_panel.py"
echo


