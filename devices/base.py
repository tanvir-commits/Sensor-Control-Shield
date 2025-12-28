"""Base class for device plugins."""

from abc import ABC, abstractmethod
from typing import List, Dict, Optional, Any
from PySide6.QtWidgets import QWidget


class DevicePlugin(ABC):
    """Base class for all device plugins.
    
    Each device plugin must inherit from this class and implement
    the required methods.
    """
    
    # Device identification (must be set by subclass)
    addresses: List[int] = []  # I2C addresses this device uses
    name: str = ""  # Device name (e.g., "SSD1306")
    manufacturer: str = ""  # Manufacturer name
    description: str = ""  # Device description
    
    def __init__(self, bus: int, address: int):
        """Initialize device plugin.
        
        Args:
            bus: I2C bus number
            address: I2C device address
        """
        self.bus = bus
        self.address = address
    
    @abstractmethod
    def detect(self) -> bool:
        """Try to detect if this device is actually present.
        
        Returns:
            True if device is detected, False otherwise
        """
        pass
    
    def get_info(self) -> Dict[str, Any]:
        """Get device information.
        
        Returns:
            Dictionary with device information
        """
        return {
            "name": self.name,
            "manufacturer": self.manufacturer,
            "description": self.description,
            "address": f"0x{self.address:02X}",
            "bus": self.bus,
        }
    
    @abstractmethod
    def get_test_ui(self) -> Optional[QWidget]:
        """Get test interface widget for this device.
        
        Returns:
            QWidget with device-specific test interface, or None if not available
        """
        pass
    
    def get_status(self) -> str:
        """Get device status.
        
        Returns:
            Status string ("OK", "ERROR", etc.)
        """
        try:
            if self.detect():
                return "OK"
            return "NOT_DETECTED"
        except Exception:
            return "ERROR"

