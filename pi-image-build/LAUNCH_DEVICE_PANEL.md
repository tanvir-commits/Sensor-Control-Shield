# How to Launch Device Panel on Raspberry Pi

## Method 1: From Terminal (Recommended for Testing)

Open a terminal on the Pi and run:

```bash
cd /opt/device-panel
export DISPLAY=:0
python3 device_panel.py
```

The GUI window should appear on your screen.

## Method 2: Create a Desktop Shortcut

1. Right-click on the desktop
2. Select "Create New" → "Blank File"
3. Name it `device-panel.desktop`
4. Edit it and add:

```ini
[Desktop Entry]
Type=Application
Name=Device Panel
Comment=Hardware Control and Monitoring GUI
Exec=/usr/bin/python3 /opt/device-panel/device_panel.py
Icon=application-x-executable
Terminal=false
Categories=Utility;System;
```

5. Right-click the file → Properties → Permissions → Check "Allow executing file as program"
6. Double-click to launch!

## Method 3: Create a Launch Script

Create a file `~/launch-device-panel.sh`:

```bash
#!/bin/bash
cd /opt/device-panel
export DISPLAY=:0
python3 device_panel.py &
```

Make it executable:
```bash
chmod +x ~/launch-device-panel.sh
```

Then run:
```bash
~/launch-device-panel.sh
```

## Method 4: Auto-Start on Login

To make it start automatically when you log in:

```bash
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
```

Then log out and log back in - Device Panel will start automatically.

## Method 5: Use Systemd Service (Already Configured)

The service is already set up. To start it:

```bash
sudo systemctl start device-panel.service
```

To check status:
```bash
systemctl status device-panel.service
```

## Troubleshooting

### If GUI doesn't appear:

1. **Check if it's running:**
   ```bash
   ps aux | grep device_panel
   ```

2. **Check for errors:**
   ```bash
   cd /opt/device-panel
   export DISPLAY=:0
   python3 device_panel.py
   ```
   (This will show errors in the terminal)

3. **Make sure you're logged into the desktop** (not just SSH)

4. **Check X server:**
   ```bash
   pgrep -f Xorg
   ```
   Should show a process if X is running

### If you see I2C errors:

That's normal if hardware isn't connected - it will use mock data and the GUI will still work.

## Quick Launch Command

The simplest way - just run this in a terminal:

```bash
cd /opt/device-panel && export DISPLAY=:0 && python3 device_panel.py &
```

The `&` runs it in the background so you can keep using the terminal.

