#ifndef SD_CARD_H
#define SD_CARD_H

#include "main.h"
#include <stdbool.h>
#include <stdint.h>

/* SD Card Pin Definitions - Arduino Shield uses SPI1 (D10-D13) */
/* D10 on NUCLEO-U545RE-Q maps to PC9 (per user manual UM3062) */
#define SD_CS_PIN          GPIO_PIN_9
#define SD_CS_PORT         GPIOC
#define SD_SPI             SPI1

/* SD Card Commands */
#define CMD0    0   /* GO_IDLE_STATE */
#define CMD8    8   /* SEND_IF_COND */
#define CMD17   17  /* READ_SINGLE_BLOCK */
#define CMD24   24  /* WRITE_BLOCK */
#define CMD55   55  /* APP_CMD */
#define CMD58   58  /* READ_OCR */
#define ACMD41  41  /* SD_SEND_OP_COND */

/* SD Card Response Types */
#define R1_IDLE_STATE      0x01
#define R1_ILLEGAL_COMMAND 0x04

/* Function Prototypes */
bool SD_Init(void);
bool SD_ReadBlock(uint32_t block_addr, uint8_t *buffer);
bool SD_WriteBlock(uint32_t block_addr, const uint8_t *buffer);
bool SD_IsPresent(void);
const char* SD_GetStatusString(void);

/* Internal SPI Functions */
void SD_CS_Low(void);
void SD_CS_High(void);
uint8_t SD_SPI_Transfer(uint8_t data);
bool SD_SendCommand(uint8_t cmd, uint32_t arg, uint8_t *response);

#endif /* SD_CARD_H */

