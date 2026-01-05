#ifndef UI_STYLING_H
#define UI_STYLING_H

#ifdef __cplusplus
extern "C" {
#endif

/**
 * Apply dark mode styling to all screens
 * This is called after ui_init() to preserve styling across re-exports
 * from SquareLine Studio.
 */
void ui_apply_dark_mode_styling(void);

#ifdef __cplusplus
} /*extern "C"*/
#endif

#endif /* UI_STYLING_H */

