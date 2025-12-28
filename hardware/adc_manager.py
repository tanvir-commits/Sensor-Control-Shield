"""ADC manager for ADS1115."""

from hardware.platform import is_raspberry_pi
from config.pins import ADC_ADDRESS, I2C_BUS


class ADCManager:
    """Simple ADC manager - real with hardware, mock otherwise."""
    
    def __init__(self):
        self.is_pi = is_raspberry_pi()
        self.adc = None
        self._i2c = None
        # Don't initialize I2C bus during __init__ to avoid interfering with I2C scanner
        # Will be created lazily on first read
    
    def _get_i2c(self):
        """Get or create I2C bus (lazy initialization)."""
        if not self.is_pi:
            return None
        
        if self._i2c is None:
            try:
                import board
                # Create I2C bus only when needed
                self._i2c = board.I2C()
            except Exception as e:
                print(f"Failed to create I2C bus: {e}")
                return None
        
        return self._i2c
    
    def read_channel(self, channel: int) -> float:
        """Read ADC channel (0-3)."""
        if not self.is_pi:
            # Mock data
            mock_voltages = {0: 1.234, 1: 3.301, 2: 0.012, 3: 5.002}
            return mock_voltages.get(channel, 0.0)
        
        # Lazy initialization: create ADC only when needed
        if self.adc is None:
            i2c = self._get_i2c()
            if i2c:
                try:
                    import adafruit_ads1x15.ads1115 as ADS
                    from adafruit_ads1x15.ads1x15 import Mode
                    self.adc = ADS.ADS1115(i2c, address=ADC_ADDRESS)
                    self.adc.mode = Mode.SINGLE
                except (ImportError, RuntimeError, ValueError, OSError, IOError) as e:
                    # Hardware not available, library not installed, or I/O error
                    # Log error but continue with mock data
                    print(f"ADC init error (using mock data): {e}")
                    self.adc = None
        
        if self.adc:
            try:
                import adafruit_ads1x15.ads1115 as ADS
                # ADS1115 channels
                channels = [
                    ADS.P0, ADS.P1, ADS.P2, ADS.P3
                ]
                if 0 <= channel <= 3:
                    value = self.adc.read(channels[channel])
                    # Convert to voltage (ADS1115 is 16-bit, ±4.096V range)
                    voltage = (value / 32767.0) * 4.096
                    return voltage
            except:
                pass
        
        # Mock data
        mock_voltages = {0: 1.234, 1: 3.301, 2: 0.012, 3: 5.002}
        return mock_voltages.get(channel, 0.0)
    
    def read_all_channels(self):
        """Read all 4 channels."""
        return {i: self.read_channel(i) for i in range(4)}

