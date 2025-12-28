"""I2C bus scanner - works on both PC and Raspberry Pi."""

import os
from typing import List, Optional


class I2CScanner:
    """I2C bus scanner using standard Linux I2C interface."""
    
    def __init__(self, bus: Optional[int] = None):
        """Initialize I2C scanner.
        
        Args:
            bus: I2C bus number. If None, auto-detects the first available bus.
        """
        if bus is None:
            bus = self._auto_detect_bus()
        self.bus = bus
        self.device_path = f"/dev/i2c-{bus}"
    
    def _auto_detect_bus(self) -> int:
        """Auto-detect the I2C bus with devices, or first available.
        
        Returns:
            Bus number with devices, or first available bus, or 1 as fallback
        """
        # Priority: Bus 1 first (GPIO2/3 - standard I2C1 on Pi)
        # Then bus 3 (I2C3 on GPIO4/5 - if enabled via dtoverlay)
        # Then check other buses (Pi 5 may use 13/14)
        bus_priority = [1, 3, 0, 14, 13, 10, 11, 12, 15]
        
        # First, try to find a bus with devices
        for bus_num in bus_priority:
            if os.path.exists(f"/dev/i2c-{bus_num}"):
                # Quick check if this bus has devices
                try:
                    import smbus2
                    test_bus = smbus2.SMBus(bus_num)
                    # Quick scan of a few addresses
                    found_any = False
                    for addr in [0x48, 0x37, 0x3a, 0x50, 0x68]:  # Common addresses
                        try:
                            test_bus.write_quick(addr)
                            found_any = True
                            break
                        except:
                            pass
                    test_bus.close()
                    if found_any:
                        return bus_num
                except:
                    pass
        
        # If no bus with devices found, return first available (prefer bus 1)
        for bus_num in bus_priority:
            if os.path.exists(f"/dev/i2c-{bus_num}"):
                return bus_num
        
        # Fallback
        return 1
    
    def scan(self) -> List[int]:
        """Scan I2C bus for devices.
        
        Uses write_quick() method which is more reliable than read_byte()
        for device detection (same method used by i2cdetect).
        
        Returns:
            List of device addresses found (0x08-0x77)
        """
        devices = []
        
        # Check if I2C bus exists
        if not os.path.exists(self.device_path):
            return devices
        
        try:
            import smbus2
            import time
            
            # Open fresh bus connection for each scan
            bus = smbus2.SMBus(self.bus)
            
            # Small delay to let bus settle (helps with capacitance issues)
            time.sleep(0.01)
            
            # Scan addresses 0x08 to 0x77 (valid I2C addresses)
            # Note: Addresses 0x00-0x07 and 0x78-0x7F are reserved
            for addr in range(0x08, 0x78):
                try:
                    # Use write_quick() - same method as i2cdetect
                    # This sends a write command and checks for ACK
                    # More reliable than read_byte() which can give false positives
                    bus.write_quick(addr)
                    devices.append(addr)
                    # Small delay between addresses to avoid bus congestion
                    time.sleep(0.001)
                except (IOError, OSError, TimeoutError):
                    # Device not present at this address - this is normal
                    # TimeoutError is a subclass of OSError but explicitly catch it
                    pass
                except Exception as e:
                    # Other unexpected errors - log but continue scanning
                    # This should rarely happen, but if it does, we don't want to stop scanning
                    import sys
                    print(f"Unexpected I2C scan error at 0x{addr:02X}: {type(e).__name__}: {e}", file=sys.stderr)
                    pass
            
            bus.close()
            # Small delay after closing to ensure bus is ready for next scan
            time.sleep(0.01)
        except ImportError:
            # smbus2 not installed
            raise RuntimeError("smbus2 library not installed")
        except PermissionError:
            # Permission denied - user not in i2c group
            raise RuntimeError(f"Permission denied accessing {self.device_path}. Add user to 'i2c' group.")
        except FileNotFoundError:
            # I2C bus device not found
            raise RuntimeError(f"I2C bus {self.bus} not found. Is I2C enabled?")
        except Exception as e:
            # Other bus errors
            raise RuntimeError(f"I2C bus error: {e}")
        
        return devices
    
    def get_status(self) -> str:
        """Get I2C bus status."""
        if os.path.exists(self.device_path):
            return "OK"
        return "NOT_AVAILABLE"
    
    @staticmethod
    def scan_all_buses() -> dict:
        """Scan all available I2C buses.
        
        Returns:
            Dictionary mapping bus numbers to lists of device addresses
        """
        results = {}
        # Check common bus numbers
        for bus_num in range(0, 16):
            bus_path = f"/dev/i2c-{bus_num}"
            if os.path.exists(bus_path):
                try:
                    scanner = I2CScanner(bus=bus_num)
                    devices = scanner.scan()
                    if devices:
                        results[bus_num] = devices
                except:
                    pass
        return results


