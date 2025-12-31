#!/bin/bash
# Quick fix for desktop icon and autostart on existing Pi installation
# Run this ON THE PI via SSH or terminal

echo "=== Fixing Device Panel Desktop Icon and Autostart ==="
echo ""

# Get current user
CURRENT_USER=${SUDO_USER:-$USER}
if [ "$CURRENT_USER" = "root" ]; then
    CURRENT_USER=$(who | awk 'NR==1{print $1}')
fi

if [ -z "$CURRENT_USER" ]; then
    CURRENT_USER="pi"
fi

USER_HOME="/home/$CURRENT_USER"
echo "Using user: $CURRENT_USER"
echo "Home directory: $USER_HOME"
echo ""

# Create desktop icon
echo "1. Creating desktop icon..."
mkdir -p "$USER_HOME/Desktop"
cat > "$USER_HOME/Desktop/device-panel.desktop" << 'DESKTOP_ICON'
[Desktop Entry]
Type=Application
Name=Device Panel
Comment=Hardware Control and Monitoring GUI
Exec=/usr/bin/python3 /opt/device-panel/device_panel.py
Icon=application-x-executable
Terminal=false
Categories=Utility;System;
StartupNotify=true
DESKTOP_ICON
chmod +x "$USER_HOME/Desktop/device-panel.desktop"
chown "$CURRENT_USER:$CURRENT_USER" "$USER_HOME/Desktop/device-panel.desktop" 2>/dev/null || true
echo "✓ Desktop icon created at $USER_HOME/Desktop/device-panel.desktop"
echo ""

# Fix autostart
echo "2. Fixing autostart..."
mkdir -p "$USER_HOME/.config/autostart"
cat > "$USER_HOME/.config/autostart/device-panel.desktop" << 'AUTOSTART'
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
AUTOSTART
chmod +x "$USER_HOME/.config/autostart/device-panel.desktop"
chown -R "$CURRENT_USER:$CURRENT_USER" "$USER_HOME/.config/autostart" 2>/dev/null || true
echo "✓ Autostart configured"
echo ""

# Update systemd service
echo "3. Updating systemd service..."
sudo tee /etc/systemd/system/device-panel.service > /dev/null << EOF
[Unit]
Description=Device Panel GUI Application
After=graphical.target network-online.target
Wants=graphical.target

[Service]
Type=simple
User=$CURRENT_USER
Group=$CURRENT_USER
Environment="DISPLAY=:0"
Environment="XAUTHORITY=$USER_HOME/.Xauthority"
Environment="PYTHONPATH=/opt/device-panel"
Environment="QT_QPA_PLATFORM=xcb"
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
sudo systemctl enable device-panel.service
echo "✓ Service updated and enabled"
echo ""

# Test launch
echo "4. Testing launch..."
export DISPLAY=:0
cd /opt/device-panel
sudo -u "$CURRENT_USER" python3 device_panel.py &
sleep 3

if pgrep -f device_panel.py > /dev/null; then
    echo "✓ Device Panel launched successfully!"
    echo "  You should see it on your screen now."
    echo ""
    echo "To stop it, run: pkill -f device_panel.py"
else
    echo "⚠ Device Panel may have launched but check for errors:"
    echo "  journalctl -u device-panel.service -n 50"
fi
echo ""

echo "=== Fix Complete ==="
echo ""
echo "Desktop icon: $USER_HOME/Desktop/device-panel.desktop"
echo "Autostart: $USER_HOME/.config/autostart/device-panel.desktop"
echo ""
echo "The desktop icon should appear on your desktop."
echo "Device Panel will auto-start on next login/reboot."
echo ""
echo "To manually start: Double-click the desktop icon or run:"
echo "  cd /opt/device-panel && export DISPLAY=:0 && python3 device_panel.py"

