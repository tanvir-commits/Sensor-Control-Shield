#!/bin/bash
# Fix Device Panel GUI display issues
# Run this ON THE PI directly (with monitor/keyboard)

echo "=== Device Panel GUI Display Fix ==="
echo ""

# Check if running
echo "1. Checking if Device Panel is running..."
if pgrep -f device_panel.py > /dev/null; then
    echo "✓ Device Panel process is running"
    ps aux | grep device_panel | grep -v grep
else
    echo "✗ Device Panel is NOT running"
fi
echo ""

# Check X server
echo "2. Checking X server..."
if pgrep -f Xorg > /dev/null; then
    echo "✓ X server is running"
else
    echo "✗ X server is NOT running - GUI won't work!"
fi
echo ""

# Check DISPLAY
echo "3. Checking DISPLAY environment..."
echo "DISPLAY=$DISPLAY"
if [ -z "$DISPLAY" ]; then
    echo "⚠️  DISPLAY not set, setting to :0"
    export DISPLAY=:0
fi
echo ""

# Check XAUTHORITY
echo "4. Checking XAUTHORITY..."
if [ -f ~/.Xauthority ]; then
    echo "✓ XAUTHORITY file exists"
    ls -la ~/.Xauthority
else
    echo "✗ XAUTHORITY missing - this might be the problem!"
    echo "  (You need to be logged in to the desktop for GUI apps to work)"
fi
echo ""

# Check if user is logged in
echo "5. Checking logged in users..."
who
echo ""

# Test X connection
echo "6. Testing X connection..."
if xdpyinfo -display :0 > /dev/null 2>&1; then
    echo "✓ Can connect to X server"
else
    echo "✗ Cannot connect to X server"
    echo "  Error: $(xdpyinfo -display :0 2>&1 | head -3)"
fi
echo ""

# Check service logs
echo "7. Recent service logs..."
journalctl -u device-panel.service -n 20 --no-pager | tail -15
echo ""

# Try manual launch with full environment
echo "8. Attempting manual launch..."
cd /opt/device-panel
export DISPLAY=:0
export XAUTHORITY=~/.Xauthority

# Kill any existing instance
pkill -f device_panel.py
sleep 1

# Try to launch
echo "Launching Device Panel..."
python3 device_panel.py 2>&1 &
DEVICE_PANEL_PID=$!
sleep 3

if ps -p $DEVICE_PANEL_PID > /dev/null; then
    echo "✓ Device Panel launched successfully (PID: $DEVICE_PANEL_PID)"
    echo "  Check your screen - it should be visible now!"
else
    echo "✗ Device Panel failed to launch"
    echo "  Check errors above"
fi
echo ""

# Fix service for future boots
echo "9. Updating service file for better GUI support..."
sudo tee /etc/systemd/system/device-panel.service > /dev/null << 'EOF'
[Unit]
Description=Device Panel GUI Application
After=graphical.target network-online.target
Wants=graphical.target

[Service]
Type=simple
User=a
Group=a
Environment="DISPLAY=:0"
Environment="XAUTHORITY=/home/a/.Xauthority"
Environment="PYTHONPATH=/opt/device-panel"
WorkingDirectory=/opt/device-panel
ExecStart=/usr/bin/python3 -u /opt/device-panel/device_panel.py
Restart=on-failure
RestartSec=5
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=graphical.target
EOF

sudo systemctl daemon-reload
echo "✓ Service updated"
echo ""

# Add to autostart (more reliable)
echo "10. Adding to desktop autostart..."
mkdir -p ~/.config/autostart
cat > ~/.config/autostart/device-panel.desktop << 'DESKTOP'
[Desktop Entry]
Type=Application
Name=Device Panel
Comment=Hardware Control and Monitoring GUI
Exec=/usr/bin/python3 /opt/device-panel/device_panel.py
Icon=application-x-executable
Terminal=false
Categories=Utility;System;
StartupNotify=true
X-GNOME-Autostart-enabled=true
DESKTOP
chmod +x ~/.config/autostart/device-panel.desktop
echo "✓ Desktop autostart configured"
echo ""

echo "=== Fix Complete ==="
echo ""
echo "The Device Panel should now be visible on your screen."
echo "If not, try logging out and logging back in, or reboot."
echo ""
echo "To manually start it anytime, run:"
echo "  cd /opt/device-panel && export DISPLAY=:0 && python3 device_panel.py &"

