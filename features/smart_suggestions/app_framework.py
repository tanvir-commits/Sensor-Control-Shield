"""App framework - base class for suggested apps."""

from abc import ABC, abstractmethod
from typing import Optional, List
from PySide6.QtWidgets import QWidget
from PySide6.QtCore import QTimer
from .device_detector import DeviceInfo
from .app_manager import AppManager


class BaseApp(ABC):
    """Base class for all suggested apps."""
    
    def __init__(self):
        self.hardware = None
        self.devices: List[DeviceInfo] = []
        self.running = False
        self.update_timer: Optional[QTimer] = None
        self.update_interval = 50  # milliseconds (20 Hz default)
        self.app_manager = AppManager()
    
    def start(self, hardware, devices: List[DeviceInfo]) -> bool:
        """Start the app with given hardware and devices.
        
        Args:
            hardware: Hardware manager
            devices: List of DeviceInfo objects
            
        Returns:
            True if started successfully, False otherwise
        """
        try:
            self.hardware = hardware
            self.devices = devices
            
            # Call subclass initialization
            if not self._initialize():
                return False
            
            # Register with app manager (stops other apps first)
            self.app_manager.register_app(self)
            
            # Start update timer
            self.update_timer = QTimer()
            self.update_timer.timeout.connect(self.update)
            self.update_timer.start(self.update_interval)
            
            self.running = True
            return True
        
        except Exception as e:
            print(f"Error starting app {self.__class__.__name__}: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def stop(self) -> None:
        """Stop the app and cleanup."""
        try:
            # Set running to False FIRST to prevent any update() calls from continuing
            self.running = False
            
            # Stop update timer immediately and disconnect all signals
            if self.update_timer:
                self.update_timer.stop()
                try:
                    self.update_timer.timeout.disconnect()  # Disconnect signal to prevent any pending calls
                except:
                    pass  # May already be disconnected
                self.update_timer = None
            
            # Small delay to ensure any in-flight update() completes
            import time
            time.sleep(0.1)  # Increased delay
            
            # Call subclass cleanup (which should clear display)
            self._cleanup()
            
            # Unregister from app manager
            self.app_manager.unregister_app(self)
        
        except Exception as e:
            print(f"Error stopping app {self.__class__.__name__}: {e}")
    
    @abstractmethod
    def _initialize(self) -> bool:
        """Initialize the app. Subclass must implement.
        
        Returns:
            True if initialization successful
        """
        pass
    
    def _cleanup(self) -> None:
        """Cleanup the app. Subclass can override."""
        pass
    
    @abstractmethod
    def update(self) -> None:
        """Periodic update. Subclass must implement.
        
        Called by timer at update_interval rate.
        """
        pass
    
    def get_ui(self) -> Optional[QWidget]:
        """Get optional control UI for the app.
        
        Returns:
            QWidget with app controls, or None if no UI
        """
        return None
    
    def is_running(self) -> bool:
        """Check if app is running.
        
        Returns:
            True if running
        """
        return self.running
    
    def find_device(self, category: str) -> Optional[DeviceInfo]:
        """Find a device by category.
        
        Args:
            category: Device category (IMU, DISPLAY, etc.)
            
        Returns:
            DeviceInfo if found, None otherwise
        """
        for device in self.devices:
            if device.category == category:
                return device
        return None
    
    def find_devices(self, category: str) -> List[DeviceInfo]:
        """Find all devices by category.
        
        Args:
            category: Device category
            
        Returns:
            List of DeviceInfo objects
        """
        return [d for d in self.devices if d.category == category]

