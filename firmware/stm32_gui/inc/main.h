/**
 * @file main.h
 * @brief Header for main.c file
 */

#ifndef __MAIN_H
#define __MAIN_H

#ifdef __cplusplus
extern "C" {
#endif

#include "stm32u5xx_hal.h"
#include "system_stm32u5xx.h"

/* Exported types */
extern UART_HandleTypeDef hlpuart1;
extern SPI_HandleTypeDef hspi1;

/* Exported constants */
/* Exported macro */
/* Exported functions prototypes */
void Error_Handler(void);

#ifdef __cplusplus
}
#endif

#endif /* __MAIN_H */

