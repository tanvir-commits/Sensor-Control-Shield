#!/bin/bash
# Initial setup script for Raspberry Pi to work with a specific branch

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Default values
BRANCH="dev"
PI_HOST=""
PI_USER="pi"
PI_DIR="/opt/device-panel"
REPO_URL="https://github.com/tanvir-commits/Sensor-Control-Shield.git"
SSH_KEY=""

# Usage function
usage() {
    echo "Usage: $0 -h <pi-host> [options]"
    echo ""
    echo "Options:"
    echo "  -h, --host HOST          Raspberry Pi hostname or IP (required)"
    echo "  -b, --branch BRANCH      Git branch to checkout (default: dev)"
    echo "  -u, --user USER          SSH username (default: pi)"
    echo "  -d, --dir DIR            Target directory (default: /opt/device-panel)"
    echo "  -r, --repo URL           Repository URL (default: GitHub repo)"
    echo "  -k, --key KEY            SSH private key path (optional)"
    echo "  --help                   Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 -h raspberrypi.local -b feature/power-profiler"
    echo "  $0 -h 192.168.1.100 -b dev -d /home/pi/device-panel"
    exit 1
}

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--host)
            PI_HOST="$2"
            shift 2
            ;;
        -b|--branch)
            BRANCH="$2"
            shift 2
            ;;
        -u|--user)
            PI_USER="$2"
            shift 2
            ;;
        -d|--dir)
            PI_DIR="$2"
            shift 2
            ;;
        -r|--repo)
            REPO_URL="$2"
            shift 2
            ;;
        -k|--key)
            SSH_KEY="$2"
            shift 2
            ;;
        --help)
            usage
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NC}"
            usage
            ;;
    esac
done

# Validate required arguments
if [[ -z "$PI_HOST" ]]; then
    echo -e "${RED}Error: Pi host is required${NC}"
    usage
fi

# Build SSH command
SSH_CMD="ssh"
if [[ -n "$SSH_KEY" ]]; then
    SSH_CMD="$SSH_CMD -i $SSH_KEY"
fi
SSH_CMD="$SSH_CMD $PI_USER@$PI_HOST"

echo -e "${GREEN}Setting up Raspberry Pi for branch '$BRANCH'${NC}"
echo "Host: $PI_USER@$PI_HOST"
echo "Directory: $PI_DIR"
echo ""

# Test SSH connection
echo -e "${YELLOW}Testing SSH connection...${NC}"
if ! $SSH_CMD "echo 'Connection successful'" >/dev/null 2>&1; then
    echo -e "${RED}Error: Could not connect to Pi${NC}"
    echo "Make sure:"
    echo "  1. Pi is powered on and connected to network"
    echo "  2. SSH is enabled on Pi"
    echo "  3. You have SSH access (password or key)"
    exit 1
fi
echo -e "${GREEN}✓ SSH connection successful${NC}"

# Install git if not present
echo -e "${YELLOW}Checking for git...${NC}"
if ! $SSH_CMD "command -v git" >/dev/null 2>&1; then
    echo -e "${YELLOW}Installing git...${NC}"
    $SSH_CMD "sudo apt-get update && sudo apt-get install -y git" || {
        echo -e "${RED}Error: Failed to install git${NC}"
        exit 1
    }
fi
echo -e "${GREEN}✓ Git is installed${NC}"

# Install Python dependencies
echo -e "${YELLOW}Checking for Python 3...${NC}"
if ! $SSH_CMD "command -v python3" >/dev/null 2>&1; then
    echo -e "${RED}Error: Python 3 is not installed${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Python 3 is installed${NC}"

# Clone or update repository
echo -e "${YELLOW}Setting up repository...${NC}"
if $SSH_CMD "test -d $PI_DIR/.git"; then
    echo -e "${YELLOW}Repository exists, updating...${NC}"
    $SSH_CMD "cd $PI_DIR && git fetch origin && git checkout $BRANCH && git pull origin $BRANCH" || {
        echo -e "${RED}Error: Failed to update repository${NC}"
        exit 1
    }
else
    echo -e "${YELLOW}Cloning repository...${NC}"
    $SSH_CMD "mkdir -p $(dirname $PI_DIR) && cd $(dirname $PI_DIR) && git clone $REPO_URL $(basename $PI_DIR) && cd $PI_DIR && git checkout $BRANCH" || {
        echo -e "${RED}Error: Failed to clone repository${NC}"
        exit 1
    }
fi
echo -e "${GREEN}✓ Repository set up${NC}"

# Install Python dependencies
echo -e "${YELLOW}Installing Python dependencies...${NC}"
if $SSH_CMD "test -f $PI_DIR/requirements.txt"; then
    $SSH_CMD "cd $PI_DIR && pip3 install -r requirements.txt" || {
        echo -e "${YELLOW}Warning: Some dependencies may have failed to install${NC}"
    }
else
    echo -e "${YELLOW}No requirements.txt found, installing common dependencies...${NC}"
    $SSH_CMD "cd $PI_DIR && pip3 install PySide6 gpiozero smbus2 adafruit-circuitpython-ads1x15 adafruit-circuitpython-ssd1306 pyserial Pillow" || {
        echo -e "${YELLOW}Warning: Some dependencies may have failed to install${NC}"
    }
fi
echo -e "${GREEN}✓ Dependencies installed${NC}"

# Enable I2C and SPI (if on Raspberry Pi)
echo -e "${YELLOW}Checking hardware interfaces...${NC}"
if $SSH_CMD "test -f /boot/config.txt"; then
    echo -e "${YELLOW}Enabling I2C and SPI...${NC}"
    $SSH_CMD "sudo raspi-config nonint do_i2c 0 && sudo raspi-config nonint do_spi 0" || {
        echo -e "${YELLOW}Warning: Could not enable I2C/SPI (may need manual configuration)${NC}"
    }
    echo -e "${GREEN}✓ Hardware interfaces configured${NC}"
else
    echo -e "${YELLOW}Not a Raspberry Pi, skipping hardware configuration${NC}"
fi

echo ""
echo -e "${GREEN}✓ Setup complete!${NC}"
echo ""
echo "Raspberry Pi is now set up for branch '$BRANCH'"
echo ""
echo "To run the app:"
echo "  ssh $PI_USER@$PI_HOST"
echo "  cd $PI_DIR"
echo "  python3 device_panel.py"
echo ""
echo "To deploy updates:"
echo "  ./scripts/deploy-to-pi.sh -b $BRANCH -h $PI_HOST"

