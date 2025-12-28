#!/bin/bash
# Complete cleanup and rebuild

set -e

cd "$(dirname "$0")"

echo "=== CLEANUP ==="
sudo bash << 'EOF'
# Unmount everything
for m in mnt/root/proc mnt/root/sys mnt/root/dev mnt/root mnt/boot; do
    mountpoint -q "$m" 2>/dev/null && umount "$m" 2>/dev/null || true
done
losetup -D 2>/dev/null || true
rm -rf mnt *.img.work build.log 2>/dev/null || true
EOF

echo "✓ Cleanup done"
echo ""
echo "=== BUILDING ==="
sudo ./build-from-image.sh


