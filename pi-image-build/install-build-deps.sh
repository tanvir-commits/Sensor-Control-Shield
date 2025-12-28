#!/bin/bash
# Install dependencies needed for image building

echo "Installing build dependencies..."

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo "Please run with sudo"
    exit 1
fi

# Install required packages
apt-get update
apt-get install -y \
    qemu-user-static \
    kpartx \
    parted \
    dosfstools \
    git \
    wget \
    xz-utils \
    binfmt-support \
    coreutils

echo "✓ Build dependencies installed"
echo
echo "You can now run: sudo ./build-from-image.sh"

