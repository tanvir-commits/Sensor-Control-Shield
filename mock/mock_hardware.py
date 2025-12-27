"""Mock hardware data generators for UI design.

This module provides fake hardware data so we can design and refine
the UI without needing actual hardware connected.
"""

import random
import time
from typing import List, Dict, Optional


class MockGPIO:
    """Mock GPIO manager for LEDs and buttons."""
    
    def __init__(self):
        self.led_states = {1: False, 2: False, 3: False, 4: False}
        self.button_states = {1: False, 2: False}
        self._last_button_change = {1: 0, 2: 0}
    
    def set_led(self, led_id: int, state: bool) -> None:
        """Set LED state."""
        if 1 <= led_id <= 4:
            self.led_states[led_id] = state
    
    def get_led(self, led_id: int) -> bool:
        """Get LED state."""
        return self.led_states.get(led_id, False)
    
    def get_button(self, button_id: int) -> bool:
        """Get button state (simulate occasional presses)."""
        # Simulate random button presses occasionally
        now = time.time()
        if now - self._last_button_change[button_id] > 3.0:
            if random.random() < 0.3:  # 30% chance to toggle
                self.button_states[button_id] = not self.button_states[button_id]
                self._last_button_change[button_id] = now
        return self.button_states[button_id]


class MockADC:
    """Mock ADC manager for analog voltage readings."""
    
    def __init__(self):
        self.base_voltages = {
            0: 1.234,
            1: 3.301,
            2: 0.012,
            3: 5.002
        }
        self._time_offset = time.time()
    
    def read_channel(self, channel: int) -> Optional[float]:
        """Read ADC channel with simulated noise."""
        if channel not in self.base_voltages:
            return None
        
        # Add slight variation to simulate real readings
        noise = (random.random() - 0.5) * 0.01  # ±5mV noise
        # Add slow sine wave variation
        time_var = 0.002 * (1 + 0.1 * (time.time() - self._time_offset))
        variation = 0.001 * (random.random() - 0.5)
        
        voltage = self.base_voltages[channel] + noise + variation
        return max(0.0, min(5.0, voltage))  # Clamp to 0-5V
    
    def read_all_channels(self) -> Dict[int, Optional[float]]:
        """Read all 4 ADC channels."""
        return {i: self.read_channel(i) for i in range(4)}


class MockI2C:
    """Mock I2C scanner."""
    
    def __init__(self):
        self.devices = [0x48]  # ADS1115 address
        self._scan_count = 0
    
    def scan(self) -> List[int]:
        """Scan I2C bus (simulate finding devices)."""
        self._scan_count += 1
        # Occasionally "find" an extra device
        if self._scan_count % 5 == 0 and random.random() < 0.3:
            return [0x48, 0x68]  # ADS1115 + maybe an IMU
        return self.devices.copy()
    
    def get_status(self) -> str:
        """Get I2C bus status."""
        return "OK"


class MockSPI:
    """Mock SPI tester."""
    
    def __init__(self):
        self.enabled = True
        self._test_count = 0
    
    def test(self) -> Dict[str, str]:
        """Run SPI test."""
        self._test_count += 1
        return {
            "enabled": "SPI enabled",
            "activity": "Clock/MOSI activity detected",
            "miso": "MISO response detected" if self._test_count % 2 == 0 else "MISO response not detected",
            "status": "OK" if self._test_count % 2 == 0 else "NOT VERIFIED"
        }


class MockPower:
    """Mock power manager for sensor rail."""
    
    def __init__(self):
        self.power_on = False
    
    def set_power(self, state: bool) -> None:
        """Set sensor power state."""
        self.power_on = state
    
    def get_power(self) -> bool:
        """Get sensor power state."""
        return self.power_on


class MockHardware:
    """Container for all mock hardware managers."""
    
    def __init__(self):
        self.gpio = MockGPIO()
        self.adc = MockADC()
        self.i2c = MockI2C()
        self.spi = MockSPI()
        self.power = MockPower()

