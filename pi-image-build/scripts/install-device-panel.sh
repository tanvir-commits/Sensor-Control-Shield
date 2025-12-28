#!/bin/bash
# Install Device Panel into the image

MOUNT_POINT=$1
REPO_URL=${2:-"https://github.com/tanvir-commits/Sensor-Control-Shield.git"}

if [ -z "$MOUNT_POINT" ]; then
    echo "Usage: $0 <mount_point> [repo_url]"
    exit 1
fi

echo "Installing Device Panel..."

# Create directory
sudo mkdir -p "$MOUNT_POINT/opt/device-panel"

# Clone repository (if we have network access in chroot)
# Otherwise, we'll copy from local source
if [ -d "../.." ] && [ -f "../../device_panel.py" ]; then
    echo "Copying Device Panel from local source..."
    sudo cp -r ../../* "$MOUNT_POINT/opt/device-panel/" 2>/dev/null
    sudo rm -rf "$MOUNT_POINT/opt/device-panel/pi-image-build" 2>/dev/null
else
    echo "Note: Repository will be cloned on first boot"
    # Create a first-boot script to clone the repo
    cat > /tmp/install-device-panel.sh << 'EOF'
#!/bin/bash
cd /opt/device-panel
git clone https://github.com/tanvir-commits/Sensor-Control-Shield.git .
chown -R pi:pi /opt/device-panel
EOF
    sudo cp /tmp/install-device-panel.sh "$MOUNT_POINT/opt/device-panel/install.sh"
    sudo chmod +x "$MOUNT_POINT/opt/device-panel/install.sh"
fi

# Set permissions
sudo chown -R 1000:1000 "$MOUNT_POINT/opt/device-panel" 2>/dev/null || \
sudo chown -R pi:pi "$MOUNT_POINT/opt/device-panel" 2>/dev/null

echo "✓ Device Panel installed to /opt/device-panel"


