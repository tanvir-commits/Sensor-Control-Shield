"""Safe plugin loader for device plugins."""

import importlib
import os
from typing import Optional, List, Dict, Any
from .base import DevicePlugin
from .registry import get_registry


class DeviceLoader:
    """Safely loads device plugins with error handling."""
    
    def __init__(self):
        self.registry = get_registry()
        self.loaded_plugins: Dict[str, type] = {}
        self.failed_plugins: List[str] = []
    
    def load_plugin(self, plugin_name: str) -> Optional[type]:
        """Load a device plugin by name.
        
        Args:
            plugin_name: Name of plugin module (e.g., "ssd1306")
            
        Returns:
            Plugin class if loaded successfully, None otherwise
        """
        if plugin_name is None:
            return None
        
        # Check if already loaded
        if plugin_name in self.loaded_plugins:
            return self.loaded_plugins[plugin_name]
        
        # Check if previously failed
        if plugin_name in self.failed_plugins:
            return None
        
        try:
            # Try to import plugin module
            module = importlib.import_module(f"devices.{plugin_name}")
            
            # Find DevicePlugin subclass
            plugin_class = None
            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                if (isinstance(attr, type) and 
                    issubclass(attr, DevicePlugin) and 
                    attr != DevicePlugin):
                    plugin_class = attr
                    break
            
            if plugin_class is None:
                raise ValueError(f"No DevicePlugin subclass found in devices.{plugin_name}")
            
            # Validate plugin
            if not hasattr(plugin_class, 'addresses'):
                raise ValueError(f"Plugin {plugin_name} missing 'addresses' attribute")
            if not hasattr(plugin_class, 'name'):
                raise ValueError(f"Plugin {plugin_name} missing 'name' attribute")
            
            # Cache successful load
            self.loaded_plugins[plugin_name] = plugin_class
            return plugin_class
            
        except ImportError as e:
            # Plugin module doesn't exist - this is OK
            self.failed_plugins.append(plugin_name)
            return None
        except Exception as e:
            # Plugin exists but has errors - log but don't crash
            print(f"Warning: Failed to load plugin {plugin_name}: {e}")
            self.failed_plugins.append(plugin_name)
            return None
    
    def create_device(self, bus: int, address: int, plugin_name: Optional[str] = None) -> Optional[DevicePlugin]:
        """Create a device plugin instance.
        
        Args:
            bus: I2C bus number
            address: I2C device address
            plugin_name: Name of plugin to use (if None, auto-detect)
            
        Returns:
            DevicePlugin instance if successful, None otherwise
        """
        # If plugin name not specified, look it up
        if plugin_name is None:
            suggestions = self.registry.lookup(address)
            if suggestions and suggestions[0][1]:  # First suggestion has plugin
                plugin_name = suggestions[0][1]
            else:
                return None
        
        # Load plugin class
        plugin_class = self.load_plugin(plugin_name)
        if plugin_class is None:
            return None
        
        try:
            # Create instance
            device = plugin_class(bus, address)
            return device
        except Exception as e:
            print(f"Warning: Failed to create device {plugin_name} at 0x{address:02X}: {e}")
            return None
    
    def get_available_plugins(self) -> List[str]:
        """Get list of available plugin names.
        
        Returns:
            List of plugin module names that are available
        """
        plugins_dir = os.path.join(os.path.dirname(__file__))
        available = []
        
        if not os.path.exists(plugins_dir):
            return available
        
        # Scan for plugin files
        for filename in os.listdir(plugins_dir):
            if filename.endswith('.py') and filename != '__init__.py' and filename != 'base.py' and filename != 'registry.py' and filename != 'loader.py':
                plugin_name = filename[:-3]  # Remove .py
                if self.load_plugin(plugin_name) is not None:
                    available.append(plugin_name)
        
        return available


# Global loader instance
_loader_instance: Optional[DeviceLoader] = None


def get_loader() -> DeviceLoader:
    """Get the global device loader instance."""
    global _loader_instance
    if _loader_instance is None:
        _loader_instance = DeviceLoader()
    return _loader_instance

