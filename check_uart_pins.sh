#!/bin/bash
echo "=== Checking UART Pin Configuration ==="
echo ""
echo "Current firmware configuration:"
grep -A 10 "HAL_UART_MspInit" firmware/stm32_nucleo_u545/src/main.c | grep -E "(PA[0-9]|GPIO_PIN|Alternate)" | head -10
echo ""
echo "UART Instance:"
grep "huart1.Instance" firmware/stm32_nucleo_u545/src/main.c
