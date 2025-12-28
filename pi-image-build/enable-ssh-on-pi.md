# How to Enable SSH on Raspberry Pi

## Method 1: Using the Boot Partition (Headless - No Monitor Needed)

If you have physical access to the SD card:

1. **Remove SD card from Pi** and insert into your computer
2. **Mount the boot partition** (usually auto-mounts as `/boot` or `/media/...`)
3. **Create SSH file:**
   ```bash
   touch /path/to/boot/ssh
   ```
   Or on Windows/Mac, just create an empty file named `ssh` (no extension) in the boot partition
4. **Eject SD card** and insert back into Pi
5. **Boot the Pi** - SSH will be enabled automatically

## Method 2: On the Pi with Monitor/Keyboard

If you have a monitor and keyboard connected to the Pi:

```bash
# Enable SSH service
sudo systemctl enable ssh
sudo systemctl start ssh

# Or use raspi-config
sudo raspi-config
# Navigate to: Interface Options > SSH > Enable
```

## Method 3: Using raspi-config (Recommended)

On the Pi:
```bash
sudo raspi-config
```

Navigate:
1. **Interface Options**
2. **SSH**
3. **Yes** (to enable)
4. **Finish**

## Method 4: Enable via Command Line

```bash
# Enable and start SSH
sudo systemctl enable ssh
sudo systemctl start ssh

# Verify it's running
sudo systemctl status ssh
```

## Verify SSH is Working

From another computer on the same network:
```bash
# Test connection
ssh pi@192.168.0.101

# Or if you changed the default user
ssh your-username@192.168.0.101
```

## Default Credentials

- **Username:** `pi`
- **Password:** Usually needs to be set on first boot, or check Raspberry Pi documentation

## Troubleshooting

### SSH not starting?
```bash
# Check if SSH service is installed
dpkg -l | grep openssh-server

# Install if missing
sudo apt-get update
sudo apt-get install openssh-server

# Check firewall
sudo ufw status
# If enabled, allow SSH:
sudo ufw allow ssh
```

### Can't connect?
1. **Check Pi is on network:**
   ```bash
   # On Pi
   ip addr show
   # or
   hostname -I
   ```

2. **Check SSH is listening:**
   ```bash
   # On Pi
   sudo netstat -tlnp | grep :22
   # Should show sshd listening on port 22
   ```

3. **Check firewall on your computer** (not blocking outbound SSH)

4. **Try ping first:**
   ```bash
   ping 192.168.0.101
   ```

## Our Custom Image

The custom image we built **should already have SSH enabled** because we added:
- `touch "$MOUNT_DIR/boot/ssh"` in the build script

If SSH isn't working, try Method 1 above to re-enable it.

