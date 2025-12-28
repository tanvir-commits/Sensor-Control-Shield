#!/bin/bash
# Troubleshooting script for Device Panel on Raspberry Pi
# Run this on the Pi itself

echo "=== Device Panel Troubleshooting ==="
echo ""

echo "1. Checking if Device Panel is installed..."
if [ -f /opt/device-panel/device_panel.py ]; then
    echo "✓ Device Panel found at /opt/device-panel/"
    ls -la /opt/device-panel/device_panel.py
else
    echo "✗ Device Panel NOT found at /opt/device-panel/"
fi
echo ""

echo "2. Checking systemd service status..."
systemctl status device-panel.service --no-pager -l
echo ""

echo "3. Checking if service is enabled..."
systemctl is-enabled device-panel.service
echo ""

echo "4. Recent service logs..."
journalctl -u device-panel.service -n 30 --no-pager
echo ""

echo "5. Checking if running in graphical mode..."
systemctl get-default
echo ""

echo "6. Checking DISPLAY environment..."
echo "DISPLAY=$DISPLAY"
echo ""

echo "7. Checking if X server is running..."
if pgrep -x Xorg > /dev/null; then
    echo "✓ X server is running"
else
    echo "✗ X server is NOT running"
fi
echo ""

echo "8. Testing manual launch (this will show errors)..."
cd /opt/device-panel
export DISPLAY=:0
python3 device_panel.py 2>&1 | head -20
echo ""

echo "9. Checking Python dependencies..."
python3 -c "import PySide6; print('PySide6:', PySide6.__version__)" 2>&1
python3 -c "import gpiozero; print('gpiozero: OK')" 2>&1
echo ""

echo "=== Troubleshooting Complete ==="

