#include "main.h"
#include "qa_agent.h"
#include <stdio.h>
#include <string.h>
#include <stdbool.h>

/* Private variables */
UART_HandleTypeDef hlpuart1;  // LPUART1 for external USB-UART adapter

/* Private function prototypes */
void SystemClock_Config(void);
static void SystemPower_Config(void);
void MX_GPIO_Init(void);
static void MX_ICACHE_Init(void);
HAL_StatusTypeDef MX_LPUART1_UART_Init(void);
void Error_Handler(void);
extern void SystemCoreClockUpdate(void);

/**
 * @brief Task 1: LED Blink Pattern
 * Blinks LED 3 times with 200ms on/off delays
 */
bool task_1_led_blink(void)
{
    // Blink LED 3 times: on-off-on-off-on-off
    for (int i = 0; i < 3; i++) {
        HAL_GPIO_WritePin(GPIOA, GPIO_PIN_5, GPIO_PIN_SET);  // LED ON (active low, so SET = ON)
        HAL_Delay(200);
        HAL_GPIO_WritePin(GPIOA, GPIO_PIN_5, GPIO_PIN_RESET); // LED OFF
        HAL_Delay(200);
    }
    // Ensure LED is off at end
    HAL_GPIO_WritePin(GPIOA, GPIO_PIN_5, GPIO_PIN_RESET);
    qa_agent_set_last_message("LED blinked 3 times");
    return true;
}

/**
 * @brief Task 2: MCU Status/Info
 * Returns system clock, HCLK, and voltage scale information
 */
bool task_2_mcu_status(void)
{
    // Update SystemCoreClock variable
    SystemCoreClockUpdate();

    // Get clock frequencies
    uint32_t sysclk = HAL_RCC_GetSysClockFreq();
    uint32_t hclk = HAL_RCC_GetHCLKFreq();

    // Get voltage scale
    uint32_t vscale = HAL_PWREx_GetVoltageRange();
    const char* vscale_str = "Unknown";
    switch(vscale) {
        case PWR_REGULATOR_VOLTAGE_SCALE1: vscale_str = "Scale1"; break;
        case PWR_REGULATOR_VOLTAGE_SCALE2: vscale_str = "Scale2"; break;
        case PWR_REGULATOR_VOLTAGE_SCALE3: vscale_str = "Scale3"; break;
        case PWR_REGULATOR_VOLTAGE_SCALE4: vscale_str = "Scale4"; break;
        default: break;
    }

    // Format status message (clocks in MHz)
    char status_msg[128];
    snprintf(status_msg, sizeof(status_msg),
             "SysClk: %lu MHz, HCLK: %lu MHz, VScale: %s",
             (unsigned long)(sysclk / 1000000UL), (unsigned long)(hclk / 1000000UL), vscale_str);

    qa_agent_set_last_message(status_msg);
    return true;
}

/**
 * @brief Main function
 */
int main(void)
{
    /* Reset of all peripherals, Initializes the Flash interface and the Systick. */
    HAL_Init();
    
    /* Configure the System Power */
    SystemPower_Config();
    
    /* Configure the system clock */
    SystemClock_Config();
    
    /* Update SystemCoreClock before QA Agent init for accurate status */
    SystemCoreClockUpdate();
    
    /* Initialize all configured peripherals */
    MX_GPIO_Init();
    MX_ICACHE_Init();
    MX_LPUART1_UART_Init();
    
    /* Initialize QA Agent with LPUART1 */
    if (!qa_agent_init(&hlpuart1)) {
        Error_Handler();
    }
    
    /* Register task callbacks */
    qa_agent_register_task(1, task_1_led_blink);
    qa_agent_register_task(2, task_2_mcu_status);
    
    /* Wait for UART to stabilize */
    HAL_Delay(100);
    
    /* Test UART TX - send startup message */
    const char *startup = "QA Agent ready\r\n";
    HAL_StatusTypeDef tx_status = HAL_UART_Transmit(&hlpuart1, (uint8_t*)startup, strlen(startup), 1000);
    
    /* If TX fails, blink LED fast to indicate error */
    if (tx_status != HAL_OK) {
        // Don't hang - just continue, but we'll know TX is broken
        // Fast blink 3 times to indicate TX error
        for(int i = 0; i < 6; i++) {
            HAL_GPIO_TogglePin(GPIOA, GPIO_PIN_5);
            HAL_Delay(100);
        }
    }
    
    /* Main loop */
    uint32_t tx_counter = 0;
    uint32_t last_led_toggle = 0;
    
    while (1) {
        /* Poll for UART commands (this reads all available bytes) */
        qa_agent_poll();
        
        /* Send periodic heartbeat message every 2 seconds for monitoring */
        static uint32_t last_tx_time = 0;
        uint32_t now = HAL_GetTick();
        if ((now - last_tx_time) >= 2000) {
            char heartbeat_msg[32];
            int len = snprintf(heartbeat_msg, sizeof(heartbeat_msg), "HEARTBEAT %lu\r\n", (unsigned long)tx_counter++);
            if (len > 0) {
                HAL_StatusTypeDef tx_status = HAL_UART_Transmit(&hlpuart1, (uint8_t*)heartbeat_msg, len, 1000);
                // If TX fails, toggle LED fast to indicate error
                if (tx_status != HAL_OK) {
                    for(int i = 0; i < 6; i++) {
                        HAL_GPIO_TogglePin(GPIOA, GPIO_PIN_5);
                        HAL_Delay(50);
                    }
                }
            }
            last_tx_time = now;
        }
        
        /* LED blink - toggle every 500ms without blocking */
        if ((now - last_led_toggle) >= 500) {
            HAL_GPIO_TogglePin(GPIOA, GPIO_PIN_5);
            last_led_toggle = now;
        }
        
        /* No delay - poll as fast as possible to catch incoming commands immediately */
    }
}

/**
 * @brief System Clock Configuration (from CubeMX)
 */
void SystemClock_Config(void)
{
    RCC_OscInitTypeDef RCC_OscInitStruct = {0};
    RCC_ClkInitTypeDef RCC_ClkInitStruct = {0};

    /** Configure the main internal regulator output voltage
     */
    if (HAL_PWREx_ControlVoltageScaling(PWR_REGULATOR_VOLTAGE_SCALE4) != HAL_OK)
    {
        Error_Handler();
    }

    /** Initializes the CPU, AHB and APB buses clocks
     */
    RCC_OscInitStruct.OscillatorType = RCC_OSCILLATORTYPE_MSI;
    RCC_OscInitStruct.MSIState = RCC_MSI_ON;
    RCC_OscInitStruct.MSICalibrationValue = RCC_MSICALIBRATION_DEFAULT;
    RCC_OscInitStruct.MSIClockRange = RCC_MSIRANGE_4;
    RCC_OscInitStruct.PLL.PLLState = RCC_PLL_NONE;
    if (HAL_RCC_OscConfig(&RCC_OscInitStruct) != HAL_OK)
    {
        Error_Handler();
    }
    
    /** Initializes the CPU, AHB and APB buses clocks
     */
    RCC_ClkInitStruct.ClockType = RCC_CLOCKTYPE_HCLK|RCC_CLOCKTYPE_SYSCLK
                                |RCC_CLOCKTYPE_PCLK1|RCC_CLOCKTYPE_PCLK2
                                |RCC_CLOCKTYPE_PCLK3;
    RCC_ClkInitStruct.SYSCLKSource = RCC_SYSCLKSOURCE_MSI;
    RCC_ClkInitStruct.AHBCLKDivider = RCC_SYSCLK_DIV1;
    RCC_ClkInitStruct.APB1CLKDivider = RCC_HCLK_DIV1;
    RCC_ClkInitStruct.APB2CLKDivider = RCC_HCLK_DIV1;
    RCC_ClkInitStruct.APB3CLKDivider = RCC_HCLK_DIV1;

    if (HAL_RCC_ClockConfig(&RCC_ClkInitStruct, FLASH_LATENCY_0) != HAL_OK)
    {
        Error_Handler();
    }
}

/**
 * @brief Power Configuration (from CubeMX)
 */
static void SystemPower_Config(void)
{
    /*
     * Switch to SMPS regulator instead of LDO
     */
    if (HAL_PWREx_ConfigSupply(PWR_SMPS_SUPPLY) != HAL_OK)
    {
        Error_Handler();
    }
}

/**
 * @brief ICACHE Initialization Function (from CubeMX)
 */
static void MX_ICACHE_Init(void)
{
    /** Enable instruction cache in 1-way (direct mapped cache)
     */
    if (HAL_ICACHE_ConfigAssociativityMode(ICACHE_1WAY) != HAL_OK)
    {
        Error_Handler();
    }
    if (HAL_ICACHE_Enable() != HAL_OK)
    {
        Error_Handler();
    }
}

/**
 * @brief LPUART1 Initialization Function (from CubeMX)
 * LPUART1 on PC0 (RX) / PC1 (TX) - CN7 pins 38/36
 */
HAL_StatusTypeDef MX_LPUART1_UART_Init(void)
{
    hlpuart1.Instance = LPUART1;
    hlpuart1.Init.BaudRate = 115200;
    hlpuart1.Init.WordLength = UART_WORDLENGTH_8B;
    hlpuart1.Init.StopBits = UART_STOPBITS_1;
    hlpuart1.Init.Parity = UART_PARITY_NONE;
    hlpuart1.Init.Mode = UART_MODE_TX_RX;
    hlpuart1.Init.HwFlowCtl = UART_HWCONTROL_NONE;
    hlpuart1.Init.OneBitSampling = UART_ONE_BIT_SAMPLE_DISABLE;
    hlpuart1.Init.ClockPrescaler = UART_PRESCALER_DIV1;
    hlpuart1.AdvancedInit.AdvFeatureInit = UART_ADVFEATURE_NO_INIT;
    hlpuart1.FifoMode = UART_FIFOMODE_DISABLE;
    
    HAL_StatusTypeDef status = HAL_UART_Init(&hlpuart1);
    if (status != HAL_OK) {
        return status;
    }
    
    if (HAL_UARTEx_SetTxFifoThreshold(&hlpuart1, UART_TXFIFO_THRESHOLD_1_8) != HAL_OK)
    {
        return HAL_ERROR;
    }
    if (HAL_UARTEx_SetRxFifoThreshold(&hlpuart1, UART_RXFIFO_THRESHOLD_1_8) != HAL_OK)
    {
        return HAL_ERROR;
    }
    if (HAL_UARTEx_DisableFifoMode(&hlpuart1) != HAL_OK)
    {
        return HAL_ERROR;
    }
    
    // Explicitly enable receiver (RE bit in CR1 register)
    SET_BIT(hlpuart1.Instance->CR1, USART_CR1_RE);
    // Explicitly enable transmitter (TE bit in CR1 register)  
    SET_BIT(hlpuart1.Instance->CR1, USART_CR1_TE);
    
    // Verify UART is enabled
    if (!(hlpuart1.Instance->CR1 & USART_CR1_UE)) {
        SET_BIT(hlpuart1.Instance->CR1, USART_CR1_UE);
    }
    
    return HAL_OK;
}

/**
 * @brief GPIO Initialization Function
 */
void MX_GPIO_Init(void)
{
    GPIO_InitTypeDef GPIO_InitStruct = {0};
    
    /* GPIO Ports Clock Enable */
    __HAL_RCC_GPIOA_CLK_ENABLE();
    __HAL_RCC_GPIOC_CLK_ENABLE();
    
    /* Configure GPIO pin: PA5 (LED on NUCLEO board) */
    GPIO_InitStruct.Pin = GPIO_PIN_5;
    GPIO_InitStruct.Mode = GPIO_MODE_OUTPUT_PP;
    GPIO_InitStruct.Pull = GPIO_NOPULL;
    GPIO_InitStruct.Speed = GPIO_SPEED_FREQ_LOW;
    HAL_GPIO_Init(GPIOA, &GPIO_InitStruct);
    
    /* Initialize LED to OFF (active low, so RESET = OFF) */
    HAL_GPIO_WritePin(GPIOA, GPIO_PIN_5, GPIO_PIN_RESET);
}

/**
 * @brief This function is executed in case of error occurrence.
 */
void Error_Handler(void)
{
    /* User can add his own implementation to report the HAL error return state */
    __disable_irq();
    while (1)
    {
        /* Infinite loop on error */
        HAL_GPIO_TogglePin(GPIOA, GPIO_PIN_5); // Blink LED on error
        HAL_Delay(100);
    }
}
