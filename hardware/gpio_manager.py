"""GPIO manager for LEDs and buttons."""

from hardware.platform import is_raspberry_pi
from PySide6.QtCore import Signal, QObject
from config.pins import LED1, LED2, LED3, LED4, BTN1, BTN2


class GPIOManager(QObject):
    """Simple GPIO manager - real on Pi, mock on PC."""
    
    def __init__(self):
        super().__init__()  # Initialize QObject
        self.is_pi = is_raspberry_pi()
        self.led_states = {1: False, 2: False, 3: False, 4: False}
        self.button_states = {1: False, 2: False}
        
        if self.is_pi:
            self._init_pi()
        else:
            self._init_mock()
    
    def _init_pi(self):
        """Initialize on Raspberry Pi."""
        try:
            from gpiozero import LED, Button
            self.leds = {
                1: LED(LED1),
                2: LED(LED2),
                3: LED(LED3),
                4: LED(LED4)
            }
            # Use minimal bounce_time for faster response (default is 0.01s = 10ms)
            self.buttons = {
                1: Button(BTN1, pull_up=True, bounce_time=None),
                2: Button(BTN2, pull_up=True, bounce_time=None)
            }
            # Set up button callbacks
            self.buttons[1].when_pressed = lambda: self._button_callback(1, True)
            self.buttons[1].when_released = lambda: self._button_callback(1, False)
            self.buttons[2].when_pressed = lambda: self._button_callback(2, True)
            self.buttons[2].when_released = lambda: self._button_callback(2, False)
        except ImportError:
            self._init_mock()
    
    def _init_mock(self):
        """Initialize mock (for PC)."""
        self.leds = None
        self.buttons = None
    
    def _button_callback(self, button_id: int, pressed: bool):
        """Button state change callback."""
        self.button_states[button_id] = pressed
    
    def set_led(self, led_id: int, state: bool):
        """Set LED state."""
        self.led_states[led_id] = state
        if self.is_pi and self.leds and led_id in self.leds:
            if state:
                self.leds[led_id].on()
            else:
                self.leds[led_id].off()
    
    def get_led(self, led_id: int) -> bool:
        """Get LED state."""
        return self.led_states.get(led_id, False)
    
    def get_button(self, button_id: int) -> bool:
        """Get button state - uses callback-updated state only."""
        # Always use callback state, never read hardware directly
                # Read hardware directly for fastest response
        if self.is_pi and self.buttons and button_id in self.buttons:
            return self.buttons[button_id].is_pressed
        return self.button_states.get(button_id, False)


