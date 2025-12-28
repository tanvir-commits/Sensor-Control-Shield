#!/bin/bash
# Script to fix Device Panel autostart on Raspberry Pi
# Run this ON THE PI after first boot

echo "=== Fixing Device Panel Autostart ==="
echo ""

# Method 1: Update systemd service
echo "1. Updating systemd service..."
sudo cp /opt/device-panel/pi-image-build/config/device-panel.service /etc/systemd/system/ 2>/dev/null || \
sudo cp /home/pi/device-panel/pi-image-build/config/device-panel.service /etc/systemd/system/ 2>/dev/null || \
echo "Service file not found, creating..."

sudo tee /etc/systemd/system/device-panel.service > /dev/null << 'EOF'
[Unit]
Description=Device Panel GUI Application
After=graphical.target network-online.target
Wants=graphical.target

[Service]
Type=simple
User=pi
Group=pi
Environment="DISPLAY=:0"
Environment="XAUTHORITY=/home/pi/.Xauthority"
WorkingDirectory=/opt/device-panel
ExecStart=/usr/bin/python3 /opt/device-panel/device_panel.py
Restart=on-failure
RestartSec=5
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=graphical.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable device-panel.service
echo "✓ Service updated and enabled"
echo ""

# Method 2: Also add to autostart (more reliable for GUI apps)
echo "2. Adding to desktop autostart..."
mkdir -p /home/pi/.config/autostart
cat > /home/pi/.config/autostart/device-panel.desktop << 'DESKTOP'
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
chmod +x /home/pi/.config/autostart/device-panel.desktop
echo "✓ Desktop autostart configured"
echo ""

# Method 3: Test manual launch
echo "3. Testing manual launch..."
cd /opt/device-panel
export DISPLAY=:0
python3 device_panel.py &
sleep 2
if pgrep -f device_panel.py > /dev/null; then
    echo "✓ Manual launch successful!"
    pkill -f device_panel.py
else
    echo "✗ Manual launch failed - check errors above"
fi
echo ""

echo "=== Fix Complete ==="
echo ""
echo "The app should now start automatically when you log in."
echo "To test immediately, log out and log back in, or reboot."

