#include "main.h"

/**
 * @brief Initializes the Global MSP (from CubeMX)
 */
void HAL_MspInit(void)
{
    __HAL_RCC_PWR_CLK_ENABLE();
}

/**
 * @brief UART MSP Initialization (from CubeMX)
 * This function configures the hardware resources for LPUART1
 */
void HAL_UART_MspInit(UART_HandleTypeDef* huart)
{
    GPIO_InitTypeDef GPIO_InitStruct = {0};
    RCC_PeriphCLKInitTypeDef PeriphClkInit = {0};
    
    if(huart->Instance == LPUART1)
    {
        /** Initializes the peripherals clock
         */
        PeriphClkInit.PeriphClockSelection = RCC_PERIPHCLK_LPUART1;
        PeriphClkInit.Lpuart1ClockSelection = RCC_LPUART1CLKSOURCE_PCLK3;
        if (HAL_RCCEx_PeriphCLKConfig(&PeriphClkInit) != HAL_OK)
        {
            Error_Handler();
        }

        /* Peripheral clock enable */
        __HAL_RCC_LPUART1_CLK_ENABLE();
        __HAL_RCC_GPIOC_CLK_ENABLE();
        
        /**LPUART1 GPIO Configuration
         * PC0     ------> LPUART1_RX (CN7 pin 38)
         * PC1     ------> LPUART1_TX (CN7 pin 36)
         */
        GPIO_InitStruct.Pin = GPIO_PIN_0 | GPIO_PIN_1;
        GPIO_InitStruct.Mode = GPIO_MODE_AF_PP;
        GPIO_InitStruct.Pull = GPIO_NOPULL;
        GPIO_InitStruct.Speed = GPIO_SPEED_FREQ_LOW;
        GPIO_InitStruct.Alternate = GPIO_AF8_LPUART1;
        HAL_GPIO_Init(GPIOC, &GPIO_InitStruct);
    }
}

/**
 * @brief UART MSP De-Initialization (from CubeMX)
 */
void HAL_UART_MspDeInit(UART_HandleTypeDef* huart)
{
    if(huart->Instance == LPUART1)
    {
        /* Peripheral clock disable */
        __HAL_RCC_LPUART1_CLK_DISABLE();

        /**LPUART1 GPIO Configuration
         * PC0     ------> LPUART1_RX (CN7 pin 38)
         * PC1     ------> LPUART1_TX (CN7 pin 36)
         */
        HAL_GPIO_DeInit(GPIOC, GPIO_PIN_0 | GPIO_PIN_1);
    }
}
