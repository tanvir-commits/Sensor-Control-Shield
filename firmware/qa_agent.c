/**
 * @file qa_agent.c
 * @brief QA Agent implementation for STM32
 */

#include "qa_agent.h"
#include <string.h>
#include <ctype.h>
#include <stdio.h>

/* Private constants */
#define QA_MAX_CMD_LEN 32
#define QA_MAX_MSG_LEN 64
#define QA_NUM_TASKS 16

/* Private variables */
static UART_HandleTypeDef *s_huart = NULL;
static qa_task_callback_t s_task_callbacks[QA_NUM_TASKS] = {NULL};
static char s_rx_buffer[QA_MAX_CMD_LEN + 1];
static uint8_t s_rx_index = 0;
static char s_last_message[QA_MAX_MSG_LEN + 1] = {0};

/* Private function prototypes */
static void qa_process_command(const char *cmd);
static void qa_send_response(bool success, const char *message);
static void qa_enter_sleep(qa_sleep_mode_t mode);
static void qa_clear_rx_buffer(void);

/**
 * @brief Initialize QA Agent
 */
bool qa_agent_init(UART_HandleTypeDef *huart)
{
    if (huart == NULL) {
        return false;
    }
    
    s_huart = huart;
    s_rx_index = 0;
    memset(s_rx_buffer, 0, sizeof(s_rx_buffer));
    memset(s_last_message, 0, sizeof(s_last_message));
    memset(s_task_callbacks, 0, sizeof(s_task_callbacks));
    
    return true;
}

/**
 * @brief Poll for incoming UART commands
 * 
 * Non-blocking function that reads all available bytes from UART RX buffer
 * and processes complete commands (terminated by newline or carriage return).
 */
void qa_agent_poll(void)
{
    if (s_huart == NULL) {
        return;
    }
    
    // Ensure receiver is enabled
    if (!(s_huart->Instance->CR1 & USART_CR1_RE)) {
        SET_BIT(s_huart->Instance->CR1, USART_CR1_RE);
    }
    
    // Read all available bytes from RX buffer
    while (__HAL_UART_GET_FLAG(s_huart, UART_FLAG_RXNE) != RESET) {
        // Read byte directly from RDR register (clears RXNE flag automatically)
        uint8_t byte = (uint8_t)(s_huart->Instance->RDR & 0xFF);
        
        // Check for end of command (newline or carriage return)
        if (byte == '\n' || byte == '\r') {
            if (s_rx_index > 0) {
                // Null-terminate the command
                s_rx_buffer[s_rx_index] = '\0';
                
                // Process the command
                qa_process_command(s_rx_buffer);
                
                // Clear buffer for next command
                qa_clear_rx_buffer();
            }
            // Ignore standalone newline/carriage return
        }
        // Check for buffer overflow
        else if (s_rx_index < QA_MAX_CMD_LEN) {
            s_rx_buffer[s_rx_index++] = (char)byte;
        }
        else {
            // Buffer overflow - send error and clear
            qa_send_response(false, "Command too long");
            qa_clear_rx_buffer();
        }
    }
}

/**
 * @brief Register a task callback
 */
bool qa_agent_register_task(uint8_t task_num, qa_task_callback_t callback)
{
    if (task_num < 1 || task_num > QA_NUM_TASKS) {
        return false;
    }
    
    s_task_callbacks[task_num - 1] = callback;
    return true;
}

/**
 * @brief Set last response message
 */
void qa_agent_set_last_message(const char *message)
{
    if (message == NULL) {
        s_last_message[0] = '\0';
        return;
    }
    
    strncpy(s_last_message, message, QA_MAX_MSG_LEN);
    s_last_message[QA_MAX_MSG_LEN] = '\0';  // Ensure null termination
}

/**
 * @brief Get UART handle
 */
UART_HandleTypeDef* qa_agent_get_uart(void)
{
    return s_huart;
}

/**
 * @brief Send a response back to the host (public API)
 * 
 * @param success True for OK response, False for ERR response
 * @param message Optional message string (can be NULL)
 */
void qa_agent_send_response(bool success, const char *message)
{
    qa_send_response(success, message);
}

/**
 * @brief Process received command
 */
static void qa_process_command(const char *cmd)
{
    if (cmd == NULL || strlen(cmd) == 0) {
        return;
    }
    
    // Clear last message
    s_last_message[0] = '\0';
    
    // Convert to uppercase for case-insensitive matching
    char cmd_upper[QA_MAX_CMD_LEN + 1];
    for (int i = 0; i < QA_MAX_CMD_LEN && cmd[i] != '\0'; i++) {
        cmd_upper[i] = (char)toupper((int)cmd[i]);
    }
    cmd_upper[QA_MAX_CMD_LEN] = '\0';
    
    // Parse TASK command: "TASK 1" through "TASK 10"
    if (strncmp(cmd_upper, "TASK ", 5) == 0) {
        int task_num = 0;
        if (sscanf(cmd + 5, "%d", &task_num) == 1) {
            if (task_num >= 1 && task_num <= QA_NUM_TASKS) {
                // Check if task is registered
                if (s_task_callbacks[task_num - 1] != NULL) {
                    // Execute task
                    bool success = s_task_callbacks[task_num - 1]();
                    
                    // Send response
                    if (success) {
                        qa_send_response(true, s_last_message[0] != '\0' ? s_last_message : NULL);
                    } else {
                        qa_send_response(false, s_last_message[0] != '\0' ? s_last_message : "Task failed");
                    }
                } else {
                    qa_send_response(false, "Task not registered");
                }
            } else {
                qa_send_response(false, "Invalid task number");
            }
        } else {
            qa_send_response(false, "Invalid task format");
        }
    }
    // Parse SLEEP command: "SLEEP ACTIVE/LIGHT/DEEP/SHUTDOWN"
    else if (strncmp(cmd_upper, "SLEEP ", 6) == 0) {
        const char *mode_str = cmd_upper + 6;
        qa_sleep_mode_t mode = QA_SLEEP_ACTIVE;
        bool valid_mode = false;
        
        if (strcmp(mode_str, "ACTIVE") == 0) {
            mode = QA_SLEEP_ACTIVE;
            valid_mode = true;
        } else if (strcmp(mode_str, "LIGHT") == 0) {
            mode = QA_SLEEP_LIGHT;
            valid_mode = true;
        } else if (strcmp(mode_str, "DEEP") == 0) {
            mode = QA_SLEEP_DEEP;
            valid_mode = true;
        } else if (strcmp(mode_str, "SHUTDOWN") == 0) {
            mode = QA_SLEEP_SHUTDOWN;
            valid_mode = true;
        }
        
        if (valid_mode) {
            // Send OK before entering sleep (MCU will be asleep after this)
            qa_send_response(true, NULL);
            
            // Enter sleep mode (this function may not return immediately)
            qa_enter_sleep(mode);
        } else {
            qa_send_response(false, "Invalid sleep mode");
        }
    }
    // Unknown command
    else {
        qa_send_response(false, "Unknown command");
    }
}

/**
 * @brief Send response to Pi (internal function)
 */
static void qa_send_response(bool success, const char *message)
{
    if (s_huart == NULL) {
        return;
    }
    
    char response[QA_MAX_MSG_LEN + 8];  // "OK" or "ERR" + space + message + newline
    
    if (success) {
        if (message != NULL && strlen(message) > 0) {
            snprintf(response, sizeof(response), "OK %s\n", message);
        } else {
            strcpy(response, "OK\n");
        }
    } else {
        if (message != NULL && strlen(message) > 0) {
            snprintf(response, sizeof(response), "ERR %s\n", message);
        } else {
            strcpy(response, "ERR\n");
        }
    }
    
    // Send response (blocking - simple and adequate for this use case)
    HAL_UART_Transmit(s_huart, (uint8_t*)response, strlen(response), HAL_MAX_DELAY);
}

/**
 * @brief Enter sleep mode
 */
static void qa_enter_sleep(qa_sleep_mode_t mode)
{
    switch (mode) {
        case QA_SLEEP_ACTIVE:
            // No sleep - just return
            // Note: Response already sent before calling this function
            break;
            
        case QA_SLEEP_LIGHT:
            // Light sleep: Stop 0 with low-power regulator
            // Note: Configure GPIOs for low power before sleep (user's responsibility)
            HAL_PWR_EnterSTOPMode(PWR_LOWPOWERREGULATOR_ON, PWR_STOPENTRY_WFI);
            // After wake: HAL automatically reconfigures system clock
            // User may need to reconfigure peripherals if needed
            // Uncomment if you have a custom clock config function:
            // SystemClock_Config();
            break;
            
        case QA_SLEEP_DEEP:
            // Deep sleep: Stop 2 with main regulator
            HAL_PWR_EnterSTOPMode(PWR_MAINREGULATOR_ON, PWR_STOPENTRY_WFI);
            // After wake: HAL automatically reconfigures system clock
            // User may need to reconfigure peripherals if needed
            // Uncomment if you have a custom clock config function:
            // SystemClock_Config();
            break;
            
        case QA_SLEEP_SHUTDOWN:
            // Shutdown: Standby mode (lowest power, requires reset to wake)
            // Note: This will reset the MCU on wake - all state is lost
            HAL_PWR_EnterSTANDBYMode();
            // This function does not return - MCU resets on wake
            break;
            
        default:
            break;
    }
}

/**
 * @brief Clear RX buffer
 */
static void qa_clear_rx_buffer(void)
{
    s_rx_index = 0;
    memset(s_rx_buffer, 0, sizeof(s_rx_buffer));
}

