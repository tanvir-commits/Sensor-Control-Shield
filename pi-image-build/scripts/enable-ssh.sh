#!/bin/bash
# Enable SSH in the image

MOUNT_POINT=$1

if [ -z "$MOUNT_POINT" ]; then
    echo "Usage: $0 <mount_point>"
    exit 1
fi

echo "Enabling SSH..."

# Method 1: Create /boot/ssh file (enables SSH on first boot)
if [ -d "$MOUNT_POINT/boot" ]; then
    sudo touch "$MOUNT_POINT/boot/ssh"
    echo "✓ Created /boot/ssh"
fi

# Method 2: Enable SSH service in systemd
if [ -d "$MOUNT_POINT/etc/systemd/system" ]; then
    sudo mkdir -p "$MOUNT_POINT/etc/systemd/system/ssh.service.d"
    sudo ln -sf /lib/systemd/system/ssh.service "$MOUNT_POINT/etc/systemd/system/multi-user.target.wants/ssh.service" 2>/dev/null
    echo "✓ Enabled SSH service"
fi

echo "SSH will be enabled on first boot"


