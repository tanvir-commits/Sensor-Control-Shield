/**
 * @file stm32u5xx_it.c
 * @brief Interrupt Service Routines
 */

#include "main.h"
#include "stm32u5xx_it.h"

/* External DMA handle for SPI1 TX */
extern DMA_HandleTypeDef hdma_spi1_tx;

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
extern UART_HandleTypeDef hlpuart1;  // Declare external UART handle

void LPUART1_IRQHandler(void)
{
    HAL_UART_IRQHandler(&hlpuart1);
}

/**
 * @brief This function handles USART1 global interrupt (blocked by ST-LINK HMI BSP).
 */
void USART1_IRQHandler(void)
{
    /* USART1 is controlled by ST-LINK firmware, not available for user code */
}

/**
 * @brief This function handles GPDMA1 Channel 0 interrupt (SPI1 TX DMA).
 */
void GPDMA1_Channel0_IRQHandler(void)
{
    HAL_DMA_IRQHandler(&hdma_spi1_tx);
}

/**
 * @brief This function handles EXTI line 13 interrupt (PC13 - User Button).
 */
void EXTI13_IRQHandler(void)
{
    HAL_GPIO_EXTI_IRQHandler(GPIO_PIN_13);
}

