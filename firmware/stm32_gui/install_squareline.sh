#!/bin/bash
# SquareLine Studio Installation Script
# Download and install SquareLine Studio for Linux

set -e

INSTALL_DIR="$HOME/.local/share/SquareLine-Studio"
BIN_DIR="$HOME/.local/bin"
APPIMAGE_NAME="SquareLine_Studio_*.AppImage"

echo "SquareLine Studio Installation Script"
echo "======================================"
echo ""
echo "This script will help you install SquareLine Studio."
echo ""
echo "Please download SquareLine Studio manually:"
echo "1. Visit: https://squareline.studio/downloads"
echo "2. Download the Linux AppImage version"
echo "3. Save it to: ~/Downloads/SquareLine_Studio_*.AppImage"
echo ""
read -p "Have you downloaded the AppImage? (y/n) " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Please download SquareLine Studio first, then run this script again."
    exit 1
fi

# Find the AppImage
APPIMAGE=$(find ~/Downloads -name "SquareLine_Studio_*.AppImage" 2>/dev/null | head -1)

if [ -z "$APPIMAGE" ]; then
    echo "Error: Could not find SquareLine Studio AppImage in ~/Downloads"
    echo "Please download it and place it in ~/Downloads/"
    exit 1
fi

echo "Found: $APPIMAGE"

# Create directories
mkdir -p "$INSTALL_DIR"
mkdir -p "$BIN_DIR"

# Copy AppImage
echo "Installing to $INSTALL_DIR..."
cp "$APPIMAGE" "$INSTALL_DIR/"
chmod +x "$INSTALL_DIR"/SquareLine_Studio_*.AppImage

# Create symlink
LATEST_APPIMAGE=$(ls -t "$INSTALL_DIR"/SquareLine_Studio_*.AppImage | head -1)
ln -sf "$LATEST_APPIMAGE" "$BIN_DIR/squareline-studio"

echo ""
echo "Installation complete!"
echo ""
echo "You can now run SquareLine Studio with:"
echo "  squareline-studio"
echo ""
echo "Or directly:"
echo "  $LATEST_APPIMAGE"
echo ""
echo "To open your project:"
echo "1. Launch SquareLine Studio"
echo "2. File > Open Project"
echo "3. Navigate to: $(pwd)/ui"
echo ""



