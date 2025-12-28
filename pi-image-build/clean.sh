#!/bin/bash
# Clean up build artifacts

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "Cleaning up build artifacts..."

# Unmount if mounted
if mountpoint -q "mnt/root/proc" 2>/dev/null; then
    sudo umount mnt/root/proc 2>/dev/null || true
fi
if mountpoint -q "mnt/root/sys" 2>/dev/null; then
    sudo umount mnt/root/sys 2>/dev/null || true
fi
if mountpoint -q "mnt/root/dev" 2>/dev/null; then
    sudo umount mnt/root/dev 2>/dev/null || true
fi
if mountpoint -q "mnt/root" 2>/dev/null; then
    sudo umount mnt/root 2>/dev/null || true
fi
if mountpoint -q "mnt/boot" 2>/dev/null; then
    sudo umount mnt/boot 2>/dev/null || true
fi

# Remove loop devices (find any associated with our images)
for loop in $(losetup -l | grep -E "(device-panel|raspios)" | awk '{print $1}'); do
    sudo kpartx -d "$loop" 2>/dev/null || true
    sudo losetup -d "$loop" 2>/dev/null || true
done

# Remove build artifacts
rm -rf mnt
rm -f *.img.work
rm -f build.log

echo "✓ Cleanup complete"
echo ""
echo "Note: Downloaded images in downloads/ are kept"
echo "      To remove them: rm -rf downloads/"
