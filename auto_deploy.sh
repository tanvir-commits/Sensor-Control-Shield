#!/bin/bash
# Fully automated deployment - handles SSH key setup and deployment

PI_HOST="192.168.101"
PI_USER="a"  
PI_PASS="1"
BRANCH="feature/smart-suggestions"

PUBKEY=$(cat ~/.ssh/id_ed25519.pub 2>/dev/null || cat ~/.ssh/id_rsa.pub 2>/dev/null)

echo "=== Automated Deployment to RPi ==="
echo ""

# Try to install SSH key using expect
echo "Setting up SSH key..."
expect << EOF
set timeout 30
spawn ssh-copy-id -i ~/.ssh/id_ed25519.pub $PI_USER@$PI_HOST
expect {
    "password:" { send "$PI_PASS\r"; exp_continue }
    "Password:" { send "$PI_PASS\r"; exp_continue }
    "Number of key(s) added" { puts "Key installed!"; exit 0 }
    "already installed" { puts "Key already installed!"; exit 0 }
    eof { exit 0 }
    timeout { 
        puts "Timeout - trying manual key install..."
        exit 1
    }
}
EOF

# If expect failed, try manual key install via ssh
if [ $? -ne 0 ]; then
    echo "Installing key via SSH command..."
    expect << EOF
set timeout 20
spawn ssh -o StrictHostKeyChecking=no $PI_USER@$PI_HOST "mkdir -p ~/.ssh && echo '$PUBKEY' >> ~/.ssh/authorized_keys && chmod 700 ~/.ssh && chmod 600 ~/.ssh/authorized_keys && echo 'KEY_INSTALLED'"
expect {
    "password:" { send "$PI_PASS\r"; exp_continue }
    "Password:" { send "$PI_PASS\r"; exp_continue }
    "KEY_INSTALLED" { puts "Key installed!"; exit 0 }
    timeout { exit 1 }
    eof
}
EOF
fi

sleep 2

# Test passwordless SSH
if ssh -o ConnectTimeout=5 -o StrictHostKeyChecking=no $PI_USER@$PI_HOST "echo 'SSH_OK'" 2>/dev/null; then
    echo "✓ Passwordless SSH working!"
    
    # Deploy
    echo "Deploying code..."
    ssh $PI_USER@$PI_HOST "cd /opt/device-panel 2>/dev/null || (mkdir -p ~/DeviceOps && cd ~/DeviceOps); [ -d .git ] && (git fetch origin && git checkout $BRANCH && git pull origin $BRANCH) || (git clone https://github.com/tanvir-commits/Sensor-Control-Shield.git . && git checkout $BRANCH)"
    
    echo "Installing dependencies..."
    ssh $PI_USER@$PI_HOST "cd /opt/device-panel 2>/dev/null || cd ~/DeviceOps; pip3 install -q -r requirements.txt 2>/dev/null"
    
    echo "Launching app..."
    ssh $PI_USER@$PI_HOST "cd /opt/device-panel 2>/dev/null || cd ~/DeviceOps; export DISPLAY=:0; nohup python3 device_panel.py > /tmp/device_panel.log 2>&1 & echo 'App launched! PID:' \$!"
    
    echo ""
    echo "=== Deployment Complete ==="
    echo "App should be running on the Pi's display"
else
    echo "✗ SSH key setup failed"
    echo "Please run manually: ssh $PI_USER@$PI_HOST"
    echo "Then add this key to ~/.ssh/authorized_keys:"
    echo "$PUBKEY"
    exit 1
fi

