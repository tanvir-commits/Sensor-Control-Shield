# STM32 NUCLEO-U545RE-Q QA Agent Project

Standalone STM32 project for NUCLEO-U545RE-Q board with QA Agent integration. **No STM32CubeMX required!**

## Quick Start

### 1. Install STM32 HAL Library

You need to download the STM32 HAL library for STM32U5 series:

```bash
# Download STM32CubeU5 from ST website:
# https://www.st.com/en/embedded-software/stm32cubeu5.html

# Extract and copy HAL files to this project:
# - Drivers/STM32U5xx_HAL_Driver/
# - Drivers/CMSIS/
```

**Or use this automated script:**

```bash
# Download STM32CubeU5 (requires registration)
wget https://www.st.com/resource/en/embedded_software/stm32cubefw_u5_v1.0.0.zip
unzip stm32cubefw_u5_v1.0.0.zip
cp -r STM32CubeU5/Drivers/STM32U5xx_HAL_Driver Drivers/
cp -r STM32CubeU5/Drivers/CMSIS Drivers/
cp STM32CubeU5/Projects/NUCLEO-U545RE-Q/Templates/SW4STM32/STM32U545RETx_FLASH.ld .
cp STM32CubeU5/Projects/NUCLEO-U545RE-Q/Templates/SW4STM32/startup_stm32u545xx.s src/
```

### 2. Build the Project

```bash
make
```

This will create:
- `build/stm32_nucleo_u545.elf` - ELF file
- `build/stm32_nucleo_u545.hex` - Intel HEX file
- `build/stm32_nucleo_u545.bin` - Binary file

### 3. Flash to Board

**Option A: Using OpenOCD (already installed)**
```bash
make flash
```

**Option B: Using STM32CubeProgrammer**
```bash
# First, download and install STM32CubeProgrammer from:
# https://www.st.com/en/development-tools/stm32cubeprog.html

# Then flash:
make flash-stm32prog
```

**Option C: Manual flash with STM32CubeProgrammer**
```bash
STM32_Programmer_CLI -c port=SWD -w build/stm32_nucleo_u545.bin 0x08000000 -v -rst
```

### 4. Test with DeviceOps

Connect the NUCLEO board via USB (ST-LINK port). The virtual COM port should appear as `/dev/ttyACM0` (Linux) or `COMx` (Windows).

Test with Python:
```python
from hardware.uart_manager import UARTManager

uart = UARTManager()
uart.open('/dev/ttyACM0', 115200)
success, response = uart.send_task(1)
print(f"Response: {response}")  # Should print "OK LED toggled"
```

## Project Structure

```
stm32_nucleo_u545/
├── Makefile              # Build configuration
├── README.md             # This file
├── inc/                  # Header files
│   ├── main.h
│   ├── qa_agent.h        # QA Agent API
│   └── stm32u5xx_it.h
├── src/                  # Source files
│   ├── main.c            # Main application
│   ├── qa_agent.c        # QA Agent implementation
│   ├── system_stm32u5xx.c
│   ├── stm32u5xx_it.c    # Interrupt handlers
│   └── stm32u5xx_hal_msp.c
├── Drivers/              # STM32 HAL library (you need to add this)
│   ├── STM32U5xx_HAL_Driver/
│   └── CMSIS/
├── startup_stm32u545xx.s # Startup code (from STM32CubeU5)
└── STM32U545RETx_FLASH.ld # Linker script (from STM32CubeU5)
```

## Configuration

### UART Configuration

The project is configured for **LPUART1** on pins:
- **PA2** = TX
- **PA3** = RX

This connects to the ST-LINK virtual COM port on NUCLEO boards.

To change UART:
1. Edit `MX_LPUART1_UART_Init()` in `src/main.c`
2. Edit `HAL_UART_MspInit()` in `src/main.c`
3. Update interrupt handler in `src/stm32u5xx_it.c`

### Task Functions

Edit `src/main.c` to add your task functions:

```c
bool my_task_3(void) {
    // Your code here
    return true;
}

// In main():
qa_agent_register_task(3, my_task_3);
```

## Troubleshooting

### Build Errors: "No such file or directory"

You need to download and add the STM32 HAL library. See step 1 above.

### Flash Errors: "Cannot find ST-LINK"

1. Check USB connection (ST-LINK port, not USB user port)
2. Install ST-LINK drivers if needed
3. Check permissions: `sudo usermod -a -G dialout $USER` (Linux)

### UART Not Working

1. Check baud rate (115200)
2. Verify UART pins (PA2/PA3 for LPUART1)
3. Check if virtual COM port appears: `ls /dev/ttyACM*`
4. Test with serial terminal: `screen /dev/ttyACM0 115200`

## Integration with STM32CubeMX

If you want to use STM32CubeMX later:

1. Generate a new CubeMX project for NUCLEO-U545RE-Q
2. Copy `qa_agent.h` and `qa_agent.c` to your CubeMX project
3. In CubeMX `main.c`, add in USER CODE sections:

```c
/* USER CODE BEGIN Includes */
#include "qa_agent.h"
/* USER CODE END Includes */

/* USER CODE BEGIN 2 */
qa_agent_init(&hlpuart1);
qa_agent_register_task(1, my_task);
/* USER CODE END 2 */

/* USER CODE BEGIN WHILE */
qa_agent_poll();
/* USER CODE END WHILE */
```

CubeMX will preserve code in USER CODE sections when regenerating.

## License

This project uses STM32 HAL library (BSD 3-Clause) and QA Agent code (provided as-is).


