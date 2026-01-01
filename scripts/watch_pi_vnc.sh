#!/bin/bash
# Launch Remmina VNC viewer to watch the Pi's screen

echo "========================================="
echo "VNC Connection to Raspberry Pi"
echo "========================================="
echo ""
echo "RealVNC is running on the Pi!"
echo ""
echo "Option 1: Connect with Remmina (recommended)"
echo "  remmina -c vnc://192.168.101"
echo ""
echo "Option 2: Connect with RealVNC Viewer"
echo "  Download from: https://www.realvnc.com/download/viewer/"
echo "  Connect to: 192.168.101"
echo ""
echo "Option 3: Connect with TigerVNC"
echo "  vncviewer 192.168.101"
echo ""

# Launch Remmina with VNC connection (x11vnc on port 5900)
remmina -c vnc://192.168.101:5900 &

echo ""
echo "VNC viewer launched! You should see the Pi's desktop."
echo "If prompted for password, check Pi's VNC settings."
echo ""

