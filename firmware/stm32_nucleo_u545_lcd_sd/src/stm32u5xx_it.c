/**
 * @file stm32u5xx_it.c
 * @brief Interrupt Service Routines
 */

#include "main.h"
#include "stm32u5xx_it.h"

/* Not needed for minimal LED test */

/**
 * @brief This function handles Non maskable interrupt.
 */
void NMI_Handler(void)
{
    while (1) {}
}

/**
 * @brief This function handles Hard fault interrupt.
 */
void HardFault_Handler(void)
{
    while (1) {}
}

/**
 * @brief This function handles Memory management fault.
 */
void MemManage_Handler(void)
{
    while (1) {}
}

/**
 * @brief This function handles Pre-fetch fault, memory access fault.
 */
void BusFault_Handler(void)
{
    while (1) {}
}

/**
 * @brief This function handles Undefined instruction or illegal state.
 */
void UsageFault_Handler(void)
{
    while (1) {}
}

/**
 * @brief This function handles System service call via SWI instruction.
 */
void SVC_Handler(void)
{
}

/**
 * @brief This function handles Debug monitor.
 */
void DebugMon_Handler(void)
{
}

/**
 * @brief This function handles Pendable request for system service.
 */
void PendSV_Handler(void)
{
}

/**
 * @brief This function handles System tick timer.
 */
void SysTick_Handler(void)
{
    HAL_IncTick();
}

/**
 * @brief This function handles LPUART1 global interrupt (PC0/PC1).
 */
void LPUART1_IRQHandler(void)
{
    /* Empty handler - UART not used in minimal LED blink firmware */
}

/**
 * @brief This function handles USART1 global interrupt (blocked by ST-LINK HMI BSP).
 */
void USART1_IRQHandler(void)
{
    /* USART1 is controlled by ST-LINK firmware, not available for user code */
}

