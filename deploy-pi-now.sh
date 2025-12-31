#!/bin/bash
# Quick deploy script with password handling

PI_HOST="192.168.101"
PI_USER="a"
PI_PASS="1"
PI_DIR="/opt/device-panel"
BRANCH="feature/smart-suggestions"

echo "Deploying to $PI_USER@$PI_HOST..."

# Use sshpass to handle password
sshpass -p "$PI_PASS" ssh -o StrictHostKeyChecking=no $PI_USER@$PI_HOST << 'ENDSSH'
cd /opt/device-panel 2>/dev/null || cd ~/DeviceOps 2>/dev/null || (mkdir -p ~/DeviceOps && cd ~/DeviceOps)

if [ -d .git ]; then
    echo "Updating repository..."
    git fetch origin
    git checkout feature/smart-suggestions
    git pull origin feature/smart-suggestions
else
    echo "Cloning repository..."
    git clone https://github.com/tanvir-commits/Sensor-Control-Shield.git .
    git checkout feature/smart-suggestions
fi

echo "Installing dependencies..."
pip3 install -q -r requirements.txt 2>/dev/null || echo "Dependencies installed (or requirements.txt not found)"

echo "Deployment complete!"
ENDSSH

echo ""
echo "Now launching app..."
sshpass -p "$PI_PASS" ssh -o StrictHostKeyChecking=no $PI_USER@$PI_HOST "cd /opt/device-panel 2>/dev/null || cd ~/DeviceOps; python3 device_panel.py"

