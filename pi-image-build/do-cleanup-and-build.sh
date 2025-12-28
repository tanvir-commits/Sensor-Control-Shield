#!/bin/bash
# Cleanup and rebuild script

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "=== Step 1: Cleaning up previous build ==="

# Unmount bind mounts
for mount in mnt/root/proc mnt/root/sys mnt/root/dev; do
    if mountpoint -q "$mount" 2>/dev/null; then
        echo "Unmounting $mount..."
        umount "$mount" 2>/dev/null || true
    fi
done

# Unmount partitions
for mount in mnt/root mnt/boot; do
    if mountpoint -q "$mount" 2>/dev/null; then
        echo "Unmounting $mount..."
        umount "$mount" 2>/dev/null || true
    fi
done

# Remove loop devices
echo "Removing loop devices..."
losetup -D 2>/dev/null || true

# Remove mount directory and work files
echo "Removing build artifacts..."
rm -rf mnt
rm -f *.img.work
rm -f build.log

echo "✓ Cleanup complete"
echo ""
echo "=== Step 2: Starting build ==="
echo ""

# Run the build script
exec ./build-from-image.sh


