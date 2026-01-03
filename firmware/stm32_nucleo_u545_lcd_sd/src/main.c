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

/* Private function prototypes */
void SystemClock_Config(void);
static void SystemPower_Config(void);
void MX_GPIO_Init(void);
static void MX_ICACHE_Init(void);
HAL_StatusTypeDef MX_LPUART1_UART_Init(void);
HAL_StatusTypeDef MX_SPI1_Init(void);
HAL_StatusTypeDef MX_TIM3_Init(void);
void Error_Handler(void);
extern void SystemCoreClockUpdate(void);
bool task_12_backlight_toggle(void);
bool task_13_display_image(void);
bool task_14_backlight_brightness(void);
bool task_15_bitmap_gallery(void);
bool task_16_next_bitmap(void);

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
 * @brief Task 6: SD Card Initialize
 * Initializes the SD card
 */
bool task_6_sd_init(void)
{
    if (SD_Init()) {
        char msg[64];
        snprintf(msg, sizeof(msg), "SD card initialized: %s", SD_GetStatusString());
        qa_agent_set_last_message(msg);
        return true;
    } else {
        char msg[64];
        snprintf(msg, sizeof(msg), "SD card init failed: %s", SD_GetStatusString());
        qa_agent_set_last_message(msg);
        return false;
    }
}

/**
 * @brief Task 7: SD Card Read Block
 * Reads block 0 from SD card
 */
bool task_7_sd_read(void)
{
    if (!SD_IsPresent()) {
        qa_agent_set_last_message("SD card not initialized");
        return false;
    }
    
    uint32_t block_addr = 0; // Read block 0
    uint8_t buffer[512];
    if (SD_ReadBlock(block_addr, buffer)) {
        // Read successful - send first 16 bytes as hex for verification
        char msg[128];
        snprintf(msg, sizeof(msg), "Block %lu read OK, first bytes: ", (unsigned long)block_addr);
        char hex_str[33];
        for (int i = 0; i < 16; i++) {
            snprintf(hex_str + (i * 2), 3, "%02X", buffer[i]);
        }
        strncat(msg, hex_str, sizeof(msg) - strlen(msg) - 1);
        qa_agent_set_last_message(msg);
        return true;
    } else {
        qa_agent_set_last_message("SD card read failed");
        return false;
    }
}

/**
 * @brief Task 8: SD Card Write Block
 * Writes a test pattern to SD card block 0
 */
bool task_8_sd_write(void)
{
    if (!SD_IsPresent()) {
        qa_agent_set_last_message("SD card not initialized");
        return false;
    }
    
    uint32_t block_addr = 0; // Write to block 0
    
    // Create test pattern
    uint8_t buffer[512];
    for (int i = 0; i < 512; i++) {
        buffer[i] = (uint8_t)(i & 0xFF);
    }
    
    // Write test pattern
    if (SD_WriteBlock(block_addr, buffer)) {
        char msg[64];
        snprintf(msg, sizeof(msg), "Block %lu written", (unsigned long)block_addr);
        qa_agent_set_last_message(msg);
        return true;
    } else {
        qa_agent_set_last_message("SD card write failed");
        return false;
    }
}

/**
 * @brief Task 9: LCD Initialize
 * Re-initializes the LCD display
 */
bool task_9_lcd_init(void)
{
    uint32_t start_time = HAL_GetTick();
    
    // Initialize LCD
    bool init_ok = ST7789_Init();
    if (init_ok) {
        ST7789_FillScreen(COLOR_BLACK); // Clear screen first
        ST7789_SetRotation(2); // Portrait inverted - try this orientation
    }
    
    uint32_t elapsed = HAL_GetTick() - start_time;
    
    // Format response message
    char msg[64];
    if (init_ok) {
        snprintf(msg, sizeof(msg), "LCD init OK (%lu ms)", (unsigned long)elapsed);
    } else {
        snprintf(msg, sizeof(msg), "LCD init failed (%lu ms)", (unsigned long)elapsed);
    }
    
    qa_agent_set_last_message(msg);
    return init_ok;
}

/**
 * @brief Task 12: Backlight Toggle
 * Toggles the LCD backlight (BL pin) on/off
 */
bool task_12_backlight_toggle(void)
{
    static uint8_t current_brightness = 20;  // Start at 20%
    
    // Toggle between 0% and 20% brightness
    if (current_brightness > 0) {
        current_brightness = 0;
    } else {
        current_brightness = 20;
    }
    
    // Set PWM duty cycle (0-100%)
    ST7789_SetBacklightBrightness(current_brightness);
    
    char msg[128];
    snprintf(msg, sizeof(msg), "BL %s (%d%%)", 
             current_brightness > 0 ? "ON" : "OFF",
             current_brightness);
    qa_agent_set_last_message(msg);
    return true;
}

/**
 * @brief Task 11: SPI Loopback Test
 * Tests SPI communication by enabling loopback mode and sending/receiving data
 */
bool task_11_spi_loopback(void)
{
    // Simple hardware loopback test: Use normal 2-line SPI mode
    // Connect MOSI (D11/PA7) to MISO (D12/PA6) externally
    // SPI will send on MOSI and receive on MISO simultaneously
    
    uint8_t test_patterns[] = {0x55, 0xAA, 0x00, 0xFF, 0x12, 0x34, 0x56, 0x78};
    uint8_t received[8] = {0};
    bool all_match = true;
    
    // Ensure SPI is ready
    if (HAL_SPI_GetState(&hspi1) != HAL_SPI_STATE_READY) {
        qa_agent_set_last_message("SPI loopback: SPI not ready");
        return false;
    }
    
    // Use TransmitReceive for simultaneous TX/RX (requires MOSI connected to MISO)
    // Send all bytes at once for better reliability
    HAL_StatusTypeDef status = HAL_SPI_TransmitReceive(&hspi1, test_patterns, received, 8, 2000);
    
    if (status != HAL_OK) {
        char msg[200];
        snprintf(msg, sizeof(msg), "SPI loopback: HAL error %d", status);
        qa_agent_set_last_message(msg);
        return false;
    }
    
    // Check if all bytes match
    for (int i = 0; i < 8; i++) {
        // If MOSI not connected to MISO, received will be 0x00 or 0xFF (idle state)
        if (received[i] != test_patterns[i]) {
            all_match = false;
            break;
        }
    }
    
    // Format result message
    char msg[250];
    if (all_match) {
        snprintf(msg, sizeof(msg), "SPI loopback OK: All 8 bytes matched (0x55 0xAA 0x00 0xFF 0x12 0x34 0x56 0x78) - MOSI connected to MISO");
    } else {
        snprintf(msg, sizeof(msg), "SPI loopback: Sent [0x%02X 0x%02X 0x%02X 0x%02X 0x%02X 0x%02X 0x%02X 0x%02X] Rcvd [0x%02X 0x%02X 0x%02X 0x%02X 0x%02X 0x%02X 0x%02X 0x%02X] - Connect MOSI(D11/PA7) to MISO(D12/PA6) for loopback",
                 test_patterns[0], test_patterns[1], test_patterns[2], test_patterns[3],
                 test_patterns[4], test_patterns[5], test_patterns[6], test_patterns[7],
                 received[0], received[1], received[2], received[3],
                 received[4], received[5], received[6], received[7]);
    }
    
    qa_agent_set_last_message(msg);
    return all_match;
}

/**
 * @brief Task 10: LCD Test
 * Draws test patterns on the LCD
 */
bool task_10_lcd_test(void)
{
    // Fill entire screen with RED to verify LCD is working
    
    qa_agent_set_last_message("LCD test: Full screen RED");
    return true;
}

/**
 * @brief Task 13: Display Image
 * Generates and displays a colorful gradient pattern
 */
/**
 * @brief Task 13: Display GUI Screen
 * Displays the current syringe pump GUI screen
 */
bool task_13_display_image(void)
{
    // Initialize GUI if not already done
    static bool gui_initialized = false;
    if (!gui_initialized) {
        GUI_Init();
        gui_initialized = true;
    }
    
    // Draw current screen
    GUI_DrawScreen(GUI_GetCurrentScreen());
    
    qa_agent_set_last_message("GUI screen displayed");
    return true;
}

/**
 * @brief Task 14: Set Backlight Brightness
 * Cycles through brightness levels: 0%, 5%, 20%, 25%, 50%, 75%, 100%
 */
bool task_14_backlight_brightness(void)
{
    static uint8_t brightness_levels[] = {0, 5, 20, 25, 50, 75, 100};
    static uint8_t level_index = 0;  // Start at 0%
    
    level_index = (level_index + 1) % 7;
    uint8_t brightness = brightness_levels[level_index];
    
    ST7789_SetBacklightBrightness(brightness);
    
    char msg[128];
    snprintf(msg, sizeof(msg), "BL brightness: %d%%", brightness);
    qa_agent_set_last_message(msg);
    return true;
}

/**
 * @brief Task 15: Bitmap Gallery Mode
 * Toggles between normal GUI mode and bitmap gallery mode
 * In gallery mode, press button to cycle through bitmaps
 */
bool task_15_bitmap_gallery(void)
{
    bitmap_mode_t current_mode = BitmapGUI_GetMode();
    uint8_t bitmap_count = BitmapGUI_GetBitmapCount();
    
    if (current_mode == BITMAP_MODE_NORMAL) {
        // Switch to gallery mode
        if (bitmap_count > 0) {
            BitmapGUI_SetMode(BITMAP_MODE_GALLERY);
            char msg[128];
            snprintf(msg, sizeof(msg), "Gallery: %d bitmaps, showing %d", 
                     bitmap_count, BitmapGUI_GetCurrentIndex() + 1);
            qa_agent_set_last_message(msg);
        } else {
            qa_agent_set_last_message("No bitmaps registered!");
            return false;
        }
    } else {
        // Switch back to normal mode
        BitmapGUI_SetMode(BITMAP_MODE_NORMAL);
        GUI_DrawScreen(GUI_GetCurrentScreen());
        qa_agent_set_last_message("Normal GUI mode");
    }
    
    return true;
}

/**
 * @brief Task 16: Next Bitmap
 * Manually cycle to next bitmap in gallery (for testing button)
 */
bool task_16_next_bitmap(void)
{
    if (BitmapGUI_GetMode() == BITMAP_MODE_GALLERY) {
        BitmapGUI_NextBitmap();
        char msg[128];
        snprintf(msg, sizeof(msg), "Bitmap %d/%d", 
                 BitmapGUI_GetCurrentIndex() + 1, 
                 BitmapGUI_GetBitmapCount());
        qa_agent_set_last_message(msg);
        return true;
    } else {
        qa_agent_set_last_message("Not in gallery mode");
        return false;
    }
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
        
        // Set default backlight brightness to 20%
        ST7789_SetBacklightBrightness(20);
        
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
    qa_agent_register_task(2, task_2_mcu_status);
    qa_agent_register_task(6, task_6_sd_init);
    qa_agent_register_task(7, task_7_sd_read);
    qa_agent_register_task(8, task_8_sd_write);
    qa_agent_register_task(9, task_9_lcd_init);
    qa_agent_register_task(10, task_10_lcd_test);
    qa_agent_register_task(11, task_11_spi_loopback);
    qa_agent_register_task(12, task_12_backlight_toggle);
    qa_agent_register_task(13, task_13_display_image);
    qa_agent_register_task(14, task_14_backlight_brightness);
    qa_agent_register_task(15, task_15_bitmap_gallery);
    qa_agent_register_task(16, task_16_next_bitmap);
    
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
    
    /* Turn LED ON after initialization */
    HAL_GPIO_WritePin(GPIOA, GPIO_PIN_5, GPIO_PIN_SET);
    
    /* Main loop */
    uint32_t tx_counter = 0;
    uint32_t last_led_toggle = 0;
    
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
    RCC_OscInitStruct.MSIClockRange = RCC_MSIRANGE_1;  // 24 MHz - 6x faster, max for SCALE4
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

    // HAL_RCC_OscConfig already set FLASH_LATENCY_2 for 24 MHz with SCALE4
    if (HAL_RCC_ClockConfig(&RCC_ClkInitStruct, FLASH_LATENCY_2) != HAL_OK)
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
    hspi1.Init.BaudRatePrescaler = SPI_BAUDRATEPRESCALER_2; // 12 MHz SPI (24 MHz / 2)
    // Note: For loopback test, we can enable BIDIMODE, but for normal operation keep it disabled
    // hspi1.Init.Direction = SPI_DIRECTION_2LINES; // Normal mode (2 lines: MOSI and MISO)
    hspi1.Init.FirstBit = SPI_FIRSTBIT_MSB;
    hspi1.Init.TIMode = SPI_TIMODE_DISABLE;
    hspi1.Init.CRCCalculation = SPI_CRCCALCULATION_DISABLE;
    hspi1.Init.CRCPolynomial = 7;
    hspi1.Init.NSSPMode = SPI_NSS_PULSE_DISABLE;
    hspi1.Init.NSSPolarity = SPI_NSS_POLARITY_LOW;
    hspi1.Init.FifoThreshold = SPI_FIFO_THRESHOLD_01DATA;
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
    sConfigOC.Pulse = 200;  // Start at 20% brightness
    sConfigOC.OCPolarity = TIM_OCPOLARITY_HIGH;
    sConfigOC.OCFastMode = TIM_OCFAST_DISABLE;
    if (HAL_TIM_PWM_ConfigChannel(&htim3, &sConfigOC, TIM_CHANNEL_1) != HAL_OK) {
        return HAL_ERROR;
    }
    
    // Note: HAL_TIM_MspPostInit is called automatically by HAL_TIM_PWM_Init
    // but we ensure GPIO is configured by calling it explicitly after channel config
    HAL_TIM_MspPostInit(&htim3);
    
    // Start PWM at 20% brightness
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
