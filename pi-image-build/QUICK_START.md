# Quick Start - Build Custom Pi OS Image

## Step 1: Download Raspberry Pi OS Image

You need to download a Raspberry Pi OS image first. Choose one method:

### Method A: Using rpi-imager (Easiest)
```bash
rpi-imager
```
1. Click "Use custom image" → "Download OS"
2. Select "Raspberry Pi OS" (standard version, NOT "Full") → This has desktop environment
   - Standard version is sufficient (Full adds extra apps we don't need)
3. Click Download (don't flash to device)
4. Image will be in `~/Downloads/`
5. Copy to build directory:
   ```bash
   cp ~/Downloads/*raspios*.img.xz pi-image-build/downloads/
   ```

### Method B: Manual Download
1. Visit: https://www.raspberrypi.com/software/operating-systems/
2. Download: **Raspberry Pi OS** (standard version, NOT "Full")
   - Standard version has desktop environment (required for GUI)
   - Full version adds extra apps we don't need
   - **NOT** "Legacy" (that's the old Bullseye version)
3. Save to: `pi-image-build/downloads/`

## Step 2: Build Custom Image

```bash
cd pi-image-build
sudo ./build-from-image.sh
```

The script will:
- Use the image you downloaded
- Enable I2C/SPI at kernel level
- Enable SSH
- Install all dependencies
- Install Device Panel
- Configure auto-start
- Create `device-panel-v1.0.img.xz`

## Step 3: Flash Image

```bash
# Extract and flash
xzcat device-panel-v1.0.img.xz | sudo dd of=/dev/sdX bs=4M status=progress

# Or use Raspberry Pi Imager (supports .xz files)
rpi-imager device-panel-v1.0.img.xz
```

## That's It!

Boot the Pi and Device Panel GUI will start automatically!

