# SSH Update Instructions

Since SSH requires password authentication, here are the commands to run on the Pi:

## Option 1: Copy and Run Script on Pi

1. Copy the `update-and-relaunch.sh` script to the Pi:
   ```bash
   scp update-and-relaunch.sh a@raspberrypi.local:~/
   ```

2. SSH to the Pi and run it:
   ```bash
   ssh a@raspberrypi.local
   chmod +x ~/update-and-relaunch.sh
   ~/update-and-relaunch.sh
   ```

## Option 2: Manual Commands on Pi

SSH to the Pi and run these commands:

```bash
# Navigate to app directory
cd /opt/device-panel  # or ~/DeviceOps if installed there

# Stop existing instance
pkill -f device_panel.py

# Update code (if git repo)
git pull

# Install/update dependencies
pip3 install -r requirements.txt

# Launch app
export DISPLAY=:0
python3 device_panel.py &
```

## Option 3: If App is Pre-installed (Custom Image)

If you're using the custom image, the app is at `/opt/device-panel`:

```bash
ssh a@raspberrypi.local

# On the Pi:
cd /opt/device-panel
pkill -f device_panel.py
git pull  # if it's a git repo, or copy files manually
export DISPLAY=:0
python3 device_panel.py &
```

## Check if App is Running

```bash
ps aux | grep device_panel
```

## View Logs/Errors

If the app doesn't launch, check for errors:
```bash
cd /opt/device-panel
export DISPLAY=:0
python3 device_panel.py
# (Run in foreground to see errors)
```

