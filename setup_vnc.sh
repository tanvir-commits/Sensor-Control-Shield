#!/bin/bash
# Setup VNC on Raspberry Pi for remote desktop access

PI_HOST="192.168.101"
PI_USER="a"

echo "========================================="
echo "VNC Setup for Raspberry Pi"
echo "========================================="
echo ""

echo "This script will set up VNC on the Pi so you can:"
echo "  - See the Pi's desktop remotely"
echo "  - Copy/paste between your PC and Pi"
echo ""

# Commands to run on Pi
cat << 'EOF'

Run these commands on the Pi (SSH in first: ssh a@192.168.101):

# Option 1: RealVNC (usually pre-installed on Pi OS)
sudo raspi-config
# Navigate to: Interface Options > VNC > Enable
# Or run:
sudo systemctl enable vncserver-x11-serviced.service
sudo systemctl start vncserver-x11-serviced.service

# Option 2: TightVNC (alternative)
sudo apt-get update
sudo apt-get install -y tightvncserver
vncserver :1 -geometry 1920x1080 -depth 24

# Option 3: x11vnc (shares existing display)
sudo apt-get update
sudo apt-get install -y x11vnc
x11vnc -storepasswd /home/a/.vnc/passwd
# Set a password when prompted
x11vnc -display :0 -auth guess -forever -loop -noxdamage -repeat -rfbauth /home/a/.vnc/passwd -rfbport 5900 -shared

# To start x11vnc on boot, create a service:
sudo nano /etc/systemd/system/x11vnc.service
# Add this content:
[Unit]
Description=Start x11vnc at startup
After=multi-user.target

[Service]
Type=simple
ExecStart=/usr/bin/x11vnc -display :0 -auth guess -forever -loop -noxdamage -repeat -rfbauth /home/a/.vnc/passwd -rfbport 5900 -shared
Restart=on-failure

[Install]
WantedBy=multi-user.target

# Then enable it:
sudo systemctl daemon-reload
sudo systemctl enable x11vnc.service
sudo systemctl start x11vnc.service

EOF

echo ""
echo "========================================="
echo "After setup, connect from your PC:"
echo "========================================="
echo ""
echo "Option 1: RealVNC Viewer (download from realvnc.com)"
echo "  Connect to: $PI_HOST:5900"
echo ""
echo "Option 2: Remmina (Linux)"
echo "  sudo apt-get install remmina remmina-plugin-vnc"
echo "  New connection > VNC > Server: $PI_HOST:5900"
echo ""
echo "Option 3: TigerVNC (cross-platform)"
echo "  sudo apt-get install tigervnc-viewer"
echo "  vncviewer $PI_HOST:5900"
echo ""
echo "Option 4: Built-in VNC (if using RealVNC)"
echo "  Just connect to: $PI_HOST"
echo ""

