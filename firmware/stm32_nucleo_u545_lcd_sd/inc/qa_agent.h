/**
 * @file qa_agent.h
 * @brief QA Agent for STM32 - Minimal UART command interface for DeviceOps test sequences
 * 
 * This module implements a simple UART-based command protocol that allows a Raspberry Pi
 * to orchestrate test sequences on an STM32 MCU. The MCU executes simple primitives (tasks)
 * and enters sleep modes on command.
 * 
 * Protocol:
 *   - Commands: "TASK 1" through "TASK 10", "SLEEP ACTIVE/LIGHT/DEEP/SHUTDOWN"
 *   - Responses: "OK" or "ERR" with optional message
 * 
 * @note Designed for STM32 U5 series but should work on other STM32 families
 */

#ifndef QA_AGENT_H
#define QA_AGENT_H

#ifdef __cplusplus
extern "C" {
#endif

#include <stdbool.h>
#include <stdint.h>
#include "stm32u5xx_hal.h"

/**
 * @brief Task callback function type
 * 
 * User-defined functions for tasks 1-10. Return true on success, false on failure.
 * Optional message can be set via qa_agent_set_last_message() if needed.
 * 
 * @return true if task executed successfully, false otherwise
 */
typedef bool (*qa_task_callback_t)(void);

/**
 * @brief Sleep mode enumeration
 */
typedef enum {
    QA_SLEEP_ACTIVE = 0,   ///< No sleep (stay awake)
    QA_SLEEP_LIGHT,        ///< Light sleep (Stop 0)
    QA_SLEEP_DEEP,         ///< Deep sleep (Stop 2)
    QA_SLEEP_SHUTDOWN      ///< Shutdown (Standby)
} qa_sleep_mode_t;

/**
 * @brief Initialize QA Agent
 * 
 * Must be called once after HAL initialization and UART configuration.
 * 
 * @param huart Pointer to UART handle (e.g., &huart1)
 * @return true if initialization successful, false otherwise
 */
bool qa_agent_init(UART_HandleTypeDef *huart);

/**
 * @brief Poll for incoming UART commands
 * 
 * Call this function periodically in your main loop. It checks for incoming
 * UART data and processes complete commands.
 * 
 * @note This is a non-blocking function. It returns immediately if no data available.
 */
void qa_agent_poll(void);

/**
 * @brief Register a task callback
 * 
 * Register a user-defined function to be called when a TASK command is received.
 * Tasks are numbered 1-10 (internally stored as indices 0-9).
 * 
 * @param task_num Task number (1-10)
 * @param callback Function to call when task is executed
 * @return true if registration successful, false if invalid task number
 * 
 * @example
 *   qa_agent_register_task(1, my_task_1_function);
 */
bool qa_agent_register_task(uint8_t task_num, qa_task_callback_t callback);

/**
 * @brief Set last response message
 * 
 * Optional: Set a custom message to be included in the OK/ERR response.
 * Call this from within a task callback if you want to provide additional info.
 * 
 * @param message Null-terminated string (max 64 chars, will be truncated)
 * 
 * @example
 *   bool my_task(void) {
 *       qa_agent_set_last_message("Task completed, LED toggled");
 *       return true;
 *   }
 */
void qa_agent_set_last_message(const char *message);

/**
 * @brief Get UART handle
 * 
 * Utility function to retrieve the UART handle (useful for debugging).
 * 
 * @return Pointer to UART handle, or NULL if not initialized
 */
UART_HandleTypeDef* qa_agent_get_uart(void);

/**
 * @brief Send a response back to the host
 * 
 * @param success True for OK response, False for ERR response
 * @param message Optional message string (can be NULL)
 */
void qa_agent_send_response(bool success, const char *message);

#ifdef __cplusplus
}
#endif

#endif /* QA_AGENT_H */

