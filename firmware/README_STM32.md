# STM32 QA Agent - Integration Guide

Minimal QA Agent implementation for STM32 that enables DeviceOps test sequence orchestration from a Raspberry Pi.

## Overview

The QA Agent implements a simple UART command protocol:
- **Commands**: `TASK 1` through `TASK 10`, `SLEEP ACTIVE/LIGHT/DEEP/SHUTDOWN`
- **Responses**: `OK` or `ERR` with optional message
- **Protocol**: ASCII, newline-terminated, 115200 baud (default)

## Files

- `qa_agent.h` - Public API header
- `qa_agent.c` - Implementation (~300 lines)

## Quick Start

### 1. Add Files to Your Project

Copy `qa_agent.h` and `qa_agent.c` to your STM32 project (e.g., in `Core/Src/` and `Core/Inc/`).

### 2. Include in Your Code

```c
#include "qa_agent.h"
```

### 3. Initialize in main()

```c
int main(void) {
    HAL_Init();
    SystemClock_Config();
    MX_USART1_UART_Init();  // Your UART initialization
    
    // Initialize QA Agent
    if (!qa_agent_init(&huart1)) {
        Error_Handler();  // Handle initialization failure
    }
    
    // Register your task callbacks
    qa_agent_register_task(1, my_task_1);
    qa_agent_register_task(2, my_task_2);
    // ... register tasks 3-10 as needed ...
    
    while (1) {
        qa_agent_poll();  // Process UART commands
        // Your other code here
    }
}
```

### 4. Implement Task Functions

```c
bool my_task_1(void) {
    // Your task 1 implementation
    HAL_GPIO_TogglePin(LED_GPIO_Port, LED_Pin);
    
    // Optional: Set response message
    qa_agent_set_last_message("LED toggled");
    
    return true;  // Return true on success, false on failure
}

bool my_task_2(void) {
    // Your task 2 implementation
    // Read sensor, toggle GPIO, etc.
    return true;
}
```

## API Reference

### `qa_agent_init(UART_HandleTypeDef *huart)`

Initialize the QA Agent with a UART handle.

**Parameters:**
- `huart`: Pointer to your UART handle (e.g., `&huart1`)

**Returns:** `true` if successful, `false` on error

**Example:**
```c
qa_agent_init(&huart1);
```

### `qa_agent_poll(void)`

Poll for incoming UART commands. Call this periodically in your main loop.

**Note:** This is non-blocking - it returns immediately if no data is available.

**Example:**
```c
while (1) {
    qa_agent_poll();
    // Other code
}
```

### `qa_agent_register_task(uint8_t task_num, qa_task_callback_t callback)`

Register a callback function for a task (1-10).

**Parameters:**
- `task_num`: Task number (1-10)
- `callback`: Function to call when task is executed

**Returns:** `true` if successful, `false` if task number is invalid

**Example:**
```c
qa_agent_register_task(1, my_task_function);
```

### `qa_agent_set_last_message(const char *message)`

Set a custom message to include in the OK/ERR response. Call this from within a task callback.

**Parameters:**
- `message`: Null-terminated string (max 64 chars)

**Example:**
```c
bool my_task(void) {
    qa_agent_set_last_message("Sensor reading: 1234");
    return true;
}
```

## Sleep Modes

The QA Agent supports four sleep modes:

| Mode | STM32 Mode | Power Consumption | Wake Source |
|------|------------|-------------------|-------------|
| ACTIVE | No sleep | Normal | N/A |
| LIGHT | Stop 0 | ~1-5 µA | GPIO interrupt, UART RX |
| DEEP | Stop 2 | ~1-5 µA | GPIO interrupt, UART RX |
| SHUTDOWN | Standby | ~0.5-2 µA | Reset pin, RTC, WKUP pin |

### Sleep Mode Notes

1. **After wake from Stop modes**: The system clock is automatically reconfigured by HAL, but you may need to reconfigure peripherals.

2. **SHUTDOWN mode**: The MCU resets on wake - all state is lost. Use only when appropriate.

3. **GPIO wake configuration**: Configure your WAKE GPIO pin as an interrupt source before entering sleep. The QA Agent does not configure GPIOs - this is your responsibility.

4. **Low power optimization**: Before entering sleep, disable unused peripherals and configure GPIOs for low power (analog mode where possible).

### Example: Sleep Mode Setup

```c
// Configure WAKE GPIO as interrupt
GPIO_InitTypeDef GPIO_InitStruct = {0};
GPIO_InitStruct.Pin = WAKE_Pin;
GPIO_InitStruct.Mode = GPIO_MODE_IT_RISING;
GPIO_InitStruct.Pull = GPIO_NOPULL;
HAL_GPIO_Init(WAKE_GPIO_Port, &GPIO_InitStruct);

// Enable interrupt
HAL_NVIC_SetPriority(EXTIx_IRQn, 0, 0);
HAL_NVIC_EnableIRQ(EXTIx_IRQn);

// Now SLEEP commands from Pi will work
```

## Protocol Details

### Command Format

Commands are ASCII strings, newline-terminated (`\n` or `\r\n`):

- `TASK 1` through `TASK 10` - Execute registered task
- `SLEEP ACTIVE` - Stay awake
- `SLEEP LIGHT` - Enter light sleep (Stop 0)
- `SLEEP DEEP` - Enter deep sleep (Stop 2)
- `SLEEP SHUTDOWN` - Enter shutdown (Standby)

Commands are case-insensitive.

### Response Format

Responses are ASCII strings, newline-terminated:

- `OK` - Command succeeded
- `OK <message>` - Command succeeded with message
- `ERR` - Command failed
- `ERR <reason>` - Command failed with reason

### Example Communication

```
Pi -> MCU: "TASK 1\n"
MCU -> Pi: "OK LED toggled\n"

Pi -> MCU: "SLEEP DEEP\n"
MCU -> Pi: "OK\n"
[MCU enters deep sleep]

[GPIO interrupt wakes MCU]
[MCU continues polling]

Pi -> MCU: "TASK 99\n"
MCU -> Pi: "ERR Invalid task number\n"
```

## Power Consumption Optimization

For ultra-low power applications:

1. **Disable unused peripherals** before sleep:
   ```c
   __HAL_RCC_ADC1_CLK_DISABLE();
   __HAL_RCC_TIM2_CLK_DISABLE();
   // etc.
   ```

2. **Configure GPIOs for low power**:
   ```c
   // Set unused GPIOs to analog mode (lowest power)
   GPIO_InitStruct.Mode = GPIO_MODE_ANALOG;
   ```

3. **Use lowest power regulator** in Stop modes (already handled for LIGHT mode)

4. **Minimize wake sources** - only enable necessary interrupts

## Troubleshooting

### MCU doesn't respond to commands

- Check UART configuration (baud rate, parity, stop bits)
- Verify UART handle is correct in `qa_agent_init()`
- Ensure `qa_agent_poll()` is called frequently in main loop
- Check UART TX/RX pins are connected correctly

### Task not executing

- Verify task is registered: `qa_agent_register_task(task_num, callback)`
- Check task number is 1-10 (not 0-9)
- Ensure callback function returns `bool`

### Sleep mode not working

- Verify GPIO wake interrupt is configured
- Check that `SystemClock_Config()` is called after wake (HAL should handle this)
- For SHUTDOWN mode, remember MCU resets on wake

### Response not received by Pi

- Check UART TX pin connection
- Verify baud rate matches (default 115200)
- Ensure UART is not being used by other code simultaneously

## STM32 U5 Specific Notes

- **Stop modes**: Use `PWR_LOWPOWERREGULATOR_ON` for LIGHT, `PWR_MAINREGULATOR_ON` for DEEP
- **Clock reconfiguration**: HAL automatically reconfigures system clock after Stop mode wake
- **Standby mode**: Lowest power, but requires reset to wake (all state lost)

## Porting to Other STM32 Families

The code should work on other STM32 families with minimal changes:

1. Update HAL includes: `#include "stm32f4xx_hal.h"` (or your family)
2. Sleep mode functions are the same across families
3. UART API is identical

## License

This code is provided as-is for integration into your STM32 projects.


