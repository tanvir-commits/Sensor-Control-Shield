"""Device registry - maps I2C addresses to possible device types."""

from typing import List, Dict, Tuple, Optional


# Device registry: address -> list of (device_name, plugin_class_name)
DEVICE_REGISTRY: Dict[int, List[Tuple[str, str]]] = {
    # ADC devices
    0x48: [("ADS1115", "ads1115"), ("ADS1015", "ads1015")],
    0x49: [("ADS1115", "ads1115"), ("ADS1015", "ads1015")],
    0x4A: [("ADS1115", "ads1115"), ("ADS1015", "ads1015")],
    0x4B: [("ADS1115", "ads1115"), ("ADS1015", "ads1015")],
    
    # OLED displays
    0x3C: [("SSD1306", "ssd1306"), ("SSD1309", "ssd1309"), ("SH1106", "sh1106")],
    0x3D: [("SSD1306", "ssd1306"), ("SSD1309", "ssd1309"), ("SH1106", "sh1106")],
    
    # IMU sensors
    0x68: [("MPU6050", "mpu6050"), ("MPU6500", "mpu6500"), ("DS3231", "ds3231")],
    0x69: [("MPU6050", "mpu6050"), ("MPU6500", "mpu6500")],
    
    # Pressure sensors
    0x76: [("BMP280", "bmp280"), ("BME280", "bme280")],
    0x77: [("BMP280", "bmp280"), ("BME280", "bme280")],
    
    # Temperature sensors
    0x18: [("MCP9808", "mcp9808")],
    0x19: [("MCP9808", "mcp9808")],
    
    # HAT EEPROM
    0x50: [("HAT EEPROM", None)],  # Pi internal, no plugin needed
}


class DeviceRegistry:
    """Registry for I2C device identification."""
    
    def __init__(self):
        self.registry = DEVICE_REGISTRY.copy()
    
    def lookup(self, address: int) -> List[Tuple[str, Optional[str]]]:
        """Look up possible devices for an I2C address.
        
        Args:
            address: I2C device address
            
        Returns:
            List of (device_name, plugin_name) tuples
            plugin_name is None if no plugin available
        """
        return self.registry.get(address, [("Unknown Device", None)])
    
    def register(self, address: int, device_name: str, plugin_name: Optional[str] = None):
        """Register a device for an address.
        
        Args:
            address: I2C device address
            device_name: Name of the device
            plugin_name: Name of plugin class (optional)
        """
        if address not in self.registry:
            self.registry[address] = []
        self.registry[address].append((device_name, plugin_name))


# Global registry instance
_registry_instance: Optional[DeviceRegistry] = None


def get_registry() -> DeviceRegistry:
    """Get the global device registry instance."""
    global _registry_instance
    if _registry_instance is None:
        _registry_instance = DeviceRegistry()
    return _registry_instance

