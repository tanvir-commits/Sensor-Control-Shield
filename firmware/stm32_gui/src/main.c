#include "main.h"
#include "lvgl_port.h"
#include "st7789_driver.h"
#include "lvgl.h"
#include <stdio.h>
#include <sys/unistd.h>
#include <sys/stat.h>

/* Syscall stubs for newlib */
int _write(int file, char *ptr, int len)
{
    (void)file;
    (void)ptr;
    (void)len;
    return len;
}

int _read(int file, char *ptr, int len)
{
    (void)file;
    (void)ptr;
    (void)len;
    return 0;
}

int _lseek(int file, int ptr, int dir)
{
    (void)file;
    (void)ptr;
    (void)dir;
    return 0;
}

int _isatty(int file)
{
    (void)file;
    return 1;
}

void _exit(int status)
{
    (void)status;
    while(1);
}

int _close(int file)
{
    (void)file;
    return 0;
}

int _fstat(int file, struct stat *st)
{
    (void)file;
    (void)st;
    return 0;
}

/* Private variables */
UART_HandleTypeDef hlpuart1;
SPI_HandleTypeDef hspi1;
TIM_HandleTypeDef htim3;
DMA_HandleTypeDef hdma_spi1_tx;

/* Private function prototypes */
void SystemClock_Config(void);
static void SystemPower_Config(void);
void MX_GPIO_Init(void);
static void MX_ICACHE_Init(void);
HAL_StatusTypeDef MX_LPUART1_UART_Init(void);
HAL_StatusTypeDef MX_SPI1_Init(void);
HAL_StatusTypeDef MX_TIM3_Init(void);
void HAL_TIM_MspPostInit(TIM_HandleTypeDef* htim);
void Error_Handler(void);
extern void SystemCoreClockUpdate(void);

/**
 * @brief  The application entry point.
 */
int main(void)
{
    /* Reset of all peripherals, Initializes the Flash interface and the Systick. */
    HAL_Init();
    
    /* Configure the System Power */
    SystemPower_Config();
    
    /* Configure the system clock */
    SystemClock_Config();
    
    /* Update SystemCoreClock */
    SystemCoreClockUpdate();
    
    /* Initialize all configured peripherals */
    MX_GPIO_Init();
    MX_ICACHE_Init();
    MX_LPUART1_UART_Init();
    MX_SPI1_Init();
    MX_TIM3_Init();
    
    /* Initialize ST7789 display */
    if (!ST7789_Init()) {
        Error_Handler();
    }
    
    ST7789_SetRotation(0);  // Portrait mode
    ST7789_SetBacklightBrightness(100);
    
    /* Clear display completely before LVGL starts */
    ST7789_FillScreen(0x0000);  // Black
    HAL_Delay(50);
    
    /* Initialize LVGL port */
    if (!lvgl_port_init()) {
        Error_Handler();
    }
    
    /* Initialize SquareLine Studio UI - standard pattern */
    #include "ui.h"
    ui_init();
    
    /* Load Screen2 */
    lv_screen_load(ui_Screen2);
    
    /* Screen switching timing */
    uint32_t start_time = HAL_GetTick();
    uint8_t current_screen = 2;  // Start with Screen2
    
    /* Main loop - standard pattern */
    while (1) {
        lv_timer_handler();
        
        /* Switch to Screen3 after 3 seconds */
        uint32_t elapsed = HAL_GetTick() - start_time;
        if (current_screen == 2 && elapsed >= 3000) {
            lv_screen_load(ui_Screen3);
            current_screen = 3;
        }
        
        HAL_Delay(5);
    }
}

/**
 * @brief  This function is executed in case of error occurrence.
 */
void Error_Handler(void)
{
    /* User can add his own implementation to report the HAL error return state */
    __disable_irq();
    while (1) {
        /* Infinite loop on error */
    }
}

/**
 * @brief System Clock Configuration
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
    RCC_OscInitStruct.MSIClockRange = RCC_MSIRANGE_4;
    RCC_OscInitStruct.PLL.PLLState = RCC_PLL_ON;
    RCC_OscInitStruct.PLL.PLLSource = RCC_PLLSOURCE_MSI;
    RCC_OscInitStruct.PLL.PLLM = 1;
    RCC_OscInitStruct.PLL.PLLN = 80;
    RCC_OscInitStruct.PLL.PLLP = 2;
    RCC_OscInitStruct.PLL.PLLQ = 2;
    RCC_OscInitStruct.PLL.PLLR = 2;
    RCC_OscInitStruct.PLL.PLLRGE = RCC_PLLVCIRANGE_0;
    RCC_OscInitStruct.PLL.PLLFRACN = 0;
    if (HAL_RCC_OscConfig(&RCC_OscInitStruct) != HAL_OK)
    {
        Error_Handler();
    }

    /** Initializes the CPU, AHB and APB buses clocks
     */
    RCC_ClkInitStruct.ClockType = RCC_CLOCKTYPE_HCLK|RCC_CLOCKTYPE_SYSCLK
                                  |RCC_CLOCKTYPE_PCLK1|RCC_CLOCKTYPE_PCLK2
                                  |RCC_CLOCKTYPE_PCLK3;
    RCC_ClkInitStruct.SYSCLKSource = RCC_SYSCLKSOURCE_PLLCLK;
    RCC_ClkInitStruct.AHBCLKDivider = RCC_SYSCLK_DIV1;
    RCC_ClkInitStruct.APB1CLKDivider = RCC_HCLK_DIV1;
    RCC_ClkInitStruct.APB2CLKDivider = RCC_HCLK_DIV1;
    RCC_ClkInitStruct.APB3CLKDivider = RCC_HCLK_DIV1;

    if (HAL_RCC_ClockConfig(&RCC_ClkInitStruct, FLASH_LATENCY_4) != HAL_OK)
    {
        Error_Handler();
    }
}

/**
 * @brief System Power Configuration
 */
static void SystemPower_Config(void)
{
    HAL_PWREx_ControlVoltageScaling(PWR_REGULATOR_VOLTAGE_SCALE1);
}

/**
 * @brief ICACHE Initialization Function
 */
static void MX_ICACHE_Init(void)
{
    /* Enable instruction cache */
    if (HAL_ICACHE_Enable() != HAL_OK)
    {
        Error_Handler();
    }
}

/**
 * @brief LPUART1 Initialization Function
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
    
    return HAL_UART_Init(&hlpuart1);
}

/**
 * @brief SPI1 Initialization Function
 */
HAL_StatusTypeDef MX_SPI1_Init(void)
{
    hspi1.Instance = SPI1;
    hspi1.Init.Mode = SPI_MODE_MASTER;
    hspi1.Init.Direction = SPI_DIRECTION_2LINES;
    hspi1.Init.DataSize = SPI_DATASIZE_8BIT;
    hspi1.Init.CLKPolarity = SPI_POLARITY_LOW;
    hspi1.Init.CLKPhase = SPI_PHASE_1EDGE;
    hspi1.Init.NSS = SPI_NSS_SOFT;
    hspi1.Init.BaudRatePrescaler = SPI_BAUDRATEPRESCALER_4;
    hspi1.Init.FirstBit = SPI_FIRSTBIT_MSB;
    hspi1.Init.TIMode = SPI_TIMODE_DISABLE;
    hspi1.Init.CRCCalculation = SPI_CRCCALCULATION_DISABLE;
    hspi1.Init.CRCPolynomial = 0x7;
    hspi1.Init.NSSPMode = SPI_NSS_PULSE_ENABLE;
    hspi1.Init.NSSPolarity = SPI_NSS_POLARITY_LOW;
    hspi1.Init.FifoThreshold = SPI_FIFO_THRESHOLD_01DATA;
    hspi1.Init.TxCRCInitializationPattern = SPI_CRC_INITIALIZATION_ALL_ZERO_PATTERN;
    hspi1.Init.RxCRCInitializationPattern = SPI_CRC_INITIALIZATION_ALL_ZERO_PATTERN;
    hspi1.Init.MasterSSIdleness = SPI_MASTER_SS_IDLENESS_00CYCLE;
    hspi1.Init.MasterInterDataIdleness = SPI_MASTER_INTERDATA_IDLENESS_00CYCLE;
    hspi1.Init.MasterReceiverAutoSusp = SPI_MASTER_RX_AUTOSUSP_DISABLE;
    hspi1.Init.MasterKeepIOState = SPI_MASTER_KEEP_IO_STATE_DISABLE;
    hspi1.Init.IOSwap = SPI_IO_SWAP_DISABLE;
    
    return HAL_SPI_Init(&hspi1);
}

/**
 * @brief TIM3 Initialization Function
 */
HAL_StatusTypeDef MX_TIM3_Init(void)
{
    TIM_ClockConfigTypeDef sClockSourceConfig = {0};
    TIM_MasterConfigTypeDef sMasterConfig = {0};

    htim3.Instance = TIM3;
    htim3.Init.Prescaler = 159;
    htim3.Init.CounterMode = TIM_COUNTERMODE_UP;
    htim3.Init.Period = 999;
    htim3.Init.ClockDivision = TIM_CLOCKDIVISION_DIV1;
    htim3.Init.AutoReloadPreload = TIM_AUTORELOAD_PRELOAD_DISABLE;
    if (HAL_TIM_Base_Init(&htim3) != HAL_OK)
    {
        return HAL_ERROR;
    }
    sClockSourceConfig.ClockSource = TIM_CLOCKSOURCE_INTERNAL;
    if (HAL_TIM_ConfigClockSource(&htim3, &sClockSourceConfig) != HAL_OK)
    {
        return HAL_ERROR;
    }
    sMasterConfig.MasterOutputTrigger = TIM_TRGO_RESET;
    sMasterConfig.MasterSlaveMode = TIM_MASTERSLAVEMODE_DISABLE;
    if (HAL_TIMEx_MasterConfigSynchronization(&htim3, &sMasterConfig) != HAL_OK)
    {
        return HAL_ERROR;
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
    __HAL_RCC_GPIOB_CLK_ENABLE();
    __HAL_RCC_GPIOC_CLK_ENABLE();

    /* Configure LCD CS pin: PC9 */
    GPIO_InitStruct.Pin = GPIO_PIN_9;
    GPIO_InitStruct.Mode = GPIO_MODE_OUTPUT_PP;
    GPIO_InitStruct.Pull = GPIO_NOPULL;
    GPIO_InitStruct.Speed = GPIO_SPEED_FREQ_LOW;
    HAL_GPIO_Init(GPIOC, &GPIO_InitStruct);
    HAL_GPIO_WritePin(GPIOC, GPIO_PIN_9, GPIO_PIN_SET);

    /* Configure LCD DC pin: PA8 */
    GPIO_InitStruct.Pin = GPIO_PIN_8;
    GPIO_InitStruct.Mode = GPIO_MODE_OUTPUT_PP;
    GPIO_InitStruct.Pull = GPIO_NOPULL;
    GPIO_InitStruct.Speed = GPIO_SPEED_FREQ_LOW;
    HAL_GPIO_Init(GPIOA, &GPIO_InitStruct);
    HAL_GPIO_WritePin(GPIOA, GPIO_PIN_8, GPIO_PIN_RESET);

    /* Configure LCD RST pin: PC7 */
    GPIO_InitStruct.Pin = GPIO_PIN_7;
    GPIO_InitStruct.Mode = GPIO_MODE_OUTPUT_PP;
    GPIO_InitStruct.Pull = GPIO_NOPULL;
    GPIO_InitStruct.Speed = GPIO_SPEED_FREQ_LOW;
    HAL_GPIO_Init(GPIOC, &GPIO_InitStruct);
    HAL_GPIO_WritePin(GPIOC, GPIO_PIN_7, GPIO_PIN_SET);
}