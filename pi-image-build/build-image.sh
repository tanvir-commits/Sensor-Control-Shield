#!/bin/bash
# Automated Raspberry Pi OS Image Builder
# Creates custom image with Device Panel pre-installed

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "=========================================="
echo "Device Panel - Pi OS Image Builder"
echo "=========================================="
echo

# Check if running on Linux
if [[ "$OSTYPE" != "linux-gnu"* ]]; then
    echo "Error: This script must run on Linux"
    exit 1
fi

# Check for required tools
for cmd in git; do
    if ! command -v $cmd &> /dev/null; then
        echo "Error: $cmd is required but not installed"
        exit 1
    fi
done

echo "This script will guide you through building a custom Pi OS image."
echo "Choose your build method:"
echo
echo "1) Live Pi Build (Recommended - Easiest)"
echo "   - Flash standard Pi OS to SD card"
echo "   - Boot Pi and run setup script"
echo "   - Create image from configured SD card"
echo
echo "2) Manual Build Instructions"
echo "   - See BUILD_INSTRUCTIONS.md for detailed steps"
echo
read -p "Choose option (1 or 2): " choice

case $choice in
    1)
        echo
        echo "=== Live Pi Build Method ==="
        echo
        echo "Steps:"
        echo "1. Flash standard Raspberry Pi OS to SD card"
        echo "2. Boot Pi and complete initial setup"
        echo "3. Run the setup script on the Pi:"
        echo "   git clone https://github.com/tanvir-commits/Sensor-Control-Shield.git"
        echo "   cd Sensor-Control-Shield/pi-image-build"
        echo "   ./setup-on-pi.sh"
        echo "4. Test everything works"
        echo "5. On another computer, create image from SD card:"
        echo "   sudo dd if=/dev/sdX of=device-panel-v1.0.img bs=4M status=progress"
        echo "   xz device-panel-v1.0.img"
        echo
        echo "See BUILD_INSTRUCTIONS.md for detailed steps."
        ;;
    2)
        echo
        echo "Opening BUILD_INSTRUCTIONS.md..."
        if command -v less &> /dev/null; then
            less BUILD_INSTRUCTIONS.md
        else
            cat BUILD_INSTRUCTIONS.md
        fi
        ;;
    *)
        echo "Invalid choice"
        exit 1
        ;;
esac

echo
echo "=========================================="
echo "Build instructions displayed above"
echo "=========================================="


