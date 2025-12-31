# Quick VNC Setup for Raspberry Pi

## Quick Setup (Recommended: x11vnc)

SSH to the Pi and run:

```bash
ssh a@192.168.101
# Enter password: 1

# Install x11vnc (shares existing display)
sudo apt-get update
sudo apt-get install -y x11vnc

# Set VNC password
x11vnc -storepasswd
# Enter a password (remember it!)

# Start VNC server
x11vnc -display :0 -auth guess -forever -loop -noxdamage -repeat -rfbauth ~/.vnc/passwd -rfbport 5900 -shared &

# Make it start on boot
sudo nano /etc/systemd/system/x11vnc.service
```

Paste this into the service file:

```ini
[Unit]
Description=Start x11vnc at startup
After=multi-user.target

[Service]
Type=simple
User=a
ExecStart=/usr/bin/x11vnc -display :0 -auth guess -forever -loop -noxdamage -repeat -rfbauth /home/a/.vnc/passwd -rfbport 5900 -shared
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

Then enable it:

```bash
sudo systemctl daemon-reload
sudo systemctl enable x11vnc.service
sudo systemctl start x11vnc.service
```

## Connect from Your PC

### Option 1: Remmina (Recommended for Linux)

```bash
sudo apt-get install remmina remmina-plugin-vnc
```

1. Open Remmina
2. New connection
3. Protocol: VNC
4. Server: `192.168.101:5900`
5. Username: (leave blank)
6. Password: (the password you set)
7. Connect

### Option 2: TigerVNC Viewer

```bash
sudo apt-get install tigervnc-viewer
vncviewer 192.168.101:5900
```

### Option 3: RealVNC Viewer

Download from: https://www.realvnc.com/download/viewer/

Connect to: `192.168.101:5900`

## Copy/Paste

Once connected via VNC:
- **Copy on PC**: Select text, Ctrl+C
- **Paste on Pi**: Click in Pi window, Ctrl+V (or right-click > Paste)
- **Copy on Pi**: Select text, Ctrl+C  
- **Paste on PC**: Click in PC window, Ctrl+V

## Alternative: RealVNC (if pre-installed)

If RealVNC is already on the Pi:

```bash
sudo raspi-config
# Interface Options > VNC > Enable
```

Then connect with RealVNC Viewer to: `192.168.101`

## Troubleshooting

If VNC doesn't work:
1. Check firewall: `sudo ufw allow 5900`
2. Check if service is running: `sudo systemctl status x11vnc`
3. Check if display is active: `echo $DISPLAY` (should show :0)
4. Try connecting: `vncviewer 192.168.101:5900`

