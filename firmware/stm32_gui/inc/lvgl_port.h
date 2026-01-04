#ifndef LVGL_PORT_H
#define LVGL_PORT_H

#include <stdbool.h>

/* LVGL display dimensions */
#define LVGL_DISPLAY_WIDTH  240
#define LVGL_DISPLAY_HEIGHT 320

/* Function prototypes */
bool lvgl_port_init(void);
void lvgl_port_tick(void);

#endif /* LVGL_PORT_H */
