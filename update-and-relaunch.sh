#!/bin/bash
# Script to update Device Panel app and relaunch on Raspberry Pi
# Run this ON THE PI

set -e

echo "=== Updating Device Panel ==="

# Determine where the app is installed
if [ -d "/opt/device-panel" ]; then
    APP_DIR="/opt/device-panel"
    echo "Found app at: $APP_DIR"
elif [ -d "$HOME/DeviceOps" ]; then
    APP_DIR="$HOME/DeviceOps"
    echo "Found app at: $APP_DIR"
else
    echo "Error: Device Panel not found!"
    echo "Looking for /opt/device-panel or ~/DeviceOps"
    exit 1
fi

cd "$APP_DIR"

# Stop any running instance
echo ""
echo "Stopping existing instance..."
pkill -f device_panel.py || echo "No running instance found"

# Update from git if it's a git repo
if [ -d ".git" ]; then
    echo ""
    echo "Pulling latest code..."
    git pull || echo "Warning: git pull failed (maybe not a git repo?)"
else
    echo ""
    echo "Not a git repo, skipping pull"
fi

# Make sure we have the latest dependencies
echo ""
echo "Checking dependencies..."
if [ -f "requirements.txt" ]; then
    python3 -m pip install -q -r requirements.txt || echo "Warning: pip install had issues"
fi

# Wait a moment for processes to stop
sleep 1

# Launch the app
echo ""
echo "Launching Device Panel..."
export DISPLAY=:0
cd "$APP_DIR"
python3 device_panel.py &

# Wait a moment and check if it launched
sleep 2
if pgrep -f device_panel.py > /dev/null; then
    echo "✓ Device Panel launched successfully!"
    echo "PID: $(pgrep -f device_panel.py)"
else
    echo "✗ Failed to launch - check errors above"
    exit 1
fi

