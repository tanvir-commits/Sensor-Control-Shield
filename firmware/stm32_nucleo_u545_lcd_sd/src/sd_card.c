#include "sd_card.h"
#include <string.h>

/* External SPI handle - will be initialized in main.c */
extern SPI_HandleTypeDef hspi1;

/* SD Card Status */
static bool sd_initialized = false;
static bool sd_present = false;
static const char* sd_status_msg = "Not initialized";

/**
 * @brief Set SD card CS pin LOW (select SD card)
 */
void SD_CS_Low(void)
{
    HAL_GPIO_WritePin(SD_CS_PORT, SD_CS_PIN, GPIO_PIN_RESET);
}

/**
 * @brief Set SD card CS pin HIGH (deselect SD card)
 */
void SD_CS_High(void)
{
    HAL_GPIO_WritePin(SD_CS_PORT, SD_CS_PIN, GPIO_PIN_SET);
}

/**
 * @brief Transfer one byte via SPI
 */
uint8_t SD_SPI_Transfer(uint8_t data)
{
    uint8_t rx_data = 0;
    HAL_SPI_TransmitReceive(&hspi1, &data, &rx_data, 1, 1000);
    return rx_data;
}

/**
 * @brief Send dummy bytes to SD card (for clock generation)
 */
static void SD_SendDummyBytes(uint8_t count)
{
    for (uint8_t i = 0; i < count; i++) {
        SD_SPI_Transfer(0xFF);
    }
}

/**
 * @brief Wait for SD card to be ready (wait for 0xFF response)
 */
static uint8_t SD_WaitReady(uint32_t timeout_ms)
{
    uint32_t start = HAL_GetTick();
    uint8_t response;
    
    do {
        response = SD_SPI_Transfer(0xFF);
        if (response == 0xFF) {
            return 0xFF;
        }
        if ((HAL_GetTick() - start) > timeout_ms) {
            return 0x00; // Timeout
        }
    } while (1);
}

/**
 * @brief Send command to SD card
 * @param cmd Command byte
 * @param arg Command argument (32-bit)
 * @param response Pointer to store response (1 byte for R1, 5 bytes for R7)
 * @return true if command sent successfully
 */
bool SD_SendCommand(uint8_t cmd, uint32_t arg, uint8_t *response)
{
    uint8_t crc = 0x01; // Dummy CRC for CMD0, CMD8 uses proper CRC
    
    // CMD8 requires proper CRC
    if (cmd == CMD8) {
        crc = 0x87; // CRC for CMD8 with 0x1AA argument
    }
    
    // Send command packet: [Start(0x00)|CMD|ARG(4 bytes)|CRC|Stop(0x01)]
    SD_CS_Low();
    SD_SendDummyBytes(1); // 8 clock cycles
    
    SD_SPI_Transfer(0x40 | cmd); // Start bit (0) + command
    SD_SPI_Transfer((arg >> 24) & 0xFF);
    SD_SPI_Transfer((arg >> 16) & 0xFF);
    SD_SPI_Transfer((arg >> 8) & 0xFF);
    SD_SPI_Transfer(arg & 0xFF);
    SD_SPI_Transfer(crc);
    
    // Wait for response (R1 response)
    // SD cards can take up to 8 bytes (64 clocks) to respond
    uint8_t r1 = 0xFF;
    uint8_t retry_count = 0;
    const uint8_t max_retries = 10; // Try up to 10 bytes
    
    do {
        r1 = SD_SPI_Transfer(0xFF);
        if ((r1 & 0x80) == 0) { // Response bit is 0 (valid response)
            break;
        }
        retry_count++;
        if (retry_count >= max_retries) {
            SD_CS_High();
            SD_SendDummyBytes(1);
            return false; // Timeout - no valid response
        }
    } while (1);
    
    if (response) {
        response[0] = r1;
        
        // For CMD8, read R7 response (4 additional bytes)
        if (cmd == CMD8 && r1 == 0x01) {
            response[1] = SD_SPI_Transfer(0xFF);
            response[2] = SD_SPI_Transfer(0xFF);
            response[3] = SD_SPI_Transfer(0xFF);
            response[4] = SD_SPI_Transfer(0xFF);
        }
    }
    
    SD_CS_High();
    SD_SendDummyBytes(1);
    
    return true;
}

/**
 * @brief Initialize SD card
 * @return true if initialization successful
 */
bool SD_Init(void)
{
    uint8_t response[5];
    uint32_t start_time;
    
    sd_initialized = false;
    sd_present = false;
    sd_status_msg = "Initializing...";
    
    // Initialize CS pin (high = deselected)
    SD_CS_High();
    
    // Send 74+ clock cycles with CS high (SD card spec requirement)
    // Use more bytes to ensure proper initialization
    SD_SendDummyBytes(20); // 160 clock cycles
    
    // Small delay to let card stabilize
    HAL_Delay(10);
    
    // Send CMD0 (GO_IDLE_STATE) - reset SD card
    // Try multiple times as some cards need retries
    uint8_t cmd0_retries = 3;
    bool cmd0_success = false;
    
    for (uint8_t retry = 0; retry < cmd0_retries; retry++) {
        if (SD_SendCommand(CMD0, 0, response)) {
            if (response[0] == R1_IDLE_STATE) {
                cmd0_success = true;
                break;
            }
        }
        HAL_Delay(10); // Wait between retries
    }
    
    if (!cmd0_success) {
        sd_status_msg = "SD card not responding";
        return false;
    }
    
    // Send CMD8 (SEND_IF_COND) - check voltage range
    if (!SD_SendCommand(CMD8, 0x1AA, response)) {
        sd_status_msg = "CMD8 failed";
        return false;
    }
    
    // Check if card supports CMD8 (SDC v2+)
    if ((response[0] & 0x04) == 0) {
        // Card supports CMD8, check voltage
        if (response[4] != 0xAA) {
            sd_status_msg = "Voltage mismatch";
            return false;
        }
    }
    
    // Send ACMD41 (SD_SEND_OP_COND) repeatedly until card is ready
    start_time = HAL_GetTick();
    do {
        // Send CMD55 first (APP_CMD)
        SD_SendCommand(CMD55, 0, response);
        
        // Send ACMD41
        SD_SendCommand(ACMD41, 0x40000000, response); // HCS bit set
        
        if (response[0] == 0x00) {
            // Card is ready
            break;
        }
        
        if ((HAL_GetTick() - start_time) > 5000) {
            sd_status_msg = "Init timeout";
            return false;
        }
        
        HAL_Delay(10);
    } while (1);
    
    // Send CMD58 (READ_OCR) to verify card type
    SD_SendCommand(CMD58, 0, response);
    
    sd_initialized = true;
    sd_present = true;
    sd_status_msg = "Initialized";
    
    return true;
}

/**
 * @brief Read a single block (512 bytes) from SD card
 * @param block_addr Block address (0-based)
 * @param buffer Buffer to store data (must be at least 512 bytes)
 * @return true if read successful
 */
bool SD_ReadBlock(uint32_t block_addr, uint8_t *buffer)
{
    uint8_t response;
    
    if (!sd_initialized) {
        return false;
    }
    
    // Send CMD17 (READ_SINGLE_BLOCK)
    // SDHC/SDXC cards use block addressing, SDSC uses byte addressing
    // For simplicity, assume SDHC (block addressing)
    if (!SD_SendCommand(CMD17, block_addr, &response)) {
        return false;
    }
    
    if (response != 0x00) {
        return false; // Error response
    }
    
    // Wait for data token (0xFE)
    uint32_t timeout = 100;
    uint32_t start = HAL_GetTick();
    uint8_t token;
    
    do {
        token = SD_SPI_Transfer(0xFF);
        if (token == 0xFE) {
            break;
        }
        if ((HAL_GetTick() - start) > timeout) {
            SD_CS_High();
            return false; // Timeout
        }
    } while (1);
    
    // Read 512 bytes of data
    SD_CS_Low();
    for (uint16_t i = 0; i < 512; i++) {
        buffer[i] = SD_SPI_Transfer(0xFF);
    }
    
    // Read CRC (2 bytes) - ignore for now
    SD_SPI_Transfer(0xFF);
    SD_SPI_Transfer(0xFF);
    
    SD_CS_High();
    SD_SendDummyBytes(1);
    
    return true;
}

/**
 * @brief Write a single block (512 bytes) to SD card
 * @param block_addr Block address (0-based)
 * @param buffer Buffer containing data (must be 512 bytes)
 * @return true if write successful
 */
bool SD_WriteBlock(uint32_t block_addr, const uint8_t *buffer)
{
    uint8_t response;
    
    if (!sd_initialized) {
        return false;
    }
    
    // Send CMD24 (WRITE_BLOCK)
    if (!SD_SendCommand(CMD24, block_addr, &response)) {
        return false;
    }
    
    if (response != 0x00) {
        return false; // Error response
    }
    
    // Send data token (0xFE)
    SD_CS_Low();
    SD_SPI_Transfer(0xFE);
    
    // Send 512 bytes of data
    for (uint16_t i = 0; i < 512; i++) {
        SD_SPI_Transfer(buffer[i]);
    }
    
    // Send dummy CRC (2 bytes)
    SD_SPI_Transfer(0xFF);
    SD_SPI_Transfer(0xFF);
    
    // Wait for data response token
    uint8_t data_response = SD_SPI_Transfer(0xFF);
    if ((data_response & 0x1F) != 0x05) {
        SD_CS_High();
        SD_SendDummyBytes(1);
        return false; // Write error
    }
    
    // Wait for write to complete
    if (SD_WaitReady(500) != 0xFF) {
        SD_CS_High();
        SD_SendDummyBytes(1);
        return false; // Timeout
    }
    
    SD_CS_High();
    SD_SendDummyBytes(1);
    
    return true;
}

/**
 * @brief Check if SD card is present
 * @return true if SD card is present and initialized
 */
bool SD_IsPresent(void)
{
    return sd_present && sd_initialized;
}

/**
 * @brief Get SD card status string
 * @return Status message string
 */
const char* SD_GetStatusString(void)
{
    return sd_status_msg;
}

