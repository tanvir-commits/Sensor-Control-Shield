"""Testing configuration for Device Panel.

Detects test environment and configures hardware availability.
"""

import os
import platform


def is_raspberry_pi():
    """Check if running on Raspberry Pi.
    
    Returns:
        bool: True if running on Raspberry Pi, False otherwise
    """
    try:
        # Check for Raspberry Pi hardware identifier
        with open('/proc/cpuinfo', 'r') as f:
            cpuinfo = f.read()
            if 'Raspberry Pi' in cpuinfo or 'BCM' in cpuinfo:
                return True
    except (FileNotFoundError, PermissionError):
        pass
    
    # Check platform
    if platform.system() == 'Linux':
        # Additional checks for RPi
        if os.path.exists('/sys/firmware/devicetree/base/model'):
            try:
                with open('/sys/firmware/devicetree/base/model', 'r') as f:
                    model = f.read()
                    if 'Raspberry Pi' in model:
                        return True
            except (PermissionError, UnicodeDecodeError):
                pass
    
    return False


def is_ubuntu():
    """Check if running on Ubuntu (development machine).
    
    Returns:
        bool: True if running on Ubuntu, False otherwise
    """
    if platform.system() == 'Linux':
        try:
            with open('/etc/os-release', 'r') as f:
                os_release = f.read()
                if 'Ubuntu' in os_release:
                    return True
        except (FileNotFoundError, PermissionError):
            pass
    
    return False


# Environment detection
IS_RASPBERRY_PI = is_raspberry_pi()
IS_UBUNTU = is_ubuntu()
IS_DEVELOPMENT = IS_UBUNTU and not IS_RASPBERRY_PI

# Hardware availability
# On Ubuntu, hardware is mocked
# On RPi, hardware is real
HARDWARE_AVAILABLE = IS_RASPBERRY_PI
USE_MOCK_HARDWARE = not HARDWARE_AVAILABLE

# Testing flags
ENABLE_HARDWARE_TESTS = IS_RASPBERRY_PI
ENABLE_MOCK_TESTS = not IS_RASPBERRY_PI

# Display configuration
# On Ubuntu, may need X11 forwarding or local display
# On RPi, typically has local display
HAS_DISPLAY = os.getenv('DISPLAY') is not None or IS_RASPBERRY_PI

