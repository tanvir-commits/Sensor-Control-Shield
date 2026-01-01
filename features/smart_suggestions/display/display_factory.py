"""Display factory - creates appropriate display adapter based on device type."""

from typing import Optional
from ..device_detector import DeviceInfo
from .display_interface import DisplayInterface
from .adapters.ssd1306_adapter import SSD1306Adapter


class DisplayFactory:
    """Factory for creating display adapters based on device type."""
    
    @staticmethod
    def create_display(device_info: DeviceInfo) -> Optional[DisplayInterface]:
        """Create appropriate display adapter for the given device.
        
        Args:
            device_info: DeviceInfo object with device name and address
            
        Returns:
            DisplayInterface instance, or None if device type not supported
        """
        device_name = device_info.device_name.upper()
        
        # SSD1306 family (SSD1306, SSD1309, SH1106)
        if device_name in ["SSD1306", "SSD1309", "SH1106"]:
            adapter = SSD1306Adapter()
            if adapter.initialize(device_info):
                return adapter
            else:
                print(f"DisplayFactory: Failed to initialize {device_name} adapter")
                return None
        
        # Future: Add other display types here
        # elif device_name in ["ST7735", "ST7735R"]:
        #     return ST7735Adapter()
        # elif device_name in ["ILI9341"]:
        #     return ILI9341Adapter()
        
        # Unknown display type
        print(f"DisplayFactory: Unknown display type: {device_name}")
        print(f"  Falling back to SSD1306 adapter (may not work)")
        
        # Fallback: Try SSD1306 adapter (might work for compatible displays)
        try:
            adapter = SSD1306Adapter()
            if adapter.initialize(device_info):
                return adapter
        except Exception as e:
            print(f"DisplayFactory: Fallback to SSD1306 failed: {e}")
        
        return None


