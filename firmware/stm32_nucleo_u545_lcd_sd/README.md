# STM32 NUCLEO-U545RE-Q LCD & SD Card Demo Project

STM32 project for NUCLEO-U545RE-Q board with UART communication, preparing for LCD and SD card integration.

## Current Status

✅ **UART Communication Working**
- LPUART1 configured on PC0 (TX) and PC1 (RX) for external USB-UART adapter
- QA Agent integrated for command processing
- Responds to `TASK 1` (LED blink) and `TASK 2` (MCU status) commands
- HEARTBEAT messages sent every 2 seconds for TX verification

## Quick Start

### 1. Build the Project

```bash
cd firmware/stm32_nucleo_u545_lcd_sd
make clean
make
```

This will create:
- `build/stm32_nucleo_u545_lcd_sd.elf` - ELF file
- `build/stm32_nucleo_u545_lcd_sd.hex` - Intel HEX file
- `build/stm32_nucleo_u545_lcd_sd.bin` - Binary file

### 2. Flash to Board

**Option A: Using OpenOCD**
```bash
make flash
```

**Option B: Using STM32CubeProgrammer**
```bash
make flash-stm32prog
```

### 3. Test UART Communication

Connect the NUCLEO board via USB-UART adapter to PC0/PC1. The serial port should appear as `/dev/ttyUSB0` (or similar).

Test with DeviceOps:
- Send `TASK 1` command - LED should blink 3 times
- Send `TASK 2` command - Should return MCU status (SysClk, HCLK, VScale)

Or test with Python:
```python
from hardware.uart_manager import UARTManager

uart = UARTManager()
uart.open('/dev/ttyUSB0', 115200)
success, response = uart.send_command('TASK 1')
print(f"Response: {response}")  # Should print "OK LED blinked 3 times"
```

## Project Structure

```
stm32_nucleo_u545_lcd_sd/
├── Makefile              # Build configuration
├── README.md             # This file
├── STM32U545RETX_FLASH.ld # Linker script
├── inc/                  # Header files
│   ├── main.h
│   ├── qa_agent.h        # QA Agent API
│   ├── stm32u5xx_hal_conf.h
│   └── stm32u5xx_it.h
├── src/                  # Source files
│   ├── main.c            # Main application
│   ├── qa_agent.c        # QA Agent implementation
│   ├── system_stm32u5xx.c
│   ├── stm32u5xx_it.c    # Interrupt handlers
│   ├── stm32u5xx_hal_msp.c
│   └── startup_stm32u545xx.s
├── Drivers/              # STM32 HAL library (symlink to ../stm32_nucleo_u545/Drivers)
└── build/                # Build output directory
```

## Configuration

### UART Configuration

The project is configured for **LPUART1** on pins:
- **PC1** = TX (CN7 pin 36)
- **PC0** = RX (CN7 pin 38)

This connects to an external USB-UART adapter (not the ST-LINK virtual COM port).

Baud rate: 115200

## Current Features

✅ **UART Communication** - LPUART1 on PC0/PC1
✅ **SD Card Support** - SPI2 interface on PB13/14/15, CS on PB12
  - TASK 6: Initialize SD card
  - TASK 7: Read block 0
  - TASK 8: Write test pattern to block 0

## Future Plans

- [ ] Add LCD display support (ST7789 controller via SPI)
- [ ] Integrate LCD tasks into QA Agent
- [ ] Add FatFS file system for SD card
- [ ] Add example applications using LCD and SD card

## Troubleshooting

### Build Errors: "No such file or directory"

The `Drivers` directory is a symlink to the base project. Make sure `../stm32_nucleo_u545/Drivers` exists.

### Flash Errors: "Cannot find ST-LINK"

1. Check USB connection (ST-LINK port on NUCLEO board)
2. Install ST-LINK drivers if needed
3. Check permissions: `sudo usermod -a -G dialout $USER` (Linux)

### UART Not Working

1. Check baud rate (115200)
2. Verify UART pins (PC0/PC1 for LPUART1)
3. Check if serial port appears: `ls /dev/ttyUSB*`
4. Test with serial terminal: `screen /dev/ttyUSB0 115200`
5. Verify wiring: PC0 (RX) to adapter TX, PC1 (TX) to adapter RX

## Related Projects

- `firmware/stm32_nucleo_u545/` - Base project with UART communication
- `firmware/qa_agent.c` - QA Agent implementation (shared)

