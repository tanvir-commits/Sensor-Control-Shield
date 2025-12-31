#!/bin/bash
# Manual deployment script - run this after SSH'ing to Pi

echo "========================================="
echo "Smart Suggestions - Manual Deployment"
echo "========================================="
echo ""
echo "Run these commands on the Pi after SSH'ing in:"
echo ""
echo "1. Navigate to project directory:"
echo "   cd /opt/device-panel 2>/dev/null || (mkdir -p ~/DeviceOps && cd ~/DeviceOps)"
echo ""
echo "2. Clone or update repository:"
echo "   if [ -d .git ]; then"
echo "     git fetch origin"
echo "     git checkout feature/smart-suggestions"
echo "     git pull origin feature/smart-suggestions"
echo "   else"
echo "     git clone https://github.com/tanvir-commits/Sensor-Control-Shield.git ."
echo "     git checkout feature/smart-suggestions"
echo "   fi"
echo ""
echo "3. Install dependencies:"
echo "   pip3 install -r requirements.txt"
echo ""
echo "4. Launch app:"
echo "   export DISPLAY=:0"
echo "   python3 device_panel.py"
echo ""
echo "========================================="
echo "OR use this one-liner (copy-paste):"
echo "========================================="
echo ""
cat << 'ONELINER'
cd /opt/device-panel 2>/dev/null || (mkdir -p ~/DeviceOps && cd ~/DeviceOps); [ -d .git ] && (git fetch origin && git checkout feature/smart-suggestions && git pull origin feature/smart-suggestions) || (git clone https://github.com/tanvir-commits/Sensor-Control-Shield.git . && git checkout feature/smart-suggestions); pip3 install -r requirements.txt; export DISPLAY=:0; python3 device_panel.py
ONELINER

