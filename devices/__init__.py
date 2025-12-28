"""Device plugin system for Device Panel.

This module provides a plugin architecture for I2C device support.
Plugins are loaded dynamically and provide device-specific testing interfaces.
"""

from .base import DevicePlugin
from .registry import DeviceRegistry, get_registry
from .loader import DeviceLoader, get_loader

__all__ = [
    'DevicePlugin',
    'DeviceRegistry',
    'get_registry',
    'DeviceLoader',
    'get_loader',
]

