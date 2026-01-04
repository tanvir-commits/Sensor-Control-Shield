#include "lvgl_port.h"
#include "st7789_driver.h"
#include "main.h"
#include "lvgl.h"
#include <string.h>

/* External SPI handle */
extern SPI_HandleTypeDef hspi1;

/* Display buffer - partial buffer strategy (1/10 of screen) */
#define DISP_BUF_SIZE (LVGL_DISPLAY_WIDTH * 32)  // 240 * 32 = 7680 pixels = 15360 bytes
static lv_color_t disp_buf_1[DISP_BUF_SIZE];
static lv_color_t disp_buf_2[DISP_BUF_SIZE];

/* Display handle */
static lv_display_t *display;

/**
 * @brief Flush wait callback - called by LVGL when it needs to wait for flush to complete
 * This ensures proper synchronization between LVGL and display driver
 */
static void flush_wait_cb(lv_display_t *disp)
{
    /* Wait for any pending SPI transactions to complete
     * In our case, flush is synchronous, so this is just a safety check */
    while (hspi1.State != HAL_SPI_STATE_READY) {
        /* Wait for SPI to be ready */
    }
    /* Ensure CS is high (transaction complete) */
    ST7789_CS_High();
}

/**
 * @brief Display flush callback - called by LVGL when display needs updating
 * Optimized to send pixel data in bulk using SPI
 * IMPORTANT: This function must be called from the same context as lv_timer_handler()
 * (i.e., from main loop, not from interrupt)
 */
static void disp_flush(lv_display_t *disp, const lv_area_t *area, uint8_t *px_map)
{
    /* Bounds checking - clamp to display dimensions */
    int32_t x1 = area->x1;
    int32_t y1 = area->y1;
    int32_t x2 = area->x2;
    int32_t y2 = area->y2;
    
    /* Ensure coordinates are within display bounds */
    if (x1 < 0) x1 = 0;
    if (y1 < 0) y1 = 0;
    if (x2 >= LVGL_DISPLAY_WIDTH) x2 = LVGL_DISPLAY_WIDTH - 1;
    if (y2 >= LVGL_DISPLAY_HEIGHT) y2 = LVGL_DISPLAY_HEIGHT - 1;
    
    /* Check for valid area */
    if (x1 > x2 || y1 > y2 || x2 < 0 || y2 < 0) {
        /* Invalid area - just mark as done */
        lv_display_flush_ready(disp);
        return;
    }
    
    /* CRITICAL: Ensure CS is HIGH before starting new transaction
     * This prevents overlapping transactions from corrupting the display */
    ST7789_CS_High();
    HAL_Delay(1);  // Small delay to ensure CS is stable
    
    /* Calculate pixel count for this area */
    uint32_t area_width = x2 - x1 + 1;
    uint32_t area_height = y2 - y1 + 1;
    uint32_t pixel_count = area_width * area_height;
    uint32_t byte_count = pixel_count * 2;  /* RGB565 = 2 bytes per pixel */
    
    /* Set address window (this leaves CS low and DC high after RAMWR) */
    ST7789_SetAddrWindow((uint16_t)x1, (uint16_t)y1, (uint16_t)x2, (uint16_t)y2);
    
    /* CRITICAL: Original working code swaps bytes from [LSB, MSB] to [MSB, LSB]
     * With LV_COLOR_16_SWAP=0, LVGL provides [LSB, MSB] format (same as original bitmaps)
     * We MUST swap bytes to [MSB, LSB] to match what ST7789_DrawImageBytes does
     * 
     * In PARTIAL mode, px_map points directly to the area being updated (not full screen)
     * Process in row chunks to avoid large static buffer */
    const uint8_t *src = (const uint8_t*)px_map;
    static uint8_t swap_buffer[240 * 2];  // Buffer for one row max (240 pixels * 2 bytes = 480 bytes)
    uint32_t area_stride = area_width * 2;  // Bytes per row in source
    
    /* Send data row by row */
    for (uint32_t row = 0; row < area_height; row++) {
        /* Swap bytes for this row */
        for (uint32_t col = 0; col < area_width; col++) {
            uint32_t src_idx = col * 2;
            uint32_t dst_idx = col * 2;
            swap_buffer[dst_idx] = src[src_idx + 1];      // MSB
            swap_buffer[dst_idx + 1] = src[src_idx];      // LSB
        }
        
        /* Send this row */
        HAL_SPI_Transmit(&hspi1, swap_buffer, area_width * 2, 1000);
        
        /* Move to next row in source buffer */
        src += area_stride;
    }
    
    /* Complete the transaction - raise CS */
    ST7789_CS_High();
    
    /* Small delay to ensure CS signal is stable */
    HAL_Delay(1);
    
    /* Inform LVGL that flushing is done - this must be called after data is sent */
    lv_display_flush_ready(disp);
}

/**
 * @brief Initialize LVGL port layer
 */
bool lvgl_port_init(void)
{
    /* Initialize LVGL */
    lv_init();
    
    /* Initialize display */
    display = lv_display_create(LVGL_DISPLAY_WIDTH, LVGL_DISPLAY_HEIGHT);
    if (display == NULL) {
        return false;
    }
    
    /* Set display buffer - use PARTIAL mode with very large single buffer (almost full screen)
     * This minimizes partial refresh calls while staying within RAM limits
     * 240 * 280 = 67,200 pixels = 134,400 bytes (single buffer fits in 256KB RAM)
     * This covers 87.5% of screen height, dramatically reducing refresh artifacts
     * Using single buffer to save RAM - LVGL will wait for flush to complete
     */
    #define DISP_BUF_SIZE_LARGE (LVGL_DISPLAY_WIDTH * 280)  // 240 * 280 = 67,200 pixels = 134,400 bytes
    static lv_color_t disp_buf_large[DISP_BUF_SIZE_LARGE];
    lv_display_set_buffers(display, disp_buf_large, NULL, sizeof(disp_buf_large), LV_DISPLAY_RENDER_MODE_PARTIAL);
    
    /* Set flush callback */
    lv_display_set_flush_cb(display, disp_flush);
    
    /* Set flush wait callback for proper synchronization
     * This ensures LVGL waits for flush to complete before sending next area */
    lv_display_set_flush_wait_cb(display, flush_wait_cb);
    
    return true;
}

/**
 * @brief Update LVGL tick - call this periodically (e.g., from SysTick)
 */
void lvgl_port_tick(void)
{
    lv_tick_inc(1);  // Increment by 1ms
}
