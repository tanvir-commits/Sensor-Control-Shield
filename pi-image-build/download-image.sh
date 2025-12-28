#!/bin/bash
# Helper script to download Raspberry Pi OS image

echo "Raspberry Pi OS Image Download Helper"
echo "======================================"
echo
echo "Option 1: Use Raspberry Pi Imager (Recommended)"
echo "  - Install: sudo apt install rpi-imager"
echo "  - Run: rpi-imager"
echo "  - Download image (don't flash)"
echo "  - Image saved to: ~/Downloads/"
echo "  - Copy to: pi-image-build/downloads/"
echo
echo "Option 2: Manual Download"
echo "  Visit: https://www.raspberrypi.com/software/operating-systems/"
echo "  Download: Raspberry Pi OS (current version, NOT Legacy) - Desktop (required for GUI)"
echo "  Save to: pi-image-build/downloads/"
echo
echo "Option 3: Direct Download (if URL known)"
echo "  wget <image-url> -O downloads/raspios.img.xz"
echo
