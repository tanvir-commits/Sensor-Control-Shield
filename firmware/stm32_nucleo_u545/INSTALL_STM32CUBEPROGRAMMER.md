# Installing STM32CubeProgrammer

STM32CubeProgrammer is the official ST tool for flashing STM32 microcontrollers.

## Download

1. Visit: https://www.st.com/en/development-tools/stm32cubeprog.html
2. Click "Get Software" (requires free ST account registration)
3. Download the Linux version

## Installation

### Option 1: Extract and Use Directly

```bash
# Extract the downloaded archive
tar -xzf en.stm32cubeprog-lin-v2.x.x.tar.gz

# Add to PATH (add to ~/.bashrc for permanent)
export PATH=$PATH:/path/to/STM32CubeProgrammer/bin

# Test
STM32_Programmer_CLI --version
```

### Option 2: Install System-Wide

```bash
# Extract
tar -xzf en.stm32cubeprog-lin-v2.x.x.tar.gz

# Copy to /opt (optional)
sudo cp -r STM32CubeProgrammer /opt/

# Create symlink (optional)
sudo ln -s /opt/STM32CubeProgrammer/bin/STM32_Programmer_CLI /usr/local/bin/

# Test
STM32_Programmer_CLI --version
```

## Usage

### Flash binary file:
```bash
STM32_Programmer_CLI -c port=SWD -w build/stm32_nucleo_u545.bin 0x08000000 -v -rst
```

### Flash hex file:
```bash
STM32_Programmer_CLI -c port=SWD -w build/stm32_nucleo_u545.hex 0x08000000 -v -rst
```

### List connected ST-LINK:
```bash
STM32_Programmer_CLI -l
```

## Troubleshooting

### Permission denied
```bash
# Add user to dialout group (for serial port access)
sudo usermod -a -G dialout $USER
# Log out and back in
```

### ST-LINK not found
- Check USB connection (use ST-LINK port, not USB user port)
- Install ST-LINK drivers if needed
- Try: `STM32_Programmer_CLI -l` to list devices

## Alternative: Use OpenOCD

If you don't want to install STM32CubeProgrammer, you can use OpenOCD (already installed):

```bash
make flash  # Uses OpenOCD
```


