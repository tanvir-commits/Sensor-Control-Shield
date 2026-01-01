#!/bin/bash
# Take a screenshot of the VNC display and download it

PI_HOST="a@192.168.101"
DISPLAY=":1"
OUTPUT="/tmp/vnc_screenshot_$(date +%Y%m%d_%H%M%S).png"

echo "Taking screenshot of VNC display $DISPLAY..."
ssh $PI_HOST "export DISPLAY=$DISPLAY && import -window root /tmp/vnc_screenshot.png 2>&1"

if [ $? -eq 0 ]; then
    echo "Downloading screenshot..."
    scp $PI_HOST:/tmp/vnc_screenshot.png "$OUTPUT" 2>&1
    if [ $? -eq 0 ]; then
        echo "✓ Screenshot saved to: $OUTPUT"
        echo "Opening screenshot..."
        xdg-open "$OUTPUT" 2>/dev/null || echo "Screenshot ready at: $OUTPUT"
    else
        echo "✗ Failed to download screenshot"
    fi
else
    echo "✗ Failed to take screenshot"
fi


