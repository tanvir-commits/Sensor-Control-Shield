# Quick Fix: Device Panel Not Showing on Screen

## Problem
Device Panel service is running but GUI is not visible on the Pi's screen.

## Quick Fix (Run on Pi)

Open a terminal on the Pi and run:

```bash
# Copy this script to the Pi, or run these commands directly:

# 1. Stop the service
sudo systemctl stop device-panel.service

# 2. Make sure you're logged into the desktop (not just SSH)

# 3. Launch manually to see errors
cd /opt/device-panel
export DISPLAY=:0
python3 device_panel.py
```

## Common Issues & Solutions

### Issue 1: User Not Logged Into Desktop
**Problem:** GUI apps need a logged-in desktop session.

**Solution:**
- Make sure you're logged into the Raspberry Pi Desktop
- Don't just SSH in - you need to be at the physical screen or VNC

### Issue 2: XAUTHORITY Missing
**Problem:** X server authentication file doesn't exist.

**Solution:**
```bash
# Log out and log back into the desktop
# This creates ~/.Xauthority automatically
```

### Issue 3: DISPLAY Not Set
**Problem:** Application doesn't know which display to use.

**Solution:**
```bash
export DISPLAY=:0
cd /opt/device-panel
python3 device_panel.py
```

### Issue 4: Service Running But No GUI
**Problem:** Service runs but can't access display.

**Solution - Use Desktop Autostart Instead:**

```bash
# Create autostart entry
mkdir -p ~/.config/autostart
cat > ~/.config/autostart/device-panel.desktop << 'EOF'
[Desktop Entry]
Type=Application
Name=Device Panel
Exec=/usr/bin/python3 /opt/device-panel/device_panel.py
Terminal=false
X-GNOME-Autostart-enabled=true
EOF

chmod +x ~/.config/autostart/device-panel.desktop

# Disable systemd service (autostart is more reliable for GUI)
sudo systemctl disable device-panel.service
sudo systemctl stop device-panel.service
```

Then **log out and log back in** - Device Panel will start automatically.

## Test Manual Launch

To test if it works manually:

```bash
cd /opt/device-panel
export DISPLAY=:0
python3 device_panel.py &
```

If you see the GUI, the issue is just autostart configuration.
If you see errors, share them and we can fix them.

## Best Solution: Desktop Autostart

For GUI applications, desktop autostart is more reliable than systemd:

1. The user must be logged in (required for GUI)
2. XAUTHORITY is automatically available
3. DISPLAY is set correctly
4. Works with the desktop session

Use the autostart method above for best results.

