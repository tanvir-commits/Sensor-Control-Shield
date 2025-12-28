#!/bin/bash
# Install Python dependencies in the image

MOUNT_POINT=$1

if [ -z "$MOUNT_POINT" ]; then
    echo "Usage: $0 <mount_point>"
    exit 1
fi

echo "Installing Python dependencies..."

# We'll use a first-boot script since we can't easily run pip in chroot
# Create installation script that runs on first boot
cat > /tmp/install-deps.sh << 'EOF'
#!/bin/bash
set -e

echo "Installing Device Panel dependencies..."

# Update package list
apt-get update

# Install system packages
apt-get install -y python3-pip python3-venv i2c-tools

# Install Python packages
pip3 install --break-system-packages \
    pyside6 \
    gpiozero \
    adafruit-circuitpython-ads1x15 \
    smbus2 \
    spidev \
    pyserial

# Add user to groups
usermod -aG gpio,i2c,spi pi

echo "✓ Dependencies installed"
EOF

sudo mkdir -p "$MOUNT_POINT/opt/device-panel"
sudo cp /tmp/install-deps.sh "$MOUNT_POINT/opt/device-panel/install-deps.sh"
sudo chmod +x "$MOUNT_POINT/opt/device-panel/install-deps.sh"

echo "✓ Dependency installation script created"
echo "  (Will run on first boot)"


