"""Display interface - abstract base class for display adapters."""

from abc import ABC, abstractmethod
from typing import Tuple
from PIL import Image
from ..device_detector import DeviceInfo


class DisplayInterface(ABC):
    """Abstract interface for display adapters.
    
    All display adapters must implement this interface to work with apps.
    This allows apps to work with any supported display controller without
    knowing the specific implementation details.
    """
    
    @abstractmethod
    def initialize(self, device_info: DeviceInfo) -> bool:
        """Initialize the display with the given device info.
        
        Args:
            device_info: DeviceInfo object containing bus, address, etc.
            
        Returns:
            True if initialization successful, False otherwise
        """
        pass
    
    @abstractmethod
    def show_image(self, image: Image.Image) -> None:
        """Display a PIL Image on the display.
        
        Args:
            image: PIL Image object (will be converted to display format)
        """
        pass
    
    @abstractmethod
    def clear(self) -> None:
        """Clear the display (fill with black/off)."""
        pass
    
    @abstractmethod
    def get_size(self) -> Tuple[int, int]:
        """Get display dimensions.
        
        Returns:
            Tuple of (width, height) in pixels
        """
        pass
    
    @abstractmethod
    def cleanup(self) -> None:
        """Cleanup resources (close connections, etc.)."""
        pass


