#!/bin/bash
# Complete setup and deployment script for RPi

PI_HOST="192.168.101"
PI_USER="a"
PI_PASS="1"
BRANCH="feature/smart-suggestions"

echo "========================================="
echo "Smart Suggestions - RPi Deployment"
echo "========================================="
echo ""

# Step 1: Setup SSH key (one-time)
echo "Step 1: Setting up SSH key..."
PUBKEY=$(cat ~/.ssh/id_ed25519.pub 2>/dev/null || cat ~/.ssh/id_rsa.pub 2>/dev/null)

if [ -z "$PUBKEY" ]; then
    echo "Generating SSH key..."
    ssh-keygen -t ed25519 -f ~/.ssh/id_ed25519 -N "" -C "device-panel-deploy" -q
    PUBKEY=$(cat ~/.ssh/id_ed25519.pub)
fi

echo "Installing SSH key on Pi..."
echo "You will be prompted for password: $PI_PASS"
if [ -f ~/.ssh/id_ed25519.pub ]; then
    ssh-copy-id -i ~/.ssh/id_ed25519.pub $PI_USER@$PI_HOST 2>/dev/null || {
        echo ""
        echo "Manual SSH key setup required:"
        echo "1. SSH to Pi: ssh $PI_USER@$PI_HOST"
        echo "2. Run: mkdir -p ~/.ssh && chmod 700 ~/.ssh"
        echo "3. Add this key to ~/.ssh/authorized_keys:"
        echo "$PUBKEY"
        echo "4. Run: chmod 600 ~/.ssh/authorized_keys"
        echo ""
        read -p "Press Enter after SSH key is set up..."
    }
elif [ -f ~/.ssh/id_rsa.pub ]; then
    ssh-copy-id -i ~/.ssh/id_rsa.pub $PI_USER@$PI_HOST 2>/dev/null || {
        echo ""
        echo "Manual SSH key setup required:"
        echo "1. SSH to Pi: ssh $PI_USER@$PI_HOST"
        echo "2. Run: mkdir -p ~/.ssh && chmod 700 ~/.ssh"
        echo "3. Add this key to ~/.ssh/authorized_keys:"
        echo "$PUBKEY"
        echo "4. Run: chmod 600 ~/.ssh/authorized_keys"
        echo ""
        read -p "Press Enter after SSH key is set up..."
    }
fi

# Step 2: Test passwordless SSH
echo ""
echo "Step 2: Testing passwordless SSH..."
if ssh -o ConnectTimeout=5 -o StrictHostKeyChecking=no $PI_USER@$PI_HOST "echo 'SSH works!'" 2>/dev/null; then
    echo "✓ Passwordless SSH is working!"
else
    echo "✗ Passwordless SSH failed. Please set up SSH keys manually."
    exit 1
fi

# Step 3: Deploy code
echo ""
echo "Step 3: Deploying code to Pi..."
./scripts/deploy-to-pi.sh -b $BRANCH -h $PI_HOST -u $PI_USER || {
    echo "Deploy script failed, trying manual deployment..."
    ssh $PI_USER@$PI_HOST "cd /opt/device-panel 2>/dev/null || (mkdir -p ~/DeviceOps && cd ~/DeviceOps); [ -d .git ] && (git fetch origin && git checkout $BRANCH && git pull origin $BRANCH) || (git clone https://github.com/tanvir-commits/Sensor-Control-Shield.git . && git checkout $BRANCH)"
}

# Step 4: Install dependencies
echo ""
echo "Step 4: Installing dependencies..."
ssh $PI_USER@$PI_HOST "cd /opt/device-panel 2>/dev/null || cd ~/DeviceOps; pip3 install -q -r requirements.txt 2>/dev/null; echo 'Dependencies installed'"

# Step 5: Launch app
echo ""
echo "Step 5: Launching app..."
echo "The app will start on the Pi's display..."
ssh $PI_USER@$PI_HOST "cd /opt/device-panel 2>/dev/null || cd ~/DeviceOps; export DISPLAY=:0; nohup python3 device_panel.py > /tmp/device_panel.log 2>&1 & echo 'App launched! PID:' \$!"

echo ""
echo "========================================="
echo "Deployment complete!"
echo "========================================="
echo ""
echo "To check app status:"
echo "  ssh $PI_USER@$PI_HOST 'ps aux | grep device_panel'"
echo ""
echo "To view app logs:"
echo "  ssh $PI_USER@$PI_HOST 'tail -f /tmp/device_panel.log'"
echo ""

