#!/bin/bash
# Helper to download image using rpi-imager

echo "This will open rpi-imager GUI to download the image"
echo "Steps:"
echo "1. Click 'Use custom image'"
echo "2. Click 'Download OS'"
echo "3. Select 'Raspberry Pi OS' (current version, NOT Legacy) → 'Desktop' (required for GUI)"
echo "4. Click Download"
echo "5. Image will be saved to ~/Downloads/"
echo ""
read -p "Press Enter to open rpi-imager, or Ctrl+C to cancel..."
rpi-imager &
echo ""
echo "After download completes, run:"
echo "  cp ~/Downloads/*raspios*.img.xz pi-image-build/downloads/"
