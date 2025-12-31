"""Power measurement manager for INA260 current sensors."""

import time
from typing import Dict, List, Optional, Tuple
from hardware.platform import is_raspberry_pi


class INA260Sensor:
    """INA260 current/power sensor interface."""
    
    # INA260 register addresses
    REG_CONFIG = 0x00
    REG_CURRENT = 0x01
    REG_BUS_VOLTAGE = 0x02
    REG_POWER = 0x03
    REG_MASK_ENABLE = 0x06
    REG_ALERT_LIMIT = 0x07
    REG_MANUFACTURER_ID = 0xFE
    REG_DIE_ID = 0xFF
    
    # INA260 default address
    DEFAULT_ADDRESS = 0x40
    
    def __init__(self, bus: int, address: int = DEFAULT_ADDRESS):
        """Initialize INA260 sensor.
        
        Args:
            bus: I2C bus number
            address: I2C address (default 0x40)
        """
        self.bus = bus
        self.address = address
        self.is_pi = is_raspberry_pi()
        self._smbus = None
        self._initialized = False
        
        if self.is_pi:
            self._init_pi()
    
    def _init_pi(self):
        """Initialize on Raspberry Pi."""
        try:
            import smbus2
            self._smbus = smbus2.SMBus(self.bus)
            # Small delay to let bus settle
            time.sleep(0.01)
            # Verify sensor is present
            self._verify_sensor()
            self._configure_sensor()
            self._initialized = True
        except ImportError:
            self._smbus = None
        except Exception as e:
            print(f"INA260 init error (bus {self.bus}, addr 0x{self.address:02X}): {e}")
            self._smbus = None
    
    def _verify_sensor(self):
        """Verify INA260 sensor is present by reading manufacturer ID."""
        if not self._smbus:
            return False
        try:
            # Read manufacturer ID (should be 0x5449 for TI)
            data = self._smbus.read_i2c_block_data(self.address, self.REG_MANUFACTURER_ID, 2)
            manufacturer_id = (data[0] << 8) | data[1]
            if manufacturer_id == 0x5449:  # TI manufacturer ID
                return True
        except:
            pass
        return False
    
    def _configure_sensor(self):
        """Configure INA260 sensor for continuous measurement."""
        if not self._smbus:
            return
        try:
            # Configuration register:
            # - Reset bit (15) = 0 (no reset)
            # - Averaging (11-9) = 111 (1024 samples) for accuracy
            # - Bus voltage conversion time (8-6) = 110 (1.1ms)
            # - Current conversion time (5-3) = 110 (1.1ms)
            # - Mode (2-0) = 111 (continuous bus voltage and current)
            config = 0xE7FF  # Continuous mode, 1024 samples average, 1.1ms conversion
            
            self._smbus.write_i2c_block_data(self.address, self.REG_CONFIG, [
                (config >> 8) & 0xFF,
                config & 0xFF
            ])
            # Wait for configuration to take effect
            time.sleep(0.01)
        except Exception as e:
            print(f"INA260 config error: {e}")
    
    def read_current(self) -> float:
        """Read current in Amperes.
        
        Returns:
            Current in Amperes (positive or negative)
        """
        if not self.is_pi or not self._smbus:
            # Mock data for testing
            return 0.123
        
        try:
            data = self._smbus.read_i2c_block_data(self.address, self.REG_CURRENT, 2)
            # INA260 returns signed 16-bit value
            raw_value = (data[0] << 8) | data[1]
            # Convert to signed
            if raw_value & 0x8000:
                raw_value = raw_value - 65536
            
            # INA260 current LSB = 1.25mA (0.00125 A)
            current = raw_value * 0.00125
            return current
        except Exception as e:
            print(f"INA260 current read error: {e}")
            return 0.0
    
    def read_voltage(self) -> float:
        """Read bus voltage in Volts.
        
        Returns:
            Voltage in Volts
        """
        if not self.is_pi or not self._smbus:
            # Mock data for testing
            return 3.3
        
        try:
            data = self._smbus.read_i2c_block_data(self.address, self.REG_BUS_VOLTAGE, 2)
            # INA260 voltage register: bits 15-3 are voltage, bit 2 is conversion ready
            raw_value = (data[0] << 8) | data[1]
            # Extract voltage (bits 15-3)
            voltage_raw = (raw_value >> 3) & 0x1FFF
            
            # INA260 voltage LSB = 1.25mV (0.00125 V)
            voltage = voltage_raw * 0.00125
            return voltage
        except Exception as e:
            print(f"INA260 voltage read error: {e}")
            return 0.0
    
    def read_power(self) -> float:
        """Read power in Watts.
        
        Returns:
            Power in Watts
        """
        if not self.is_pi or not self._smbus:
            # Mock data for testing
            return 0.405  # 3.3V * 0.123A
        
        try:
            data = self._smbus.read_i2c_block_data(self.address, self.REG_POWER, 2)
            # INA260 power register: unsigned 16-bit
            raw_value = (data[0] << 8) | data[1]
            
            # INA260 power LSB = 10mW (0.01 W)
            power = raw_value * 0.01
            return power
        except Exception as e:
            print(f"INA260 power read error: {e}")
            return 0.0
    
    def read_all(self) -> Dict[str, float]:
        """Read all measurements.
        
        Returns:
            Dictionary with 'current', 'voltage', and 'power'
        """
        return {
            'current': self.read_current(),
            'voltage': self.read_voltage(),
            'power': self.read_power()
        }
    
    def close(self):
        """Close I2C bus connection."""
        if self._smbus:
            try:
                self._smbus.close()
            except:
                pass
            self._smbus = None


class PowerMeasurementManager:
    """Manager for multiple INA260 sensors on different I2C buses."""
    
    def __init__(self):
        """Initialize power measurement manager."""
        self.sensors: Dict[Tuple[int, int], INA260Sensor] = {}  # (bus, address) -> sensor
        self.bus_names: Dict[int, str] = {}  # bus -> user-defined name
        self.is_pi = is_raspberry_pi()
    
    def add_sensor(self, bus: int, address: int = INA260Sensor.DEFAULT_ADDRESS, 
                   bus_name: Optional[str] = None) -> bool:
        """Add an INA260 sensor.
        
        Args:
            bus: I2C bus number
            address: I2C address (default 0x40)
            bus_name: Optional user-defined name for the bus (e.g., "LCD", "MCU", "Motor")
        
        Returns:
            True if sensor was added successfully, False otherwise
        """
        key = (bus, address)
        if key in self.sensors:
            return True  # Already added
        
        try:
            sensor = INA260Sensor(bus, address)
            if sensor._smbus or not self.is_pi:  # Success or mock mode
                self.sensors[key] = sensor
                if bus_name:
                    self.bus_names[bus] = bus_name
                return True
        except Exception as e:
            print(f"Failed to add INA260 sensor (bus {bus}, addr 0x{address:02X}): {e}")
        
        return False
    
    def remove_sensor(self, bus: int, address: int):
        """Remove a sensor.
        
        Args:
            bus: I2C bus number
            address: I2C address
        """
        key = (bus, address)
        if key in self.sensors:
            self.sensors[key].close()
            del self.sensors[key]
    
    def get_sensor(self, bus: int, address: int) -> Optional[INA260Sensor]:
        """Get a sensor by bus and address.
        
        Args:
            bus: I2C bus number
            address: I2C address
        
        Returns:
            INA260Sensor instance or None
        """
        return self.sensors.get((bus, address))
    
    def get_bus_name(self, bus: int) -> str:
        """Get user-defined name for a bus, or default name.
        
        Args:
            bus: I2C bus number
        
        Returns:
            Bus name (user-defined or default like "Bus 1")
        """
        return self.bus_names.get(bus, f"Bus {bus}")
    
    def set_bus_name(self, bus: int, name: str):
        """Set user-defined name for a bus.
        
        Args:
            bus: I2C bus number
            name: User-defined name
        """
        self.bus_names[bus] = name
    
    def list_sensors(self) -> List[Dict]:
        """List all registered sensors.
        
        Returns:
            List of dictionaries with 'bus', 'address', 'bus_name', and 'sensor' keys
        """
        result = []
        for (bus, address), sensor in self.sensors.items():
            result.append({
                'bus': bus,
                'address': address,
                'bus_name': self.get_bus_name(bus),
                'sensor': sensor
            })
        return result
    
    def scan_bus_for_ina260(self, bus: int) -> List[int]:
        """Scan I2C bus for INA260 sensors.
        
        Args:
            bus: I2C bus number
        
        Returns:
            List of INA260 addresses found (typically 0x40, 0x41, etc.)
        """
        if not self.is_pi:
            # Mock: return common addresses
            return [0x40, 0x41]
        
        addresses = []
        try:
            import smbus2
            smbus = smbus2.SMBus(bus)
            
            # INA260 addresses are typically 0x40-0x4F (A0-A3 pins)
            # Check common addresses
            for addr in range(0x40, 0x50):
                try:
                    # Try to read manufacturer ID to verify it's an INA260
                    data = smbus.read_i2c_block_data(addr, INA260Sensor.REG_MANUFACTURER_ID, 2)
                    manufacturer_id = (data[0] << 8) | data[1]
                    if manufacturer_id == 0x5449:  # TI manufacturer ID
                        addresses.append(addr)
                except:
                    pass
            
            smbus.close()
        except Exception as e:
            print(f"Error scanning bus {bus} for INA260: {e}")
        
        return addresses
    
    def close_all(self):
        """Close all sensor connections."""
        for sensor in self.sensors.values():
            sensor.close()
        self.sensors.clear()

