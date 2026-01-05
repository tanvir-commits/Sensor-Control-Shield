##########################################################################################################################
# Makefile for STM32 GUI Project with LVGL
##########################################################################################################################

#######################################
# Target
#######################################
TARGET = stm32_gui

#######################################
# Building variables
#######################################
# Debug build?
DEBUG = 1
# Optimization level
OPT = -Og

#######################################
# Paths
#######################################
# Build path
BUILD_DIR = build

#######################################
# Source files
#######################################
# C sources
C_SOURCES =  \
src/main.c \
src/system/st7789_driver.c \
src/system/button_driver.c \
src/lvgl_port.c \
src/gui_config.c \
src/test_bitmap_12.c \
src/system_stm32u5xx.c \
src/stm32u5xx_it.c \
src/stm32u5xx_hal_msp.c \
lvgl/src/lv_init.c \
lvgl/src/display/lv_display.c \
lvgl/src/draw/lv_draw_buf.c \
lvgl/src/misc/lv_event.c \
lvgl/src/core/lv_group.c \
lvgl/src/indev/lv_indev.c \
lvgl/src/indev/lv_indev_scroll.c \
lvgl/src/core/lv_obj.c \
lvgl/src/core/lv_obj_class.c \
lvgl/src/core/lv_obj_draw.c \
lvgl/src/core/lv_obj_pos.c \
lvgl/src/core/lv_obj_scroll.c \
lvgl/src/core/lv_obj_style.c \
lvgl/src/core/lv_obj_style_gen.c \
lvgl/src/core/lv_obj_tree.c \
lvgl/src/core/lv_obj_event.c \
lvgl/src/core/lv_refr.c \
lvgl/src/themes/lv_theme.c \
lvgl/src/themes/default/lv_theme_default.c \
lvgl/src/layouts/lv_layout.c \
lvgl/src/layouts/flex/lv_flex.c \
lvgl/src/layouts/grid/lv_grid.c \
lvgl/src/libs/bin_decoder/lv_bin_decoder.c \
lvgl/src/draw/lv_draw.c \
lvgl/src/draw/lv_draw_arc.c \
lvgl/src/draw/lv_draw_image.c \
lvgl/src/draw/lv_draw_label.c \
lvgl/src/draw/lv_draw_line.c \
lvgl/src/draw/lv_draw_mask.c \
lvgl/src/draw/lv_draw_rect.c \
lvgl/src/draw/lv_draw_triangle.c \
lvgl/src/draw/lv_image_decoder.c \
lvgl/src/draw/sw/lv_draw_sw.c \
lvgl/src/draw/sw/lv_draw_sw_arc.c \
lvgl/src/draw/sw/blend/lv_draw_sw_blend.c \
lvgl/src/draw/sw/blend/lv_draw_sw_blend_to_rgb565.c \
lvgl/src/draw/sw/blend/lv_draw_sw_blend_to_rgb888.c \
lvgl/src/draw/sw/blend/lv_draw_sw_blend_to_argb8888.c \
lvgl/src/draw/sw/lv_draw_sw_triangle.c \
lvgl/src/draw/sw/lv_draw_sw_gradient.c \
lvgl/src/draw/sw/lv_draw_sw_img.c \
lvgl/src/draw/sw/lv_draw_sw_letter.c \
lvgl/src/draw/sw/lv_draw_sw_line.c \
lvgl/src/draw/sw/lv_draw_sw_fill.c \
lvgl/src/draw/sw/lv_draw_sw_border.c \
lvgl/src/draw/sw/lv_draw_sw_box_shadow.c \
lvgl/src/draw/sw/lv_draw_sw_mask.c \
lvgl/src/draw/sw/lv_draw_sw_mask_rect.c \
lvgl/src/draw/sw/lv_draw_sw_transform.c \
lvgl/src/font/lv_font.c \
lvgl/src/font/lv_font_dejavu_16_persian_hebrew.c \
lvgl/src/font/lv_font_fmt_txt.c \
lvgl/src/font/lv_binfont_loader.c \
lvgl/src/font/lv_font_montserrat_10.c \
lvgl/src/font/lv_font_montserrat_12.c \
lvgl/src/font/lv_font_montserrat_14.c \
lvgl/src/font/lv_font_montserrat_16.c \
lvgl/src/font/lv_font_montserrat_18.c \
lvgl/src/font/lv_font_montserrat_20.c \
lvgl/src/font/lv_font_montserrat_22.c \
lvgl/src/font/lv_font_montserrat_24.c \
lvgl/src/font/lv_font_montserrat_26.c \
lvgl/src/font/lv_font_montserrat_28.c \
lvgl/src/font/lv_font_montserrat_30.c \
lvgl/src/font/lv_font_montserrat_32.c \
lvgl/src/font/lv_font_montserrat_34.c \
lvgl/src/font/lv_font_montserrat_36.c \
lvgl/src/font/lv_font_montserrat_38.c \
lvgl/src/font/lv_font_montserrat_40.c \
lvgl/src/font/lv_font_montserrat_42.c \
lvgl/src/font/lv_font_montserrat_44.c \
lvgl/src/font/lv_font_montserrat_46.c \
lvgl/src/font/lv_font_montserrat_48.c \
lvgl/src/font/lv_font_montserrat_28_compressed.c \
lvgl/src/font/lv_font_simsun_16_cjk.c \
lvgl/src/font/lv_font_unscii_8.c \
lvgl/src/font/lv_font_unscii_16.c \
lvgl/src/misc/lv_anim.c \
lvgl/src/misc/lv_anim_timeline.c \
lvgl/src/misc/lv_area.c \
lvgl/src/misc/lv_array.c \
lvgl/src/misc/lv_palette.c \
lvgl/src/misc/cache/lv_cache.c \
lvgl/src/misc/cache/lv_cache_entry.c \
lvgl/src/misc/cache/lv_image_cache.c \
lvgl/src/misc/cache/_lv_cache_lru_rb.c \
lvgl/src/osal/lv_os_none.c \
lvgl/src/misc/lv_async.c \
lvgl/src/misc/lv_bidi.c \
lvgl/src/misc/lv_color.c \
lvgl/src/misc/lv_fs.c \
lvgl/src/misc/lv_ll.c \
lvgl/src/misc/lv_log.c \
lvgl/src/misc/lv_math.c \
lvgl/src/stdlib/lv_mem.c \
lvgl/src/stdlib/builtin/lv_mem_core_builtin.c \
lvgl/src/stdlib/builtin/lv_string_builtin.c \
lvgl/src/stdlib/builtin/lv_sprintf_builtin.c \
lvgl/src/misc/lv_style.c \
lvgl/src/misc/lv_style_gen.c \
lvgl/src/tick/lv_tick.c \
lvgl/src/misc/lv_templ.c \
lvgl/src/misc/lv_timer.c \
lvgl/src/misc/lv_tlsf.c \
lvgl/src/misc/lv_text.c \
lvgl/src/misc/lv_text_ap.c \
lvgl/src/misc/lv_utils.c \
lvgl/src/widgets/arc/lv_arc.c \
lvgl/src/widgets/bar/lv_bar.c \
lvgl/src/widgets/button/lv_button.c \
lvgl/src/widgets/buttonmatrix/lv_buttonmatrix.c \
lvgl/src/widgets/canvas/lv_canvas.c \
lvgl/src/widgets/calendar/lv_calendar.c \
lvgl/src/widgets/calendar/lv_calendar_header_arrow.c \
lvgl/src/widgets/calendar/lv_calendar_header_dropdown.c \
lvgl/src/widgets/chart/lv_chart.c \
lvgl/src/widgets/checkbox/lv_checkbox.c \
lvgl/src/widgets/dropdown/lv_dropdown.c \
lvgl/src/widgets/image/lv_image.c \
lvgl/src/widgets/keyboard/lv_keyboard.c \
lvgl/src/widgets/label/lv_label.c \
lvgl/src/widgets/led/lv_led.c \
lvgl/src/widgets/line/lv_line.c \
lvgl/src/widgets/list/lv_list.c \
lvgl/src/widgets/menu/lv_menu.c \
lvgl/src/widgets/msgbox/lv_msgbox.c \
lvgl/src/widgets/objx_templ/lv_objx_templ.c \
lvgl/src/widgets/roller/lv_roller.c \
lvgl/src/widgets/scale/lv_scale.c \
lvgl/src/widgets/slider/lv_slider.c \
lvgl/src/widgets/span/lv_span.c \
lvgl/src/widgets/spinbox/lv_spinbox.c \
lvgl/src/widgets/spinner/lv_spinner.c \
lvgl/src/widgets/switch/lv_switch.c \
lvgl/src/widgets/table/lv_table.c \
lvgl/src/widgets/tabview/lv_tabview.c \
lvgl/src/widgets/textarea/lv_textarea.c \
lvgl/src/widgets/tileview/lv_tileview.c \
lvgl/src/widgets/win/lv_win.c \
Drivers/STM32U5xx_HAL_Driver/Src/stm32u5xx_hal_uart.c \
Drivers/STM32U5xx_HAL_Driver/Src/stm32u5xx_hal_uart_ex.c \
Drivers/STM32U5xx_HAL_Driver/Src/stm32u5xx_hal.c \
Drivers/STM32U5xx_HAL_Driver/Src/stm32u5xx_hal_rcc.c \
Drivers/STM32U5xx_HAL_Driver/Src/stm32u5xx_hal_tim.c \
Drivers/STM32U5xx_HAL_Driver/Src/stm32u5xx_hal_tim_ex.c \
Drivers/STM32U5xx_HAL_Driver/Src/stm32u5xx_hal_rcc_ex.c \
Drivers/STM32U5xx_HAL_Driver/Src/stm32u5xx_hal_flash.c \
Drivers/STM32U5xx_HAL_Driver/Src/stm32u5xx_hal_flash_ex.c \
Drivers/STM32U5xx_HAL_Driver/Src/stm32u5xx_hal_gpio.c \
Drivers/STM32U5xx_HAL_Driver/Src/stm32u5xx_hal_pwr.c \
Drivers/STM32U5xx_HAL_Driver/Src/stm32u5xx_hal_pwr_ex.c \
Drivers/STM32U5xx_HAL_Driver/Src/stm32u5xx_hal_cortex.c \
Drivers/STM32U5xx_HAL_Driver/Src/stm32u5xx_hal_exti.c \
Drivers/STM32U5xx_HAL_Driver/Src/stm32u5xx_hal_dma.c \
Drivers/STM32U5xx_HAL_Driver/Src/stm32u5xx_hal_dma_ex.c \
Drivers/STM32U5xx_HAL_Driver/Src/stm32u5xx_hal_icache.c \
Drivers/STM32U5xx_HAL_Driver/Src/stm32u5xx_hal_spi.c \
Drivers/STM32U5xx_HAL_Driver/Src/stm32u5xx_hal_spi_ex.c

# SquareLine Studio UI files (updated for new export)
ifneq ($(wildcard ui/ui.c),)
C_SOURCES += ui/ui.c \
ui/ui_helpers.c \
ui/ui_styling.c \
ui/components/ui_comp_hook.c \
ui/components/ui_comp.c \
ui/screens/ui_Screen1.c \
ui/screens/ui_Screen2.c \
ui/screens/ui_Screen3.c \
ui/images/ui_img_12_png.c \
ui/images/ui_img_check_png.c \
ui/images/ui_img_5_png.c
endif

# ASM sources
ASM_SOURCES =  \
src/startup_stm32u545xx.s

#######################################
# Binaries
#######################################
PREFIX = arm-none-eabi-
ifdef GCC_PATH
CC = $(GCC_PATH)/$(PREFIX)gcc
AS = $(GCC_PATH)/$(PREFIX)gcc -x assembler-with-cpp
CP = $(GCC_PATH)/$(PREFIX)objcopy
SZ = $(GCC_PATH)/$(PREFIX)size
else
CC = $(PREFIX)gcc
AS = $(PREFIX)gcc -x assembler-with-cpp
CP = $(PREFIX)objcopy
SZ = $(PREFIX)size
endif
HEX = $(CP) -O ihex
BIN = $(CP) -O binary -S

#######################################
# CFLAGS
#######################################
# CPU
CPU = -mcpu=cortex-m33

# FPU
FPU = -mfpu=fpv5-sp-d16

# FLOAT-ABI
FLOAT-ABI = -mfloat-abi=hard

# MCU
MCU = $(CPU) -mthumb $(FPU) $(FLOAT-ABI)

# C defines
C_DEFS =  \
-DUSE_HAL_DRIVER \
-DSTM32U545xx

# Check if SquareLine Studio UI is exported and add define
ifneq ($(wildcard ui/ui.h),)
C_DEFS += -DUI_H
endif

# C includes
C_INCLUDES =  \
-Iinc \
-Iconfig \
-Isrc/system \
-Ilvgl \
-Ilvgl/src \
-Iui \
-IDrivers/STM32U5xx_HAL_Driver/Inc \
-IDrivers/STM32U5xx_HAL_Driver/Inc/Legacy \
-IDrivers/CMSIS/Device/ST/STM32U5xx/Include \
-IDrivers/CMSIS/Include

# Compile flags
CFLAGS = $(MCU) $(C_DEFS) $(C_INCLUDES) $(OPT) -Wall -fdata-sections -ffunction-sections

ifeq ($(DEBUG), 1)
CFLAGS += -g -gdwarf-2
endif

# Generate dependency information
CFLAGS += -MMD -MP -MF"$(@:%.o=%.d)"

#######################################
# LDFLAGS
#######################################
# Link script
LDSCRIPT = STM32U545RETX_FLASH.ld

# Libraries
LIBS = -lc -lm -lnosys
LIBDIR =
LDFLAGS = $(MCU) -specs=nano.specs -T$(LDSCRIPT) $(LIBDIR) $(LIBS) -Wl,-Map=$(BUILD_DIR)/$(TARGET).map,--cref -Wl,--gc-sections

# Default action: build all
all: $(BUILD_DIR)/$(TARGET).elf $(BUILD_DIR)/$(TARGET).hex $(BUILD_DIR)/$(TARGET).bin

#######################################
# Build steps
#######################################
# List of objects
OBJECTS = $(addprefix $(BUILD_DIR)/,$(notdir $(C_SOURCES:.c=.o)))
vpath %.c $(sort $(dir $(C_SOURCES)))
# List of ASM program objects
OBJECTS += $(addprefix $(BUILD_DIR)/,$(notdir $(ASM_SOURCES:.s=.o)))
vpath %.s $(sort $(dir $(ASM_SOURCES)))

$(BUILD_DIR)/%.o: %.c Makefile | $(BUILD_DIR)
	$(CC) -c $(CFLAGS) -Wa,-a,-ad,-alms=$(BUILD_DIR)/$(notdir $(<:.c=.lst)) $< -o $@

$(BUILD_DIR)/%.o: %.s Makefile | $(BUILD_DIR)
	$(AS) -c $(CFLAGS) $< -o $@

$(BUILD_DIR)/$(TARGET).elf: $(OBJECTS) Makefile
	$(CC) $(OBJECTS) $(LDFLAGS) -o $@
	$(SZ) $@

$(BUILD_DIR)/%.hex: $(BUILD_DIR)/%.elf | $(BUILD_DIR)
	$(HEX) $< $@

$(BUILD_DIR)/%.bin: $(BUILD_DIR)/%.elf | $(BUILD_DIR)
	$(BIN) $< $@

$(BUILD_DIR):
	mkdir $@

#######################################
# Flash and debug
#######################################
# Flash using OpenOCD
flash: $(BUILD_DIR)/$(TARGET).elf
	openocd -f interface/stlink.cfg -f target/stm32u5x.cfg -c "program $(BUILD_DIR)/$(TARGET).elf verify reset exit"

# Flash using STM32CubeProgrammer
flash-stm32prog: $(BUILD_DIR)/$(TARGET).bin
	@if command -v STM32_Programmer_CLI >/dev/null 2>&1; then \
		STM32_Programmer_CLI -c port=SWD -w $(BUILD_DIR)/$(TARGET).bin 0x08000000 -v -rst; \
	else \
		echo "STM32CubeProgrammer not found. Install from: https://www.st.com/en/development-tools/stm32cubeprog.html"; \
		echo "Or use: make flash (requires OpenOCD)"; \
	fi

# Clean
clean:
	-rm -fR $(BUILD_DIR)

#######################################
# Dependencies
#######################################
-include $(wildcard $(BUILD_DIR)/*.d)

# *** EOF ***

