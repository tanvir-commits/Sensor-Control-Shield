#include "main.h"
#include "qa_agent.h"
#include "sd_card.h"
#include "st7789.h"
#include "syringe_gui.h"
#include "bitmap_gui.h"
#include <stdio.h>
#include <string.h>
#include <stdbool.h>

/* Private variables */
UART_HandleTypeDef hlpuart1;  // LPUART1 for external USB-UART adapter
SPI_HandleTypeDef hspi1;      // SPI1 for SD card (Arduino shield D10-D13)
TIM_HandleTypeDef htim3;      // TIM3 for backlight PWM
DMA_HandleTypeDef hdma_spi1_tx;  // DMA for SPI1 TX (LCD transfers)

/* Private function prototypes */
void SystemClock_Config(void);
static void SystemPower_Config(void);
void MX_GPIO_Init(void);
static void MX_ICACHE_Init(void);
HAL_StatusTypeDef MX_LPUART1_UART_Init(void);
HAL_StatusTypeDef MX_SPI1_Init(void);
HAL_StatusTypeDef MX_TIM3_Init(void);
void HAL_TIM_MspPostInit(TIM_HandleTypeDef* htim);  // Forward declaration
void Error_Handler(void);
extern void SystemCoreClockUpdate(void);
bool task_2_lcd_off(void);
bool task_3_lcd_on(void);
bool task_4_lcd_toggle(void);

/**
 * @brief Task 1: LED Blink Pattern
 * Blinks LED 3 times with 200ms on/off delays
 */
bool task_1_led_blink(void)
{
    // Blink LED 3 times: on-off-on-off-on-off
    for (int i = 0; i < 3; i++) {
        HAL_GPIO_WritePin(GPIOA, GPIO_PIN_5, GPIO_PIN_SET);  // LED ON
        HAL_Delay(200);
        HAL_GPIO_WritePin(GPIOA, GPIO_PIN_5, GPIO_PIN_RESET); // LED OFF
        HAL_Delay(200);
    }
    // Keep LED ON at end
    HAL_GPIO_WritePin(GPIOA, GPIO_PIN_5, GPIO_PIN_SET);
    qa_agent_set_last_message("LED blinked 3 times, now ON");
    return true;
}

/**
 * @brief Task 2: LCD OFF
 * Turns off LCD backlight and puts display in sleep mode
 */
bool task_2_lcd_off(void)
{
    // Turn off backlight and put display in sleep
    ST7789_SetBacklightBrightness(0);
    ST7789_WriteCommand(0x28);  // DISPOFF
    HAL_Delay(10);
    ST7789_WriteCommand(0x10);  // SLPIN
    HAL_Delay(10);
    qa_agent_set_last_message("LCD off");
    return true;
}

/**
 * @brief Task 3: LCD ON
 * Wakes LCD display and turns on backlight
 */
bool task_3_lcd_on(void)
{
    // Wake display and turn on backlight
    ST7789_WriteCommand(0x11);  // SLPOUT
    HAL_Delay(120);
    ST7789_WriteCommand(0x29);  // DISPON
    HAL_Delay(20);
    ST7789_SetBacklightBrightness(100);
    qa_agent_set_last_message("LCD on");
    return true;
}

/**
 * @brief Task 4: LCD Next Image
 * Cycles to the next image in the gallery, wrapping around when reaching the end
 */
bool task_4_lcd_toggle(void)
{
    uint8_t bitmap_count = BitmapGUI_GetBitmapCount();
    
    if (bitmap_count == 0) {
        qa_agent_set_last_message("No bitmaps registered!");
        return false;
    }
    
    // Ensure we're in gallery mode
    if (BitmapGUI_GetMode() != BITMAP_MODE_GALLERY) {
        BitmapGUI_SetMode(BITMAP_MODE_GALLERY);
    }
    
    // Cycle to next bitmap (wraps automatically)
    BitmapGUI_NextBitmap();
    
    // Get current index after cycling
    uint8_t current_idx = BitmapGUI_GetCurrentIndex();
    char msg[128];
    snprintf(msg, sizeof(msg), "Image %d/%d", 
             current_idx + 1, bitmap_count);
    qa_agent_set_last_message(msg);
    
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
    MX_SPI1_Init();
    // Initialize TIM3 AFTER GPIO to ensure PC6 is configured for PWM, not GPIO
    MX_TIM3_Init();
    
    /* Initialize SD card */
    if (SD_Init()) {
        // SD card initialized successfully
    } else {
        // SD card init failed - continue anyway, status will be reported
    }
    
    /* Initialize GUI system */
    GUI_Init();
    
    /* Initialize LCD and draw first screen */
    if (ST7789_Init()) {
        ST7789_FillScreen(COLOR_BLACK); // Clear screen first
        ST7789_SetRotation(0); // Portrait - correct orientation (user confirmed this works)
        
        // Set default backlight brightness to 100%
        ST7789_SetBacklightBrightness(100);
        
        // Start in bitmap gallery mode for testing
        // Bitmaps should be registered by now (from GUI_Init above)
        uint8_t bitmap_count = BitmapGUI_GetBitmapCount();
        if (bitmap_count > 0) {
            BitmapGUI_SetMode(BITMAP_MODE_GALLERY);
        } else {
            // No bitmaps - show normal GUI
            GUI_DrawScreen(SCREEN_DELIVERY_STATUS);
        }
    }
    
    /* Initialize QA Agent with LPUART1 */
    if (!qa_agent_init(&hlpuart1)) {
        Error_Handler();
    }
    
    /* Register task callbacks */
    qa_agent_register_task(1, task_1_led_blink);
    qa_agent_register_task(2, task_2_lcd_off);
    qa_agent_register_task(3, task_3_lcd_on);
    qa_agent_register_task(4, task_4_lcd_toggle);
    
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
    
    /* Turn off both LEDs (LD2 on PA5, LD3 on PB5) for power measurement */
    HAL_GPIO_WritePin(GPIOA, GPIO_PIN_5, GPIO_PIN_RESET);  // LD2 OFF
    HAL_GPIO_WritePin(GPIOB, GPIO_PIN_5, GPIO_PIN_RESET); // LD3 OFF (active-high: LOW = OFF)
    
    /* Main loop */
    uint32_t tx_counter = 0;
    
    while (1) {
        /* Poll for UART commands (this reads all available bytes) */
        qa_agent_poll();
        
        /* Process button input for screen switching */
        GUI_ProcessButton();
        
        uint32_t now = HAL_GetTick();
        
        /* Send periodic heartbeat message every 2 seconds for monitoring */
        static uint32_t last_tx_time = 0;
        if ((now - last_tx_time) >= 2000) {
            char heartbeat_msg[32];
            int len = snprintf(heartbeat_msg, sizeof(heartbeat_msg), "HEARTBEAT %lu\r\n", (unsigned long)tx_counter++);
            if (len > 0) {
                HAL_UART_Transmit(&hlpuart1, (uint8_t*)heartbeat_msg, len, 1000);
                // If TX fails, LED error indication disabled for power measurement
                // if (tx_status != HAL_OK) {
                //     for(int i = 0; i < 6; i++) {
                //         HAL_GPIO_TogglePin(GPIOA, GPIO_PIN_5);
                //         HAL_Delay(50);
                //     }
                // }
            }
            last_tx_time = now;
        }
        
        /* LED blink disabled for power measurement */
        // if ((now - last_led_toggle) >= 500) {
        //     HAL_GPIO_TogglePin(GPIOA, GPIO_PIN_5);
        //     last_led_toggle = now;
        // }
        
        /* Debug: Send button state every 2 seconds */
        static uint32_t last_button_debug = 0;
        if ((now - last_button_debug) >= 2000) {
            GPIO_PinState btn = HAL_GPIO_ReadPin(GPIOC, GPIO_PIN_13);
            char btn_msg[64];
            int len = snprintf(btn_msg, sizeof(btn_msg), "BTN_STATE: PC13=%s (0x%02X)\r\n", 
                              (btn == GPIO_PIN_SET) ? "HIGH" : "LOW", (unsigned int)btn);
            if (len > 0) {
                HAL_UART_Transmit(&hlpuart1, (uint8_t*)btn_msg, len, 100);
            }
            last_button_debug = now;
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
     * SCALE1 (1.1V-1.2V) required for 160MHz operation
     */
    if (HAL_PWREx_ControlVoltageScaling(PWR_REGULATOR_VOLTAGE_SCALE1) != HAL_OK)
    {
        Error_Handler();
    }

    /** Initializes the CPU, AHB and APB buses clocks
     */
    RCC_OscInitStruct.OscillatorType = RCC_OSCILLATORTYPE_MSI;
    RCC_OscInitStruct.MSIState = RCC_MSI_ON;
    RCC_OscInitStruct.MSICalibrationValue = RCC_MSICALIBRATION_DEFAULT;
    RCC_OscInitStruct.MSIClockRange = RCC_MSIRANGE_1;  // 24 MHz MSI
    
    // Configure PLL for 160MHz: (24MHz / 3) * 20 / 1 = 160MHz
    RCC_OscInitStruct.PLL.PLLState = RCC_PLL_ON;
    RCC_OscInitStruct.PLL.PLLSource = RCC_PLLSOURCE_MSI;
    RCC_OscInitStruct.PLL.PLLM = 3;   // Divide MSI by 3 -> 8MHz
    RCC_OscInitStruct.PLL.PLLN = 20;  // Multiply by 20 -> 160MHz VCO
    RCC_OscInitStruct.PLL.PLLP = 2;   // PLLP divider (not used for SYSCLK)
    RCC_OscInitStruct.PLL.PLLQ = 2;   // PLLQ divider (for USB, etc.)
    RCC_OscInitStruct.PLL.PLLR = 1;   // PLLR divider -> 160MHz SYSCLK
    RCC_OscInitStruct.PLL.PLLRGE = RCC_PLLVCIRANGE_1;  // VCO input range 8-16 MHz (8MHz fits here)
    RCC_OscInitStruct.PLL.PLLFRACN = 0;  // No fractional part
    
    if (HAL_RCC_OscConfig(&RCC_OscInitStruct) != HAL_OK)
    {
        Error_Handler();
    }
    
    /** Initializes the CPU, AHB and APB buses clocks
     */
    RCC_ClkInitStruct.ClockType = RCC_CLOCKTYPE_HCLK|RCC_CLOCKTYPE_SYSCLK
                                |RCC_CLOCKTYPE_PCLK1|RCC_CLOCKTYPE_PCLK2
                                |RCC_CLOCKTYPE_PCLK3;
    RCC_ClkInitStruct.SYSCLKSource = RCC_SYSCLKSOURCE_PLLCLK;  // Use PLL as system clock
    RCC_ClkInitStruct.AHBCLKDivider = RCC_SYSCLK_DIV1;
    RCC_ClkInitStruct.APB1CLKDivider = RCC_HCLK_DIV1;
    RCC_ClkInitStruct.APB2CLKDivider = RCC_HCLK_DIV1;
    RCC_ClkInitStruct.APB3CLKDivider = RCC_HCLK_DIV1;

    // FLASH_LATENCY_4 required for 160MHz at SCALE1 (4 wait states)
    if (HAL_RCC_ClockConfig(&RCC_ClkInitStruct, FLASH_LATENCY_4) != HAL_OK)
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
 * @brief SPI1 Initialization Function
 * SPI1 for SD card Arduino shield: PA5 (SCK/D13), PA6 (MISO/D12), PA7 (MOSI/D11)
 * Note: PA5 is also the LED pin, but SPI takes priority when SPI1 is active
 */
HAL_StatusTypeDef MX_SPI1_Init(void)
{
    hspi1.Instance = SPI1;
    hspi1.Init.Mode = SPI_MODE_MASTER;
    hspi1.Init.Direction = SPI_DIRECTION_2LINES;
    hspi1.Init.DataSize = SPI_DATASIZE_8BIT;
    hspi1.Init.CLKPolarity = SPI_POLARITY_LOW;  // CPOL=0 for SPI Mode 0 (Waveshare official code)
    hspi1.Init.CLKPhase = SPI_PHASE_1EDGE;     // CPHA=0 for SPI Mode 0
    hspi1.Init.NSS = SPI_NSS_SOFT;
    hspi1.Init.BaudRatePrescaler = SPI_BAUDRATEPRESCALER_8; // 20 MHz SPI (160 MHz / 8)
    // Note: For loopback test, we can enable BIDIMODE, but for normal operation keep it disabled
    // hspi1.Init.Direction = SPI_DIRECTION_2LINES; // Normal mode (2 lines: MOSI and MISO)
    hspi1.Init.FirstBit = SPI_FIRSTBIT_MSB;
    hspi1.Init.TIMode = SPI_TIMODE_DISABLE;
    hspi1.Init.CRCCalculation = SPI_CRCCALCULATION_DISABLE;
    hspi1.Init.CRCPolynomial = 7;
    hspi1.Init.NSSPMode = SPI_NSS_PULSE_DISABLE;
    hspi1.Init.NSSPolarity = SPI_NSS_POLARITY_LOW;
    hspi1.Init.FifoThreshold = SPI_FIFO_THRESHOLD_08DATA;  // Increased from 01DATA to 08DATA for faster transfers
    hspi1.Init.TxCRCInitializationPattern = SPI_CRC_INITIALIZATION_ALL_ZERO_PATTERN;
    hspi1.Init.RxCRCInitializationPattern = SPI_CRC_INITIALIZATION_ALL_ZERO_PATTERN;
    hspi1.Init.MasterSSIdleness = SPI_MASTER_SS_IDLENESS_00CYCLE;
    hspi1.Init.MasterInterDataIdleness = SPI_MASTER_INTERDATA_IDLENESS_00CYCLE;
    hspi1.Init.MasterReceiverAutoSusp = SPI_MASTER_RX_AUTOSUSP_DISABLE;
    hspi1.Init.MasterKeepIOState = SPI_MASTER_KEEP_IO_STATE_DISABLE;
    hspi1.Init.IOSwap = SPI_IO_SWAP_DISABLE;
    
    if (HAL_SPI_Init(&hspi1) != HAL_OK) {
        return HAL_ERROR;
    }
    
    return HAL_OK;
}

/**
 * @brief TIM3 Initialization Function
 * TIM3 for backlight PWM on PC6 (TIM3_CH1)
 */
HAL_StatusTypeDef MX_TIM3_Init(void)
{
    TIM_MasterConfigTypeDef sMasterConfig = {0};
    TIM_OC_InitTypeDef sConfigOC = {0};
    RCC_ClkInitTypeDef clkconfig;
    uint32_t uwTimclock, uwAPB1Prescaler = 0U;
    uint32_t uwPrescalerValue = 0U;
    uint32_t pFLatency = 0U;
    
    // Get clock configuration to calculate correct TIM3 clock
    HAL_RCC_GetClockConfig(&clkconfig, &pFLatency);
    uwAPB1Prescaler = clkconfig.APB1CLKDivider;
    
    // Compute TIM3 clock: if APB1 prescaler = 1, TIM3 clock = APB1, else TIM3 clock = 2 * APB1
    if (uwAPB1Prescaler == RCC_HCLK_DIV1) {
        uwTimclock = HAL_RCC_GetPCLK1Freq();
    } else {
        uwTimclock = 2UL * HAL_RCC_GetPCLK1Freq();
    }
    
    // Configure for 1 kHz PWM frequency
    // Prescaler: divide timer clock to get 1 MHz counter clock
    uwPrescalerValue = (uint32_t)((uwTimclock / 1000000U) - 1U);
    
    htim3.Instance = TIM3;
    htim3.Init.Prescaler = uwPrescalerValue;
    htim3.Init.CounterMode = TIM_COUNTERMODE_UP;
    htim3.Init.Period = 1000 - 1;  // 1 kHz PWM frequency (1 MHz / 1000)
    htim3.Init.ClockDivision = TIM_CLOCKDIVISION_DIV1;
    htim3.Init.AutoReloadPreload = TIM_AUTORELOAD_PRELOAD_ENABLE;
    
    if (HAL_TIM_PWM_Init(&htim3) != HAL_OK) {
        return HAL_ERROR;
    }
    
    sMasterConfig.MasterOutputTrigger = TIM_TRGO_RESET;
    sMasterConfig.MasterSlaveMode = TIM_MASTERSLAVEMODE_DISABLE;
    if (HAL_TIMEx_MasterConfigSynchronization(&htim3, &sMasterConfig) != HAL_OK) {
        return HAL_ERROR;
    }
    
    sConfigOC.OCMode = TIM_OCMODE_PWM1;
    sConfigOC.Pulse = 1000;  // Start at 100% brightness
    sConfigOC.OCPolarity = TIM_OCPOLARITY_HIGH;
    sConfigOC.OCFastMode = TIM_OCFAST_DISABLE;
    if (HAL_TIM_PWM_ConfigChannel(&htim3, &sConfigOC, TIM_CHANNEL_1) != HAL_OK) {
        return HAL_ERROR;
    }
    
    // Note: HAL_TIM_MspPostInit is called automatically by HAL_TIM_PWM_Init
    // but we ensure GPIO is configured by calling it explicitly after channel config
    HAL_TIM_MspPostInit(&htim3);
    
    // Start PWM at 100% brightness
    HAL_TIM_PWM_Start(&htim3, TIM_CHANNEL_1);
    
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
    __HAL_RCC_GPIOB_CLK_ENABLE();
    __HAL_RCC_GPIOC_CLK_ENABLE();
    
    /* Configure GPIO pin: PA5 (LED on NUCLEO board) */
    /* NOTE: PA5 is also SPI1_SCK (Arduino D13) - SPI takes priority when SPI1 is active */
    /* We'll configure PA5 for SPI in HAL_SPI_MspInit, so don't configure it as GPIO here */
    /* LED will not work when SPI1 is active, which is expected for Arduino shield compatibility */
    
    /* Configure GPIO pin: PC9 (SD card CS - Arduino D10 on NUCLEO-U545RE-Q) */
    /* NOTE: LCD also uses PC9 for CS - they share SPI1 but conflict on CS pin! */
    GPIO_InitStruct.Pin = GPIO_PIN_9;
    GPIO_InitStruct.Mode = GPIO_MODE_OUTPUT_PP;
    GPIO_InitStruct.Pull = GPIO_NOPULL;
    GPIO_InitStruct.Speed = GPIO_SPEED_FREQ_LOW;
    HAL_GPIO_Init(GPIOC, &GPIO_InitStruct);
    
    /* Initialize SD CS to HIGH (deselected) */
    HAL_GPIO_WritePin(GPIOC, GPIO_PIN_9, GPIO_PIN_SET);
    
    /* Configure LCD control pins */
    /* LCD DC (D7) - PA8 */
    GPIO_InitStruct.Pin = GPIO_PIN_8;
    GPIO_InitStruct.Mode = GPIO_MODE_OUTPUT_PP;
    GPIO_InitStruct.Pull = GPIO_NOPULL;
    GPIO_InitStruct.Speed = GPIO_SPEED_FREQ_LOW;
    HAL_GPIO_Init(GPIOA, &GPIO_InitStruct);
    HAL_GPIO_WritePin(GPIOA, GPIO_PIN_8, GPIO_PIN_RESET); // DC low = command mode
    
    /* LCD RST (D8) - PC7 (per datasheet D8=PC7) */
    GPIO_InitStruct.Pin = GPIO_PIN_7;
    GPIO_InitStruct.Mode = GPIO_MODE_OUTPUT_PP;
    GPIO_InitStruct.Pull = GPIO_NOPULL;
    GPIO_InitStruct.Speed = GPIO_SPEED_FREQ_LOW;
    HAL_GPIO_Init(GPIOC, &GPIO_InitStruct);
    HAL_GPIO_WritePin(GPIOC, GPIO_PIN_7, GPIO_PIN_SET); // RST high = normal
    
    /* LCD BL (D9) - PC6 (TIM3_CH1/PWM) - Configured in HAL_TIM_MspPostInit */
    
    /* Configure User Button (B1) - PC13 */
    /* Note: On STM32U5, PC13 is in a special power domain and may need PWR configuration */
    GPIO_InitStruct.Pin = GPIO_PIN_13;
    GPIO_InitStruct.Mode = GPIO_MODE_INPUT;
    GPIO_InitStruct.Pull = GPIO_PULLDOWN;  // Try pull-down (matches BSP code)
    GPIO_InitStruct.Speed = GPIO_SPEED_FREQ_HIGH;
    HAL_GPIO_Init(GPIOC, &GPIO_InitStruct);
    
    /* Configure LD3 (PB5) - User LED */
    /* Note: LD3 might be active-low, so we'll try both HIGH and LOW */
    __HAL_RCC_GPIOB_CLK_ENABLE();
    GPIO_InitStruct.Pin = GPIO_PIN_5;
    GPIO_InitStruct.Mode = GPIO_MODE_OUTPUT_PP;
    GPIO_InitStruct.Pull = GPIO_NOPULL;
    GPIO_InitStruct.Speed = GPIO_SPEED_FREQ_LOW;
    HAL_GPIO_Init(GPIOB, &GPIO_InitStruct);
    
    /* Turn off LD3 - try LOW (standard active-high LED) */
    HAL_GPIO_WritePin(GPIOB, GPIO_PIN_5, GPIO_PIN_RESET);
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
        /* Infinite loop on error - LED blink disabled for power measurement */
        // HAL_GPIO_TogglePin(GPIOA, GPIO_PIN_5); // Blink LED on error
        HAL_Delay(100);
    }
}
