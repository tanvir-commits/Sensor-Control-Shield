#ifndef BUTTON_DRIVER_H
#define BUTTON_DRIVER_H

#include "main.h"
#include <stdint.h>
#include <stdbool.h>

/* Button definitions - 5 buttons: Up, Down, Left, Right, Play */
typedef enum {
    BUTTON_UP = 0,
    BUTTON_DOWN,
    BUTTON_LEFT,
    BUTTON_RIGHT,
    BUTTON_PLAY,
    BUTTON_COUNT
} button_id_t;

/* Button state */
typedef enum {
    BUTTON_STATE_RELEASED = 0,
    BUTTON_STATE_PRESSED,
    BUTTON_STATE_HELD
} button_state_t;

/* Button pin definitions - TODO: Update with actual GPIO pins */
#define BUTTON_UP_PIN       GPIO_PIN_0
#define BUTTON_UP_PORT      GPIOA
#define BUTTON_DOWN_PIN     GPIO_PIN_1
#define BUTTON_DOWN_PORT    GPIOA
#define BUTTON_LEFT_PIN     GPIO_PIN_2
#define BUTTON_LEFT_PORT    GPIOA
#define BUTTON_RIGHT_PIN    GPIO_PIN_3
#define BUTTON_RIGHT_PORT   GPIOA
#define BUTTON_PLAY_PIN     GPIO_PIN_13
#define BUTTON_PLAY_PORT    GPIOC

/* Debounce time in milliseconds */
#define BUTTON_DEBOUNCE_MS  50

/* Function prototypes */
bool button_driver_init(void);
button_state_t button_driver_read(button_id_t button);
bool button_driver_is_pressed(button_id_t button);
void button_driver_update(void);  // Call periodically to update button states

/* UART simulation functions - for testing without physical buttons */
void button_driver_simulate_press(button_id_t button);
void button_driver_simulate_release(button_id_t button);

#endif /* BUTTON_DRIVER_H */

