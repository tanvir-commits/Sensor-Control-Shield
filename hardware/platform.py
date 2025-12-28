"""Platform detection for hardware abstraction."""

import platform


def is_raspberry_pi():
    """Check if running on Raspberry Pi."""
    try:
        with open('/proc/cpuinfo', 'r') as f:
            cpuinfo = f.read()
            return 'Raspberry Pi' in cpuinfo or 'BCM' in cpuinfo
    except:
        return False


def get_platform():
    """Get platform name."""
    if is_raspberry_pi():
        return 'raspberry_pi'
    return 'pc'


