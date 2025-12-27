#!/bin/bash
# Launch script for Device Panel GUI

cd "$(dirname "$0")"
source venv/bin/activate
python3 device_panel.py

