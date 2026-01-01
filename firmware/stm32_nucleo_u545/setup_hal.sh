#!/bin/bash
# Setup script to download and install STM32 HAL library

set -e

echo "STM32 HAL Library Setup for NUCLEO-U545RE-Q"
echo "=============================================="
echo ""

# Check if STM32CubeU5 already exists
if [ -d "STM32CubeU5" ]; then
    echo "STM32CubeU5 directory found. Using existing files..."
else
    echo "STM32CubeU5 not found. You need to download it manually:"
    echo ""
    echo "1. Visit: https://www.st.com/en/embedded-software/stm32cubeu5.html"
    echo "2. Download STM32CubeU5 package"
    echo "3. Extract it to this directory"
    echo ""
    echo "Or use wget (if you have the direct download link):"
    echo "  wget <download_url> -O stm32cubefw_u5.zip"
    echo "  unzip stm32cubefw_u5.zip"
    echo ""
    read -p "Press Enter when STM32CubeU5 is extracted to this directory..."
fi

if [ ! -d "STM32CubeU5" ]; then
    echo "Error: STM32CubeU5 directory not found!"
    exit 1
fi

echo "Copying HAL driver files..."
mkdir -p Drivers
cp -r STM32CubeU5/Drivers/STM32U5xx_HAL_Driver Drivers/ 2>/dev/null || echo "Warning: Could not copy HAL driver"
cp -r STM32CubeU5/Drivers/CMSIS Drivers/ 2>/dev/null || echo "Warning: Could not copy CMSIS"

echo "Copying linker script and startup code..."
# Try to find linker script
if [ -f "STM32CubeU5/Projects/NUCLEO-U545RE-Q/Templates/SW4STM32/STM32U545RETx_FLASH.ld" ]; then
    cp STM32CubeU5/Projects/NUCLEO-U545RE-Q/Templates/SW4STM32/STM32U545RETx_FLASH.ld .
    echo "  ✓ Linker script copied"
else
    echo "  ⚠ Linker script not found - you'll need to add it manually"
fi

# Try to find startup code
if [ -f "STM32CubeU5/Projects/NUCLEO-U545RE-Q/Templates/SW4STM32/startup_stm32u545xx.s" ]; then
    cp STM32CubeU5/Projects/NUCLEO-U545RE-Q/Templates/SW4STM32/startup_stm32u545xx.s src/
    echo "  ✓ Startup code copied"
else
    # Try alternative location
    if [ -f "STM32CubeU5/Projects/NUCLEO-U545RE-Q/Templates/STM32CubeIDE/startup_stm32u545xx.s" ]; then
        cp STM32CubeU5/Projects/NUCLEO-U545RE-Q/Templates/STM32CubeIDE/startup_stm32u545xx.s src/
        echo "  ✓ Startup code copied (from CubeIDE template)"
    else
        echo "  ⚠ Startup code not found - you'll need to add it manually"
    fi
fi

echo ""
echo "Setup complete!"
echo ""
echo "Next steps:"
echo "1. Verify Drivers/STM32U5xx_HAL_Driver exists"
echo "2. Verify Drivers/CMSIS exists"
echo "3. Verify linker script exists: STM32U545RETx_FLASH.ld"
echo "4. Verify startup code exists: src/startup_stm32u545xx.s"
echo "5. Run: make"
echo ""


