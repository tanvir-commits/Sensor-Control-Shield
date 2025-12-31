"""Device detector - scans I2C buses and categorizes devices."""

from typing import List, Tuple, Optional, Dict
from dataclasses import dataclass
from hardware.i2c_scanner import I2CScanner
from devices.registry import get_registry


@dataclass
class DeviceInfo:
    """Information about a detected device."""
    bus: int
    address: int
    device_name: str
    category: Optional[str]  # IMU, DISPLAY, TEMP_SENSOR, etc.
    plugin_name: Optional[str] = None


# Device category mapping
DEVICE_CATEGORIES: Dict[str, List[str]] = {
    "IMU": ["MPU6050", "MPU6500"],
    "DISPLAY": ["SSD1306", "SSD1309", "SH1106"],
    "TEMP_SENSOR": ["MCP9808"],
    "PRESSURE_SENSOR": ["BMP280", "BME280"],
    "ADC": ["ADS1115", "ADS1015"],
}


class DeviceDetector:
    """Detects and categorizes I2C devices."""
    
    def __init__(self):
        self.registry = get_registry()
    
    def scan_all_devices(self, hardware=None) -> List[DeviceInfo]:
        """Scan all I2C buses and return categorized device list.
        
        Args:
            hardware: Hardware manager (optional, uses I2CScanner if not provided)
            
        Returns:
            List of DeviceInfo objects
        """
        devices = []
        
        try:
            # Scan all available I2C buses
            if hardware and hasattr(hardware, 'i2c'):
                # Use hardware's I2C scanner if available
                all_buses = I2CScanner.scan_all_buses()
            else:
                # Use I2CScanner directly
                all_buses = I2CScanner.scan_all_buses()
            
            # Process each bus
            for bus_num, addresses in all_buses.items():
                for address in addresses:
                    # Skip HAT EEPROM (internal Pi device)
                    if address == 0x50:
                        continue
                    
                    # Look up device in registry
                    suggestions = self.registry.lookup(address)
                    if suggestions:
                        device_name, plugin_name = suggestions[0]
                        
                        # Categorize device
                        category = self.categorize_device(device_name, address)
                        
                        device_info = DeviceInfo(
                            bus=bus_num,
                            address=address,
                            device_name=device_name,
                            category=category,
                            plugin_name=plugin_name
                        )
                        devices.append(device_info)
                    else:
                        # Unknown device
                        device_info = DeviceInfo(
                            bus=bus_num,
                            address=address,
                            device_name="Unknown Device",
                            category=None,
                            plugin_name=None
                        )
                        devices.append(device_info)
        
        except Exception as e:
            print(f"Error scanning devices: {e}")
            # Return empty list on error
        
        return devices
    
    def categorize_device(self, device_name: str, address: int) -> Optional[str]:
        """Categorize a device by name.
        
        Args:
            device_name: Name of the device
            address: I2C address
            
        Returns:
            Category string (IMU, DISPLAY, etc.) or None
        """
        # Check each category
        for category, device_names in DEVICE_CATEGORIES.items():
            if device_name in device_names:
                return category
        
        # Special case: Check address for known devices
        if address in [0x68, 0x69]:
            # IMU addresses
            if "MPU" in device_name.upper() or "IMU" in device_name.upper():
                return "IMU"
        
        if address in [0x3C, 0x3D]:
            # Display addresses
            if "SSD" in device_name.upper() or "SH" in device_name.upper():
                return "DISPLAY"
        
        return None
    
    def get_device_categories(self, devices: List[DeviceInfo]) -> List[str]:
        """Extract unique categories from device list.
        
        Args:
            devices: List of DeviceInfo objects
            
        Returns:
            List of unique category strings
        """
        categories = set()
        for device in devices:
            if device.category:
                categories.add(device.category)
        return sorted(list(categories))

