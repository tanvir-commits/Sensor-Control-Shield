#include "button_driver.h"
#include <string.h>

/* Button GPIO pin/port arrays for easy iteration */
static const struct {
    GPIO_TypeDef *port;
    uint16_t pin;
} button_gpio[BUTTON_COUNT] = {
    [BUTTON_UP]    = {BUTTON_UP_PORT,    BUTTON_UP_PIN},
    [BUTTON_DOWN]  = {BUTTON_DOWN_PORT,  BUTTON_DOWN_PIN},
    [BUTTON_LEFT]  = {BUTTON_LEFT_PORT,  BUTTON_LEFT_PIN},
    [BUTTON_RIGHT] = {BUTTON_RIGHT_PORT, BUTTON_RIGHT_PIN},
    [BUTTON_PLAY]  = {BUTTON_PLAY_PORT,  BUTTON_PLAY_PIN},
};

/* Button state tracking */
static struct {
    button_state_t state;
    uint32_t press_time;
    uint32_t release_time;
    bool last_raw_state;
    bool uart_simulated;  // True if button state is from UART simulation
} button_data[BUTTON_COUNT];

/* System tick for debouncing */
extern uint32_t HAL_GetTick(void);

/**
 * @brief Initialize button driver
 * Configures GPIO pins as inputs with pull-up resistors
 */
bool button_driver_init(void)
{
    GPIO_InitTypeDef GPIO_InitStruct = {0};
    
    /* Enable GPIO clocks */
    __HAL_RCC_GPIOA_CLK_ENABLE();
    __HAL_RCC_GPIOC_CLK_ENABLE();
    
    /* Configure directional buttons (PA0-PA3) as inputs with pull-up */
    GPIO_InitStruct.Pin = BUTTON_UP_PIN | BUTTON_DOWN_PIN | BUTTON_LEFT_PIN | 
                          BUTTON_RIGHT_PIN;
    GPIO_InitStruct.Mode = GPIO_MODE_INPUT;
    GPIO_InitStruct.Pull = GPIO_PULLUP;  // Buttons pull to GND when pressed
    GPIO_InitStruct.Speed = GPIO_SPEED_FREQ_LOW;
    HAL_GPIO_Init(GPIOA, &GPIO_InitStruct);
    
    /* Configure PLAY button (PC13 - blue button on Nucleo) as input with pull-up */
    GPIO_InitStruct.Pin = BUTTON_PLAY_PIN;
    GPIO_InitStruct.Mode = GPIO_MODE_INPUT;
    GPIO_InitStruct.Pull = GPIO_PULLUP;  // PC13 button pulls to GND when pressed
    GPIO_InitStruct.Speed = GPIO_SPEED_FREQ_LOW;
    HAL_GPIO_Init(GPIOC, &GPIO_InitStruct);
    
    /* Initialize button state data */
    memset(button_data, 0, sizeof(button_data));
    
    /* Read initial state */
    uint32_t current_tick = HAL_GetTick();
    for (int i = 0; i < BUTTON_COUNT; i++) {
        /* PC13 button: pressed = LOW (GPIO_PIN_RESET), released = HIGH (GPIO_PIN_SET) */
        bool pressed = (HAL_GPIO_ReadPin(button_gpio[i].port, button_gpio[i].pin) == GPIO_PIN_RESET);
        button_data[i].last_raw_state = pressed;
        button_data[i].state = BUTTON_STATE_RELEASED;
        button_data[i].press_time = current_tick;
        button_data[i].release_time = current_tick;
        button_data[i].uart_simulated = false;
    }
    
    return true;
}

/**
 * @brief Read raw GPIO state (true = pressed, false = released)
 * Note: Pull-up configuration means pressed = LOW (GPIO_PIN_RESET)
 * If UART simulation is active, return simulated state instead
 */
static bool button_read_raw(button_id_t button)
{
    if (button >= BUTTON_COUNT) {
        return false;
    }
    
    /* If UART simulated, return simulated state */
    if (button_data[button].uart_simulated) {
        return (button_data[button].state == BUTTON_STATE_PRESSED || 
                button_data[button].state == BUTTON_STATE_HELD);
    }
    
    /* Otherwise read from GPIO */
    return HAL_GPIO_ReadPin(button_gpio[button].port, button_gpio[button].pin) == GPIO_PIN_RESET;
}

/**
 * @brief Update button states with debouncing
 * Call this periodically (e.g., in main loop or timer interrupt)
 */
void button_driver_update(void)
{
    uint32_t current_tick = HAL_GetTick();
    
    for (int i = 0; i < BUTTON_COUNT; i++) {
        bool raw_state = button_read_raw((button_id_t)i);
        bool last_state = button_data[i].last_raw_state;
        
        /* For UART simulated buttons, skip debounce and use state directly */
        if (button_data[i].uart_simulated) {
            /* UART simulated - state is already set by simulate_press/release */
            /* Just update last_raw_state to match */
            button_data[i].last_raw_state = raw_state;
            continue;  /* Skip debounce logic for simulated buttons */
        }
        
        if (raw_state != last_state) {
            /* State changed - start debounce timer */
            if (raw_state) {
                /* Button pressed */
                button_data[i].press_time = current_tick;
            } else {
                /* Button released */
                button_data[i].release_time = current_tick;
            }
        } else {
            /* State stable - check if debounce time has passed */
            if (raw_state) {
                /* Button is pressed */
                if (current_tick - button_data[i].press_time >= BUTTON_DEBOUNCE_MS) {
                    if (button_data[i].state == BUTTON_STATE_RELEASED) {
                        button_data[i].state = BUTTON_STATE_PRESSED;
                    } else {
                        button_data[i].state = BUTTON_STATE_HELD;
                    }
                }
            } else {
                /* Button is released */
                if (current_tick - button_data[i].release_time >= BUTTON_DEBOUNCE_MS) {
                    button_data[i].state = BUTTON_STATE_RELEASED;
                }
            }
        }
        
        button_data[i].last_raw_state = raw_state;
    }
}

/**
 * @brief Read button state (with debouncing)
 */
button_state_t button_driver_read(button_id_t button)
{
    if (button >= BUTTON_COUNT) {
        return BUTTON_STATE_RELEASED;
    }
    
    return button_data[button].state;
}

/**
 * @brief Check if button is currently pressed
 */
bool button_driver_is_pressed(button_id_t button)
{
    button_state_t state = button_driver_read(button);
    return (state == BUTTON_STATE_PRESSED || state == BUTTON_STATE_HELD);
}

/**
 * @brief Simulate button press via UART command
 * This allows testing without physical buttons
 * The button will stay pressed for a short time to allow LVGL to read it
 */
void button_driver_simulate_press(button_id_t button)
{
    if (button >= BUTTON_COUNT) {
        return;
    }
    
    uint32_t current_tick = HAL_GetTick();
    button_data[button].uart_simulated = true;
    button_data[button].press_time = current_tick - BUTTON_DEBOUNCE_MS;  // Pretend debounce already passed
    button_data[button].state = BUTTON_STATE_PRESSED;
    button_data[button].last_raw_state = true;
    /* Set state immediately so it's detected on next button_driver_update() */
}

/**
 * @brief Simulate button release via UART command
 */
void button_driver_simulate_release(button_id_t button)
{
    if (button >= BUTTON_COUNT) {
        return;
    }
    
    uint32_t current_tick = HAL_GetTick();
    button_data[button].uart_simulated = true;
    button_data[button].release_time = current_tick;
    button_data[button].state = BUTTON_STATE_RELEASED;
    button_data[button].last_raw_state = false;
}

