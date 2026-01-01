"""SSD1306/SSD1309/SH1106 display adapter."""

from typing import Tuple, Optional
from PIL import Image
from ...device_detector import DeviceInfo
from ..display_interface import DisplayInterface


class SSD1306Adapter(DisplayInterface):
    """Adapter for SSD1306, SSD1309, and SH1106 OLED displays.
    
    These displays use the same I2C protocol and driver, so one adapter
    handles all three controller chips.
    """
    
    def __init__(self):
        self.display = None
        self.device_info: Optional[DeviceInfo] = None
        self.width = 128
        self.height = 64
    
    def initialize(self, device_info: DeviceInfo) -> bool:
        """Initialize SSD1306 display."""
        try:
            import board
            import adafruit_ssd1306
            
            self.device_info = device_info
            i2c = board.I2C()
            
            # Try 128x64 first, fallback to 128x32
            try:
                self.display = adafruit_ssd1306.SSD1306_I2C(
                    128, 64, i2c, addr=device_info.address
                )
                self.width = 128
                self.height = 64
            except Exception:
                # Try 128x32
                try:
                    self.display = adafruit_ssd1306.SSD1306_I2C(
                        128, 32, i2c, addr=device_info.address
                    )
                    self.width = 128
                    self.height = 32
                except Exception as e:
                    print(f"SSD1306Adapter: Failed to initialize display: {e}")
                    return False
            
            # Clear display
            self.display.fill(0)
            self.display.show()
            
            return True
        
        except ImportError:
            print("SSD1306Adapter: adafruit_ssd1306 library not available")
            return False
        except Exception as e:
            print(f"SSD1306Adapter: Initialization error: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def show_image(self, image: Image.Image) -> None:
        """Display PIL Image on SSD1306."""
        if not self.display:
            raise RuntimeError("Display not initialized")
        
        try:
            # Ensure image matches display size
            if image.size != (self.width, self.height):
                # Use LANCZOS resampling if available, otherwise use default
                try:
                    image = image.resize((self.width, self.height), Image.Resampling.LANCZOS)
                except AttributeError:
                    # Fallback for older PIL versions
                    image = image.resize((self.width, self.height), Image.LANCZOS)
            
            # Ensure image is in '1' mode (1-bit monochrome)
            if image.mode != '1':
                image = image.convert('1')
            
            # Display image
            self.display.image(image)
            self.display.show()
        
        except Exception as e:
            print(f"SSD1306Adapter: Error showing image: {e}")
            raise
    
    def clear(self) -> None:
        """Clear display."""
        if not self.display:
            return
        
        try:
            self.display.fill(0)
            self.display.show()
        except Exception as e:
            print(f"SSD1306Adapter: Error clearing display: {e}")
    
    def get_size(self) -> Tuple[int, int]:
        """Get display dimensions."""
        return (self.width, self.height)
    
    def cleanup(self) -> None:
        """Cleanup resources."""
        try:
            if self.display:
                self.clear()
                # Note: adafruit_ssd1306 doesn't have explicit close,
                # but we clear the reference
                self.display = None
        except Exception as e:
            print(f"SSD1306Adapter: Error during cleanup: {e}")

