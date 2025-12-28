"""ADC manager for ADS1115."""

from hardware.platform import is_raspberry_pi
from config.pins import ADC_ADDRESS, I2C_BUS


class ADCManager:
    """Simple ADC manager - real with hardware, mock otherwise."""
    
    def __init__(self):
        self.is_pi = is_raspberry_pi()
        self.adc = None
        self.i2c = None
        # Don't initialize I2C bus during __init__ to avoid interfering with I2C scanner
        # Will be created lazily on first read
    
    def _get_i2c(self):
        """Get or create I2C bus (lazy initialization)."""
        if not self.is_pi:
            return None
        
        if self.i2c is None:
            try:
                import board
                import time
                # Create I2C bus only when needed
                self.i2c = board.I2C()
                time.sleep(0.1)  # Let bus settle
            except Exception as e:
                print(f"Failed to create I2C bus: {e}")
                return None
        
        return self.i2c
    
    def read_channel(self, channel: int) -> float:
        """Read ADC channel (0-3)."""
        if not self.is_pi:
            # Mock data
            mock_voltages = {0: 1.234, 1: 3.301, 2: 0.012, 3: 5.002}
            return mock_voltages.get(channel, 0.0)
        
        # Lazy initialization: create I2C bus and ADC only when needed
        if self.adc is None:
            i2c = self._get_i2c()
            if not i2c:
                # Can't create I2C bus - return mock data
                mock_voltages = {0: 1.234, 1: 3.301, 2: 0.012, 3: 5.002}
                return mock_voltages.get(channel, 0.0)
            
            # Try to create ADC instance
            try:
                import adafruit_ads1x15.ads1115 as ADS
                from adafruit_ads1x15.ads1x15 import Mode
                
                try:
                    self.adc = ADS.ADS1115(i2c, address=ADC_ADDRESS)
                    self.adc.mode = Mode.SINGLE
                    print("ADC object created successfully on first read")
                except RuntimeError as e:
                    # Device not detected - return mock data
                    error_msg = str(e)
                    if "No I2C device" in error_msg or "0x48" in error_msg:
                        print(f"ADC device not found at 0x{ADC_ADDRESS:02X}: {e}")
                    else:
                        print(f"ADC init error: {e}")
                    # Return mock data instead of failing
                    mock_voltages = {0: 1.234, 1: 3.301, 2: 0.012, 3: 5.002}
                    return mock_voltages.get(channel, 0.0)
            except ImportError as e:
                print(f"ADC libraries not available: {e}")
                mock_voltages = {0: 1.234, 1: 3.301, 2: 0.012, 3: 5.002}
                return mock_voltages.get(channel, 0.0)
        
        # Read from ADC
        if self.adc:
            try:
                import adafruit_ads1x15.ads1115 as ADS
                import time
                
                # ADS1115 channels
                channels = [
                    ADS.P0, ADS.P1, ADS.P2, ADS.P3
                ]
                if 0 <= channel <= 3:
                    # Add small delay between reads to avoid bus congestion
                    time.sleep(0.01)
                    value = self.adc.read(channels[channel])
                    # Convert to voltage (ADS1115 is 16-bit, ±4.096V range)
                    voltage = (value / 32767.0) * 4.096
                    return voltage
            except Exception as e:
                # Log error but don't crash
                print(f"ADC read error (channel {channel}): {e}")
        
        # Fallback to mock data
        mock_voltages = {0: 1.234, 1: 3.301, 2: 0.012, 3: 5.002}
        return mock_voltages.get(channel, 0.0)
    
    def read_all_channels(self):
        """Read all 4 channels."""
        return {i: self.read_channel(i) for i in range(4)}
