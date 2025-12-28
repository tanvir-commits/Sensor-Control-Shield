# Manual Image Build Instructions

## Prerequisites

- Raspberry Pi OS Desktop image (download from raspberrypi.com - Desktop version required for GUI)
- Linux system with:
  - `qemu-user-static` (for ARM emulation)
  - `parted`, `kpartx`, `losetup` (for image manipulation)
  - `git` (for cloning Device Panel)

## Method 1: Live Pi Build (Easiest)

### Step 1: Prepare Raspberry Pi
1. Flash standard Raspberry Pi OS Desktop to SD card (Desktop version required for GUI)
2. Boot Pi and complete initial setup
3. Connect to network

### Step 2: Configure Hardware
```bash
# Enable I2C and SPI
sudo raspi-config
# Interface Options > I2C > Enable
# Interface Options > SPI > Enable
sudo reboot
```

### Step 3: Install Dependencies
```bash
sudo apt-get update
sudo apt-get install -y python3-pip python3-venv i2c-tools
sudo usermod -aG gpio,i2c,spi pi
pip3 install pyside6 gpiozero adafruit-circuitpython-ads1x15 smbus2 spidev pyserial
```

### Step 4: Install Device Panel
```bash
sudo mkdir -p /opt/device-panel
cd /opt/device-panel
sudo git clone https://github.com/tanvir-commits/Sensor-Control-Shield.git .
sudo chown -R pi:pi /opt/device-panel
```

### Step 5: Enable SSH
```bash
sudo systemctl enable ssh
sudo systemctl start ssh
sudo touch /boot/ssh
```

### Step 6: Configure Auto-Start
```bash
# Copy systemd service
sudo cp /opt/device-panel/pi-image-build/config/device-panel.service /etc/systemd/system/
sudo systemctl enable device-panel.service
```

### Step 7: Test Everything
```bash
# Verify I2C
i2cdetect -y 1

# Verify SPI
ls /dev/spidev*

# Test GUI
python3 /opt/device-panel/device_panel.py

# Check services
sudo systemctl status ssh
sudo systemctl status device-panel.service
```

### Step 8: Create Image
On another computer with SD card reader:
```bash
# Find SD card device (be careful!)
lsblk

# Create image (replace sdX with your device)
sudo dd if=/dev/sdX of=device-panel-v1.0.img bs=4M status=progress

# Compress
xz device-panel-v1.0.img

# Create checksum
sha256sum device-panel-v1.0.img.xz > device-panel-v1.0.img.xz.sha256
```

## Method 2: Image Customization (Advanced)

This method modifies the image file directly without booting a Pi.

### Step 1: Download Base Image
```bash
mkdir -p downloads
cd downloads
wget https://downloads.raspberrypi.com/raspios_armhf/images/raspios_armhf-*/raspios-*.img.xz
unxz raspios-*.img.xz
```

### Step 2: Mount Image
```bash
cd ..
mkdir -p mnt/boot mnt/root

# Find loop device
LOOP_DEV=$(sudo losetup --find --show downloads/raspios-*.img)
sudo partprobe $LOOP_DEV

# Mount partitions
sudo mount ${LOOP_DEV}p1 mnt/boot
sudo mount ${LOOP_DEV}p2 mnt/root
```

### Step 3: Configure Boot
```bash
# Enable I2C/SPI in config.txt
sudo cp config/boot-config.txt mnt/boot/config.txt

# Enable SSH
sudo touch mnt/boot/ssh
```

### Step 4: Install Device Panel (using chroot)
```bash
# Copy qemu for ARM emulation
sudo cp /usr/bin/qemu-arm-static mnt/root/usr/bin/

# Copy Device Panel
sudo cp -r ../* mnt/root/opt/device-panel/ 2>/dev/null || true

# Chroot and install
sudo chroot mnt/root /bin/bash << 'EOF'
cd /opt/device-panel
apt-get update
apt-get install -y python3-pip
pip3 install pyside6 gpiozero adafruit-circuitpython-ads1x15 smbus2 spidev pyserial
EOF
```

### Step 5: Configure Services
```bash
# Copy systemd service
sudo cp config/device-panel.service mnt/root/etc/systemd/system/
sudo chroot mnt/root systemctl enable device-panel.service
```

### Step 6: Unmount and Create Final Image
```bash
sudo umount mnt/boot mnt/root
sudo losetup -d $LOOP_DEV

# Copy and compress
cp downloads/raspios-*.img device-panel-v1.0.img
xz device-panel-v1.0.img
sha256sum device-panel-v1.0.img.xz > device-panel-v1.0.img.xz.sha256
```

## Verification

After creating image, verify:
- Image size is reasonable (~2-4GB compressed)
- Checksum matches
- Can be flashed with Raspberry Pi Imager
- Boots and shows Device Panel GUI
- I2C/SPI work: `i2cdetect -y 1` and `ls /dev/spidev*`
- SSH accessible: `ssh pi@<pi-ip>`

