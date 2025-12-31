"""Power profiler core functionality."""

import time
from typing import Dict, List, Optional, Callable
from hardware.power_measurement import PowerMeasurementManager, INA260Sensor


class PowerProfiler:
    """Power profiler for measurement and test automation."""
    
    def __init__(self, power_manager: PowerMeasurementManager,
                 gpio_manager=None, adc_manager=None):
        """Initialize power profiler.
        
        Args:
            power_manager: PowerMeasurementManager instance
            gpio_manager: GPIOManager instance (optional)
            adc_manager: ADCManager instance (optional)
        """
        self.power_manager = power_manager
        self.gpio_manager = gpio_manager
        self.adc_manager = adc_manager
        
        # Measurement history
        self.measurement_history: List[Dict] = []
        self.max_history = 1000  # Keep last 1000 measurements
        
        # Continuous measurement state
        self.continuous_measuring = False
        self.measurement_callback: Optional[Callable] = None
    
    def add_sensor(self, bus: int, address: int = 0x40, bus_name: Optional[str] = None) -> bool:
        """Add a power sensor.
        
        Args:
            bus: I2C bus number
            address: I2C address (default 0x40)
            bus_name: Optional user-defined name for the bus
        
        Returns:
            True if sensor was added successfully
        """
        return self.power_manager.add_sensor(bus, address, bus_name)
    
    def remove_sensor(self, bus: int, address: int):
        """Remove a power sensor."""
        self.power_manager.remove_sensor(bus, address)
    
    def get_measurement(self, bus: int, address: int) -> Optional[Dict[str, float]]:
        """Get current measurement from a sensor.
        
        Args:
            bus: I2C bus number
            address: I2C address
        
        Returns:
            Dictionary with 'current', 'voltage', 'power', 'timestamp', 'bus', 'address'
            or None if sensor not found
        """
        sensor = self.power_manager.get_sensor(bus, address)
        if not sensor:
            return None
        
        measurement = sensor.read_all()
        measurement['timestamp'] = time.time()
        measurement['bus'] = bus
        measurement['address'] = address
        measurement['bus_name'] = self.power_manager.get_bus_name(bus)
        
        return measurement
    
    def get_all_measurements(self) -> List[Dict[str, float]]:
        """Get current measurements from all sensors.
        
        Returns:
            List of measurement dictionaries
        """
        measurements = []
        for sensor_info in self.power_manager.list_sensors():
            measurement = self.get_measurement(sensor_info['bus'], sensor_info['address'])
            if measurement:
                measurements.append(measurement)
        return measurements
    
    def start_continuous_measurement(self, interval: float = 0.1, 
                                     callback: Optional[Callable] = None):
        """Start continuous measurement.
        
        Args:
            interval: Measurement interval in seconds (default 0.1 = 10Hz)
            callback: Optional callback function called with each measurement
        """
        self.continuous_measuring = True
        self.measurement_callback = callback
        
        # Note: Actual continuous measurement would be implemented with a thread
        # For now, this is a placeholder that can be called periodically
        # The UI will handle the timing via QTimer
    
    def stop_continuous_measurement(self):
        """Stop continuous measurement."""
        self.continuous_measuring = False
        self.measurement_callback = None
    
    def take_measurement(self) -> List[Dict[str, float]]:
        """Take a single measurement from all sensors and add to history.
        
        Returns:
            List of measurement dictionaries
        """
        measurements = self.get_all_measurements()
        
        # Add to history
        for measurement in measurements:
            self.measurement_history.append(measurement)
            # Trim history if too long
            if len(self.measurement_history) > self.max_history:
                self.measurement_history.pop(0)
        
        # Call callback if continuous measurement is active
        if self.continuous_measuring and self.measurement_callback:
            for measurement in measurements:
                self.measurement_callback(measurement)
        
        return measurements
    
    def clear_history(self):
        """Clear measurement history."""
        self.measurement_history.clear()
    
    def get_history(self, bus: Optional[int] = None, 
                   address: Optional[int] = None,
                   max_points: Optional[int] = None) -> List[Dict]:
        """Get measurement history.
        
        Args:
            bus: Filter by bus number (optional)
            address: Filter by address (optional)
            max_points: Maximum number of points to return (optional)
        
        Returns:
            List of measurement dictionaries
        """
        history = self.measurement_history
        
        # Filter by bus/address if specified
        if bus is not None or address is not None:
            history = [
                m for m in history
                if (bus is None or m.get('bus') == bus) and
                   (address is None or m.get('address') == address)
            ]
        
        # Limit points if specified
        if max_points and len(history) > max_points:
            history = history[-max_points:]
        
        return history
    
    def scan_bus(self, bus: int) -> List[int]:
        """Scan I2C bus for INA260 sensors.
        
        Args:
            bus: I2C bus number
        
        Returns:
            List of INA260 addresses found
        """
        return self.power_manager.scan_bus_for_ina260(bus)
    
    def list_sensors(self) -> List[Dict]:
        """List all registered sensors.
        
        Returns:
            List of sensor information dictionaries
        """
        return self.power_manager.list_sensors()

