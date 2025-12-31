#!/bin/bash
# Deploy a specific branch to a Raspberry Pi

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Default values
BRANCH=""
PI_HOST=""
PI_USER="pi"
PI_DIR="/opt/device-panel"
SSH_KEY=""

# Usage function
usage() {
    echo "Usage: $0 -b <branch> -h <pi-host> [options]"
    echo ""
    echo "Options:"
    echo "  -b, --branch BRANCH      Git branch to deploy (required)"
    echo "  -h, --host HOST          Raspberry Pi hostname or IP (required)"
    echo "  -u, --user USER          SSH username (default: pi)"
    echo "  -d, --dir DIR            Target directory on Pi (default: /opt/device-panel)"
    echo "  -k, --key KEY            SSH private key path (optional)"
    echo "  -r, --restart            Restart device-panel service after deployment"
    echo "  --help                   Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 -b feature/power-profiler -h raspberrypi.local"
    echo "  $0 -b dev -h 192.168.1.100 -u pi -d /home/pi/device-panel"
    exit 1
}

# Parse arguments
RESTART_SERVICE=false
while [[ $# -gt 0 ]]; do
    case $1 in
        -b|--branch)
            BRANCH="$2"
            shift 2
            ;;
        -h|--host)
            PI_HOST="$2"
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
        -k|--key)
            SSH_KEY="$2"
            shift 2
            ;;
        -r|--restart)
            RESTART_SERVICE=true
            shift
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
if [[ -z "$BRANCH" ]]; then
    echo -e "${RED}Error: Branch is required${NC}"
    usage
fi

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

# Build SCP command
SCP_CMD="scp"
if [[ -n "$SSH_KEY" ]]; then
    SCP_CMD="$SCP_CMD -i $SSH_KEY"
fi

echo -e "${GREEN}Deploying branch '$BRANCH' to $PI_USER@$PI_HOST${NC}"
echo ""

# Check if branch exists locally
if ! git rev-parse --verify "$BRANCH" >/dev/null 2>&1; then
    echo -e "${RED}Error: Branch '$BRANCH' does not exist locally${NC}"
    exit 1
fi

# Push branch to remote (if not already pushed)
echo -e "${YELLOW}Pushing branch to remote...${NC}"
git push origin "$BRANCH" || echo -e "${YELLOW}Branch already pushed or no remote${NC}"

# Create directory on Pi if it doesn't exist
echo -e "${YELLOW}Ensuring directory exists on Pi...${NC}"
$SSH_CMD "mkdir -p $PI_DIR" || {
    echo -e "${RED}Error: Could not create directory on Pi${NC}"
    exit 1
}

# Check if git repo exists on Pi
echo -e "${YELLOW}Checking git repository on Pi...${NC}"
if $SSH_CMD "test -d $PI_DIR/.git"; then
    echo -e "${GREEN}Git repository exists, updating...${NC}"
    # Update existing repo
    $SSH_CMD "cd $PI_DIR && git fetch origin && git checkout $BRANCH && git pull origin $BRANCH" || {
        echo -e "${RED}Error: Failed to update repository${NC}"
        exit 1
    }
else
    echo -e "${YELLOW}No git repository found, cloning...${NC}"
    # Clone repository
    REPO_URL=$(git remote get-url origin 2>/dev/null || echo "https://github.com/tanvir-commits/Sensor-Control-Shield.git")
    $SSH_CMD "cd $(dirname $PI_DIR) && git clone $REPO_URL $(basename $PI_DIR) && cd $PI_DIR && git checkout $BRANCH" || {
        echo -e "${RED}Error: Failed to clone repository${NC}"
        exit 1
    }
fi

# Install dependencies
echo -e "${YELLOW}Installing dependencies...${NC}"
$SSH_CMD "cd $PI_DIR && pip3 install -r requirements.txt" || {
    echo -e "${YELLOW}Warning: Could not install dependencies (requirements.txt may not exist)${NC}"
}

# Restart service if requested
if [[ "$RESTART_SERVICE" == true ]]; then
    echo -e "${YELLOW}Restarting device-panel service...${NC}"
    $SSH_CMD "sudo systemctl restart device-panel.service" || {
        echo -e "${YELLOW}Warning: Could not restart service (service may not exist)${NC}"
    }
fi

echo ""
echo -e "${GREEN}✓ Deployment complete!${NC}"
echo ""
echo "Branch '$BRANCH' is now deployed to $PI_USER@$PI_HOST:$PI_DIR"
echo ""
echo "To run the app on the Pi:"
echo "  ssh $PI_USER@$PI_HOST"
echo "  cd $PI_DIR"
echo "  python3 device_panel.py"

