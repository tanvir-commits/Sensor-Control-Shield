/**
 * @file ui_styling.c
 * @brief Dark mode styling for SquareLine Studio UI screens
 * 
 * This file applies dark mode styling to all screens after initialization.
 * It's kept separate from generated SquareLine Studio files so it won't be
 * overwritten when re-exporting from SquareLine Studio.
 */

#include "ui.h"
#include "ui_styling.h"
#include "screens/ui_Screen1.h"
#include "screens/ui_Screen2.h"
#include "screens/ui_Screen3.h"

/**
 * Apply dark mode styling to all screens
 * This is called after ui_init() to preserve styling across re-exports
 */
void ui_apply_dark_mode_styling(void)
{
    /* Screen1 - black background */
    if (ui_Screen1 != NULL) {
        lv_obj_set_style_bg_color(ui_Screen1, lv_color_hex(0x000000), LV_PART_MAIN | LV_STATE_DEFAULT);
        lv_obj_set_style_bg_opa(ui_Screen1, LV_OPA_COVER, LV_PART_MAIN | LV_STATE_DEFAULT);
    }
    
    /* Screen2 - black background, white text */
    if (ui_Screen2 != NULL) {
        lv_obj_set_style_bg_color(ui_Screen2, lv_color_hex(0x000000), LV_PART_MAIN | LV_STATE_DEFAULT);
        lv_obj_set_style_bg_opa(ui_Screen2, LV_OPA_COVER, LV_PART_MAIN | LV_STATE_DEFAULT);
        
        /* White text for labels - these are declared in ui_Screen2.c */
        extern lv_obj_t * ui_Detecting_Cassette_;
        extern lv_obj_t * ui_Please_Wait;
        extern lv_obj_t * ui_Check_Icon;
        
        if (ui_Detecting_Cassette_ != NULL) {
            lv_obj_set_style_text_color(ui_Detecting_Cassette_, lv_color_hex(0xFFFFFF), LV_PART_MAIN | LV_STATE_DEFAULT);
        }
        if (ui_Please_Wait != NULL) {
            lv_obj_set_style_text_color(ui_Please_Wait, lv_color_hex(0xFFFFFF), LV_PART_MAIN | LV_STATE_DEFAULT);
        }
        if (ui_Check_Icon != NULL) {
            lv_obj_add_flag(ui_Check_Icon, LV_OBJ_FLAG_HIDDEN);  // Hide checkmark initially
        }
    }
    
    /* Screen3 - black background */
    if (ui_Screen3 != NULL) {
        lv_obj_set_style_bg_color(ui_Screen3, lv_color_hex(0x000000), LV_PART_MAIN | LV_STATE_DEFAULT);
        lv_obj_set_style_bg_opa(ui_Screen3, LV_OPA_COVER, LV_PART_MAIN | LV_STATE_DEFAULT);
    }
}

