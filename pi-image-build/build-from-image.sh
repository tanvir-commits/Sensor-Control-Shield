#!/bin/bash
# Automated Pi OS Image Customization
# Downloads, modifies, and creates custom image with Device Panel

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Configuration
# Try to auto-detect latest, or specify manually
# Latest as of 2024: https://downloads.raspberrypi.com/raspios_armhf/images/
IMAGE_VERSION=""  # Will be auto-detected or you can set manually
BASE_URL="https://downloads.raspberrypi.com/raspios_armhf/images"

# Alternative: Use latest from raspberrypi.com
# Check https://downloads.raspberrypi.com/raspios_armhf/images/ for latest
OUTPUT_IMAGE="device-panel-v1.0.img"
MOUNT_DIR="mnt"
DOWNLOAD_DIR="downloads"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check for root
if [ "$EUID" -ne 0 ]; then 
    log_error "This script must be run as root (use sudo)"
    exit 1
fi

# Check for required tools
log_info "Checking required tools..."
for cmd in losetup kpartx qemu-arm-static git wget xz parted resize2fs e2fsck; do
    if ! command -v $cmd &> /dev/null; then
        log_error "$cmd is required but not installed"
        log_info "Install with: sudo apt-get install $cmd"
        exit 1
    fi
done
log_info "✓ All required tools available"

# Cleanup function
cleanup() {
    log_info "Cleaning up..."
    
    # Unmount bind mounts first
    if mountpoint -q "$MOUNT_DIR/root/proc" 2>/dev/null; then
        umount "$MOUNT_DIR/root/proc" 2>/dev/null || true
    fi
    if mountpoint -q "$MOUNT_DIR/root/sys" 2>/dev/null; then
        umount "$MOUNT_DIR/root/sys" 2>/dev/null || true
    fi
    if mountpoint -q "$MOUNT_DIR/root/dev" 2>/dev/null; then
        umount "$MOUNT_DIR/root/dev" 2>/dev/null || true
    fi
    
    # Unmount partitions
    if mountpoint -q "$MOUNT_DIR/root" 2>/dev/null; then
        umount "$MOUNT_DIR/root" 2>/dev/null || true
    fi
    if mountpoint -q "$MOUNT_DIR/boot" 2>/dev/null; then
        umount "$MOUNT_DIR/boot" 2>/dev/null || true
    fi
    
    # Remove loop devices
    if [ -n "$LOOP_DEV" ]; then
        kpartx -d "$LOOP_DEV" 2>/dev/null || true
        losetup -d "$LOOP_DEV" 2>/dev/null || true
    fi
    
    # Remove mount directory (ignore errors from virtual filesystems)
    rm -rf "$MOUNT_DIR" 2>/dev/null || true
    
    log_info "Cleanup complete"
}

trap cleanup EXIT

# Step 1: Download or use existing image
log_info "Step 1: Preparing Raspberry Pi OS image..."
mkdir -p "$DOWNLOAD_DIR"
cd "$DOWNLOAD_DIR"

# Check if user has manually downloaded an image
if ls *.img 2>/dev/null | grep -q .; then
    IMAGE_FILE=$(ls -t *.img | head -1)
    log_info "Using existing image: $IMAGE_FILE"
elif ls *.img.xz 2>/dev/null | grep -q .; then
    IMAGE_XZ=$(ls -t *.img.xz | head -1)
    log_info "Found compressed image: $IMAGE_XZ"
    if [ ! -f "${IMAGE_XZ%.xz}" ]; then
        log_info "Extracting..."
        xz -d "$IMAGE_XZ"
    fi
    IMAGE_FILE="${IMAGE_XZ%.xz}"
else
    log_error "No Raspberry Pi OS image found!"
    log_info ""
    log_info "Please download a Raspberry Pi OS image:"
    log_info "1. Visit: https://www.raspberrypi.com/software/operating-systems/"
    log_info "2. Download: Raspberry Pi OS (standard version, NOT 'Full', NOT Legacy)"
    log_info "   Standard version has desktop environment (required for GUI)"
    log_info "3. Place the .img or .img.xz file in: $DOWNLOAD_DIR/"
    log_info ""
    log_info "Or use Raspberry Pi Imager to download directly"
    log_info ""
    read -p "Press Enter after placing image file in $DOWNLOAD_DIR/, or Ctrl+C to cancel..."
    
    if ls *.img 2>/dev/null | grep -q .; then
        IMAGE_FILE=$(ls -t *.img | head -1)
    elif ls *.img.xz 2>/dev/null | grep -q .; then
        IMAGE_XZ=$(ls -t *.img.xz | head -1)
        xz -d "$IMAGE_XZ"
        IMAGE_FILE="${IMAGE_XZ%.xz}"
    else
        log_error "Still no image found. Exiting."
        exit 1
    fi
fi

log_info "✓ Using image: $IMAGE_FILE"
cd ..

# Step 2: Create working copy and expand
log_info "Step 2: Creating working copy of image..."
WORK_IMAGE="${OUTPUT_IMAGE}.work"
log_info "Copying image (this may take a while)..."
cp "$DOWNLOAD_DIR/$IMAGE_FILE" "$WORK_IMAGE"
log_info "✓ Working copy created: $WORK_IMAGE"

# Expand image by 2GB to have room for packages
log_info "Expanding image by 2GB for package installation..."
dd if=/dev/zero bs=1M count=2048 >> "$WORK_IMAGE" 2>/dev/null
log_info "✓ Image expanded"

# Step 3: Setup loop device, expand partition, and mount
log_info "Step 3: Setting up image partitions..."
LOOP_DEV=$(losetup --find --show -P "$WORK_IMAGE")
sleep 2  # Wait for partitions to be ready

# Expand partition 2 to fill the extra space we added
log_info "Expanding partition 2 to use all available space..."
parted "$LOOP_DEV" --script resizepart 2 100%
sleep 1

# Resize filesystem
log_info "Resizing filesystem..."
e2fsck -f "${LOOP_DEV}p2" || true
resize2fs "${LOOP_DEV}p2"
log_info "✓ Partition expanded"

mkdir -p "$MOUNT_DIR/boot" "$MOUNT_DIR/root"

# Mount partitions
mount "${LOOP_DEV}p1" "$MOUNT_DIR/boot"
mount "${LOOP_DEV}p2" "$MOUNT_DIR/root"

log_info "✓ Image mounted"

# Step 4: Configure boot
log_info "Step 4: Configuring boot settings..."

# Enable I2C/SPI in config.txt
if ! grep -q "dtparam=i2c_arm=on" "$MOUNT_DIR/boot/config.txt"; then
    echo "" >> "$MOUNT_DIR/boot/config.txt"
    echo "# Device Panel - Enable I2C" >> "$MOUNT_DIR/boot/config.txt"
    echo "dtparam=i2c_arm=on" >> "$MOUNT_DIR/boot/config.txt"
    echo "dtparam=i2c_arm_baudrate=100000" >> "$MOUNT_DIR/boot/config.txt"
fi

if ! grep -q "dtparam=spi=on" "$MOUNT_DIR/boot/config.txt"; then
    echo "# Device Panel - Enable SPI" >> "$MOUNT_DIR/boot/config.txt"
    echo "dtparam=spi=on" >> "$MOUNT_DIR/boot/config.txt"
fi

# Enable I2C3 on GPIO4/GPIO5 (for J16 I2C_PORT_C connector)
if ! grep -q "dtoverlay=i2c3" "$MOUNT_DIR/boot/config.txt"; then
    echo "# Device Panel - Enable I2C3 (second I2C bus)" >> "$MOUNT_DIR/boot/config.txt"
    echo "dtoverlay=i2c3,pins_4_5" >> "$MOUNT_DIR/boot/config.txt"
fi

# Enable SSH
touch "$MOUNT_DIR/boot/ssh"

log_info "✓ Boot configuration updated (I2C, I2C3, SPI, SSH enabled)"

# Step 5: Setup chroot environment
log_info "Step 5: Setting up chroot environment..."

# Copy qemu for ARM emulation
if [ ! -f "$MOUNT_DIR/root/usr/bin/qemu-arm-static" ]; then
    cp /usr/bin/qemu-arm-static "$MOUNT_DIR/root/usr/bin/"
fi

# Copy DNS config
cp /etc/resolv.conf "$MOUNT_DIR/root/etc/"

# Bind mount system directories
mount --bind /dev "$MOUNT_DIR/root/dev"
mount --bind /sys "$MOUNT_DIR/root/sys"
mount --bind /proc "$MOUNT_DIR/root/proc"

log_info "✓ Chroot environment ready"

# Step 6: Install dependencies in chroot
log_info "Step 6: Installing dependencies (this may take a while)..."
if ! chroot "$MOUNT_DIR/root" /bin/bash << 'CHROOT_EOF'
set -e

# Update package list
apt-get update

# Install system packages (including base64 which may be needed by pip)
apt-get install -y python3-pip python3-venv i2c-tools git coreutils

# Install Python packages
pip3 install --break-system-packages \
    pyside6 \
    gpiozero \
    adafruit-circuitpython-ads1x15 \
    adafruit-circuitpython-ssd1306 \
    smbus2 \
    spidev \
    pyserial \
    Pillow

echo "Dependencies installed successfully"
CHROOT_EOF
then
    log_error "Failed to install dependencies in chroot"
    exit 1
fi

log_info "✓ Dependencies installed"

# Step 7: Install Device Panel
log_info "Step 7: Installing Device Panel..."

# Copy Device Panel from parent directory
DEVICE_PANEL_SOURCE="$(dirname "$SCRIPT_DIR")"
if [ -f "$DEVICE_PANEL_SOURCE/device_panel.py" ]; then
    mkdir -p "$MOUNT_DIR/root/opt/device-panel"
    # Copy all necessary files and directories
    cp -r "$DEVICE_PANEL_SOURCE"/device_panel.py "$MOUNT_DIR/root/opt/device-panel/" 2>/dev/null || true
    cp -r "$DEVICE_PANEL_SOURCE"/ui "$MOUNT_DIR/root/opt/device-panel/" 2>/dev/null || true
    cp -r "$DEVICE_PANEL_SOURCE"/hardware "$MOUNT_DIR/root/opt/device-panel/" 2>/dev/null || true
    cp -r "$DEVICE_PANEL_SOURCE"/config "$MOUNT_DIR/root/opt/device-panel/" 2>/dev/null || true
    cp -r "$DEVICE_PANEL_SOURCE"/mock "$MOUNT_DIR/root/opt/device-panel/" 2>/dev/null || true
    cp -r "$DEVICE_PANEL_SOURCE"/devices "$MOUNT_DIR/root/opt/device-panel/" 2>/dev/null || true
    # Remove pi-image-build from the copy if it exists
    rm -rf "$MOUNT_DIR/root/opt/device-panel/pi-image-build" 2>/dev/null || true
    log_info "✓ Device Panel copied from local source (v0.1)"
else
    # Clone from GitHub in chroot (using v0.1 tag)
    chroot "$MOUNT_DIR/root" /bin/bash << 'CHROOT_EOF'
mkdir -p /opt/device-panel
cd /opt/device-panel
git clone --branch v0.1 --depth 1 https://github.com/tanvir-commits/Sensor-Control-Shield.git .
rm -rf pi-image-build
CHROOT_EOF
    log_info "✓ Device Panel cloned from GitHub (v0.1 tag)"
fi

# Set permissions (use user ID 1000 which is typically the first user)
chroot "$MOUNT_DIR/root" chown -R 1000:1000 /opt/device-panel 2>/dev/null || true

# Step 8: Configure services and desktop
log_info "Step 8: Configuring services and desktop..."

# Copy systemd service (will use user ID 1000, not hardcoded "pi")
cp config/device-panel.service "$MOUNT_DIR/root/etc/systemd/system/"

# Update service file to use user ID 1000 instead of "pi"
chroot "$MOUNT_DIR/root" /bin/bash << 'CHROOT_EOF'
# Get username for user ID 1000
USERNAME=$(id -nu 1000 2>/dev/null || echo "pi")
# Update service file
sed -i "s/User=pi/User=$USERNAME/g" /etc/systemd/system/device-panel.service
sed -i "s/Group=pi/Group=$USERNAME/g" /etc/systemd/system/device-panel.service
sed -i "s|/home/pi|/home/$USERNAME|g" /etc/systemd/system/device-panel.service
CHROOT_EOF

# Create desktop launcher for all users
mkdir -p "$MOUNT_DIR/root/usr/share/applications"
cat > "$MOUNT_DIR/root/usr/share/applications/device-panel.desktop" << 'DESKTOP'
[Desktop Entry]
Type=Application
Name=Device Panel
Comment=Hardware Control and Monitoring GUI
Exec=/usr/bin/python3 /opt/device-panel/device_panel.py
Icon=application-x-executable
Terminal=false
Categories=Utility;System;
StartupNotify=true
DESKTOP

# Create autostart for default user (user ID 1000)
chroot "$MOUNT_DIR/root" /bin/bash << 'CHROOT_EOF'
USERNAME=$(id -nu 1000 2>/dev/null || echo "pi")
USER_HOME="/home/$USERNAME"
if [ -d "$USER_HOME" ]; then
    mkdir -p "$USER_HOME/.config/autostart"
    cat > "$USER_HOME/.config/autostart/device-panel.desktop" << 'AUTOSTART'
[Desktop Entry]
Type=Application
Name=Device Panel
Comment=Hardware Control and Monitoring GUI
Exec=/usr/bin/python3 /opt/device-panel/device_panel.py
Icon=application-x-executable
Terminal=false
Categories=Utility;System;
StartupNotify=true
X-GNOME-Autostart-enabled=true
AUTOSTART
    chown -R 1000:1000 "$USER_HOME/.config" 2>/dev/null || true
fi
CHROOT_EOF

# Enable services in chroot
chroot "$MOUNT_DIR/root" /bin/bash << 'CHROOT_EOF'
# Enable SSH
systemctl enable ssh

# Enable Device Panel
systemctl enable device-panel.service

# Add user to groups (assuming user ID 1000)
if id 1000 &>/dev/null; then
    usermod -aG gpio,i2c,spi $(id -nu 1000) 2>/dev/null || true
fi
CHROOT_EOF

log_info "✓ Services and desktop configured"

# Step 9: Unmount
log_info "Step 9: Unmounting image..."
umount "$MOUNT_DIR/root/proc"
umount "$MOUNT_DIR/root/sys"
umount "$MOUNT_DIR/root/dev"
umount "$MOUNT_DIR/root"
umount "$MOUNT_DIR/boot"

kpartx -d "$LOOP_DEV"
losetup -d "$LOOP_DEV"

log_info "✓ Image unmounted"

# Step 10: Create final image
log_info "Step 10: Creating final image..."
mv "$WORK_IMAGE" "$OUTPUT_IMAGE"

# Compress
log_info "Compressing image (this may take a while)..."
xz -9 "$OUTPUT_IMAGE"

# Create checksum
sha256sum "${OUTPUT_IMAGE}.xz" > "${OUTPUT_IMAGE}.xz.sha256"

log_info "✓ Final image created: ${OUTPUT_IMAGE}.xz"
log_info "✓ Checksum: ${OUTPUT_IMAGE}.xz.sha256"

echo
log_info "=========================================="
log_info "Build Complete!"
log_info "=========================================="
echo
log_info "Image: ${OUTPUT_IMAGE}.xz"
log_info "Size: $(du -h ${OUTPUT_IMAGE}.xz | cut -f1)"
log_info "Checksum: $(cat ${OUTPUT_IMAGE}.xz.sha256)"
echo
log_info "To flash this image:"
log_info "  xzcat ${OUTPUT_IMAGE}.xz | sudo dd of=/dev/sdX bs=4M status=progress"
log_info "  Or use Raspberry Pi Imager with the .xz file"
echo

