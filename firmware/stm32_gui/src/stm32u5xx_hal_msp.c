#include "main.h"

/* External DMA handle for SPI1 TX */
extern DMA_HandleTypeDef hdma_spi1_tx;

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

/**
 * @brief SPI MSP Initialization
 * This function configures the hardware resources for SPI1
 * SPI1 on PA5 (SCK/Arduino D13), PA6 (MISO/Arduino D12), PA7 (MOSI/Arduino D11)
 * Note: PA5 is also the LED pin, but SPI function takes priority
 */
void HAL_SPI_MspInit(SPI_HandleTypeDef* hspi)
{
    GPIO_InitTypeDef GPIO_InitStruct = {0};
    RCC_PeriphCLKInitTypeDef PeriphClkInit = {0};
    
    if(hspi->Instance == SPI1)
    {
        /** Initializes the peripherals clock
         */
        PeriphClkInit.PeriphClockSelection = RCC_PERIPHCLK_SPI1;
        PeriphClkInit.Spi1ClockSelection = RCC_SPI1CLKSOURCE_PCLK2;
        if (HAL_RCCEx_PeriphCLKConfig(&PeriphClkInit) != HAL_OK)
        {
            Error_Handler();
        }

        /* Peripheral clock enable */
        __HAL_RCC_SPI1_CLK_ENABLE();
        __HAL_RCC_GPIOA_CLK_ENABLE();
        __HAL_RCC_GPDMA1_CLK_ENABLE();  // Enable DMA clock
        
        /**SPI1 GPIO Configuration (Arduino Shield pins)
         * PA5     ------> SPI1_SCK  (Arduino D13)
         * PA6     ------> SPI1_MISO (Arduino D12)
         * PA7     ------> SPI1_MOSI (Arduino D11)
         */
        GPIO_InitStruct.Pin = GPIO_PIN_5 | GPIO_PIN_6 | GPIO_PIN_7;
        GPIO_InitStruct.Mode = GPIO_MODE_AF_PP;
        GPIO_InitStruct.Pull = GPIO_NOPULL;
        GPIO_InitStruct.Speed = GPIO_SPEED_FREQ_MEDIUM;
        GPIO_InitStruct.Alternate = GPIO_AF5_SPI1;
        HAL_GPIO_Init(GPIOA, &GPIO_InitStruct);

        /* Configure DMA for SPI1 TX */
        hspi->hdmatx = &hdma_spi1_tx;
        
        hdma_spi1_tx.Instance = GPDMA1_Channel0;
        hdma_spi1_tx.Init.Request = GPDMA1_REQUEST_SPI1_TX;
        hdma_spi1_tx.Init.BlkHWRequest = DMA_BREQ_SINGLE_BURST;
        hdma_spi1_tx.Init.Direction = DMA_MEMORY_TO_PERIPH;
        hdma_spi1_tx.Init.SrcInc = DMA_SINC_INCREMENTED;
        hdma_spi1_tx.Init.DestInc = DMA_DINC_FIXED;
        hdma_spi1_tx.Init.SrcDataWidth = DMA_SRC_DATAWIDTH_BYTE;
        hdma_spi1_tx.Init.DestDataWidth = DMA_DEST_DATAWIDTH_BYTE;
        hdma_spi1_tx.Init.Priority = DMA_HIGH_PRIORITY;
        hdma_spi1_tx.Init.SrcBurstLength = 8;  // Increased from 1 to 8 for faster transfers
        hdma_spi1_tx.Init.DestBurstLength = 8;  // Increased from 1 to 8 for faster transfers
        hdma_spi1_tx.Init.TransferEventMode = DMA_TCEM_BLOCK_TRANSFER;
        hdma_spi1_tx.Init.Mode = DMA_NORMAL;
        
        if (HAL_DMA_Init(&hdma_spi1_tx) != HAL_OK)
        {
            Error_Handler();
        }

        /* Link DMA to SPI */
        __HAL_LINKDMA(hspi, hdmatx, hdma_spi1_tx);

        /* DMA interrupt init */
        HAL_NVIC_SetPriority(GPDMA1_Channel0_IRQn, 0, 0);
        HAL_NVIC_EnableIRQ(GPDMA1_Channel0_IRQn);
    }
}

/**
 * @brief SPI MSP De-Initialization
 */
void HAL_SPI_MspDeInit(SPI_HandleTypeDef* hspi)
{
    if(hspi->Instance == SPI1)
    {
        /* Peripheral clock disable */
        __HAL_RCC_SPI1_CLK_DISABLE();

        /**SPI1 GPIO Configuration
         * PA5     ------> SPI1_SCK  (Arduino D13)
         * PA6     ------> SPI1_MISO (Arduino D12)
         * PA7     ------> SPI1_MOSI (Arduino D11)
         */
        HAL_GPIO_DeInit(GPIOA, GPIO_PIN_5 | GPIO_PIN_6 | GPIO_PIN_7);
        
        /* Deinitialize DMA */
        HAL_DMA_DeInit(&hdma_spi1_tx);
        HAL_NVIC_DisableIRQ(GPDMA1_Channel0_IRQn);
    }
}

/**
 * @brief TIM PWM MSP Initialization
 * This function configures the hardware resources for TIM3 PWM (backlight)
 */
void HAL_TIM_PWM_MspInit(TIM_HandleTypeDef* htim)
{
    if(htim->Instance == TIM3)
    {
        /* Peripheral clock enable */
        __HAL_RCC_TIM3_CLK_ENABLE();
    }
}

/**
 * @brief TIM MSP Post-Initialization
 * Configures GPIO for TIM3_CH1 on PC6 (backlight PWM)
 */
void HAL_TIM_MspPostInit(TIM_HandleTypeDef* htim)
{
    GPIO_InitTypeDef GPIO_InitStruct = {0};
    
    if(htim->Instance == TIM3)
    {
        __HAL_RCC_GPIOC_CLK_ENABLE();
        
        /**TIM3 GPIO Configuration
         * PC6     ------> TIM3_CH1 (Backlight PWM)
         */
        GPIO_InitStruct.Pin = GPIO_PIN_6;
        GPIO_InitStruct.Mode = GPIO_MODE_AF_PP;
        GPIO_InitStruct.Pull = GPIO_NOPULL;
        GPIO_InitStruct.Speed = GPIO_SPEED_FREQ_LOW;
        GPIO_InitStruct.Alternate = GPIO_AF2_TIM3;
        HAL_GPIO_Init(GPIOC, &GPIO_InitStruct);
    }
}

/**
 * @brief TIM PWM MSP De-Initialization
 */
void HAL_TIM_PWM_MspDeInit(TIM_HandleTypeDef* htim)
{
    if(htim->Instance == TIM3)
    {
        /* Peripheral clock disable */
        __HAL_RCC_TIM3_CLK_DISABLE();
        
        /**TIM3 GPIO Configuration
         * PC6     ------> TIM3_CH1
         */
        HAL_GPIO_DeInit(GPIOC, GPIO_PIN_6);
    }
}
