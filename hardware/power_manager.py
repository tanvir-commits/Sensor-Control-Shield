"""Power manager for sensor rail control."""

from hardware.platform import is_raspberry_pi
from config.pins import SENSOR_POWER


class PowerManager:
    """Simple power manager - real on Pi, mock on PC."""
    
    def __init__(self):
        self.is_pi = is_raspberry_pi()
        self.power_on = False
        self.gpio = None
        
        if self.is_pi:
            self._init_pi()
    
    def _init_pi(self):
        """Initialize on Raspberry Pi."""
        try:
            from gpiozero import OutputDevice
            self.gpio = OutputDevice(SENSOR_POWER)
        except ImportError:
            self.gpio = None
    
    def set_power(self, state: bool):
        """Set sensor power state."""
        self.power_on = state
        if self.is_pi and self.gpio:
            if state:
                self.gpio.on()
            else:
                self.gpio.off()
    
    def get_power(self) -> bool:
        """Get sensor power state."""
        return self.power_on


