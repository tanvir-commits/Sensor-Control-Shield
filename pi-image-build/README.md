# Raspberry Pi OS Image Builder

This folder contains everything needed to build a custom Raspberry Pi OS image with Device Panel pre-installed.

## Quick Start

### Method 1: Automated Image File Modification (Recommended)
```bash
# Install build dependencies (one time)
sudo ./install-build-deps.sh

# Build custom image
sudo ./build-from-image.sh
```

This will:
1. Download Raspberry Pi OS image
2. Mount it
3. Enable I2C/SPI at kernel level
4. Enable SSH
5. Install all dependencies
6. Install Device Panel
7. Configure auto-start
8. Create final compressed image

### Method 2: Live Pi Build
See `BUILD_INSTRUCTIONS.md` for manual steps using a physical Pi.

## What Gets Built

- Custom Raspberry Pi OS image (`.img.xz` file)
- I2C and SPI enabled at kernel level
- SSH enabled by default
- Device Panel GUI pre-installed
- Auto-starts on boot
- All dependencies installed
- Ready to flash and use

## Requirements

- Linux system (Ubuntu/Debian recommended)
- Root/sudo access
- ~4GB free disk space
- Internet connection (for downloading base image)

## Build Dependencies

Run `sudo ./install-build-deps.sh` to install:
- qemu-user-static (for ARM emulation)
- kpartx, parted (for image manipulation)
- git, wget, xz-utils (for downloading/extracting)

## Output

After building, you'll get:
- `device-panel-v1.0.img.xz` - Compressed image file
- `device-panel-v1.0.img.xz.sha256` - Checksum file

## Flashing the Image

```bash
# Extract and flash
xzcat device-panel-v1.0.img.xz | sudo dd of=/dev/sdX bs=4M status=progress

# Or use Raspberry Pi Imager (supports .xz files directly)
```

## Clean Up

To remove build artifacts:
```bash
./clean.sh
```

This removes:
- Downloaded images
- Mounted partitions
- Build artifacts
- Everything except source scripts

## Files

- `build-from-image.sh` - Main automated build script
- `install-build-deps.sh` - Install build dependencies
- `setup-on-pi.sh` - Alternative: setup script for live Pi
- `BUILD_INSTRUCTIONS.md` - Detailed manual build steps
- `config/` - Configuration files for image
- `scripts/` - Helper scripts
- `.gitignore` - Excludes build artifacts
