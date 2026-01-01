# Quick Start Guide

Get your NUCLEO-U545RE-Q board running with QA Agent in 5 minutes!

## Prerequisites

✅ ARM GCC toolchain installed (`arm-none-eabi-gcc`)  
✅ Make installed  
✅ STM32 HAL library (see step 1)

## Steps

### 1. Download STM32 HAL Library

```bash
# Option A: Use setup script (interactive)
./setup_hal.sh

# Option B: Manual download
# 1. Visit: https://www.st.com/en/embedded-software/stm32cubeu5.html
# 2. Download and extract STM32CubeU5
# 3. Run: ./setup_hal.sh
```

### 2. Build

```bash
make
```

If successful, you'll see:
```
arm-none-eabi-size build/stm32_nucleo_u545.elf
```

### 3. Connect Board

- Connect NUCLEO board via USB to **ST-LINK port** (not USB user port)
- Verify connection: `ls /dev/ttyACM*` (should show `/dev/ttyACM0`)

### 4. Flash

**Option A: OpenOCD (easiest)**
```bash
make flash
```

**Option B: STM32CubeProgrammer**
```bash
# First install (see INSTALL_STM32CUBEPROGRAMMER.md)
make flash-stm32prog
```

### 5. Test

**Using Python (from DeviceOps):**
```python
from hardware.uart_manager import UARTManager

uart = UARTManager()
uart.open('/dev/ttyACM0', 115200)
success, response = uart.send_task(1)
print(response)  # Should print "OK LED toggled"
```

**Using serial terminal:**
```bash
screen /dev/ttyACM0 115200
# Type: TASK 1
# Should see: OK LED toggled
```

## Troubleshooting

**"No such file or directory" during build?**
→ You need to download STM32 HAL library (step 1)

**"STM32_Programmer_CLI: command not found"?**
→ Install STM32CubeProgrammer or use `make flash` (OpenOCD)

**Board not responding?**
→ Check USB connection, verify `/dev/ttyACM0` exists, check baud rate (115200)

## Next Steps

- Edit `src/main.c` to add your own task functions
- Register tasks: `qa_agent_register_task(task_num, your_function)`
- Test with DeviceOps test sequences!


