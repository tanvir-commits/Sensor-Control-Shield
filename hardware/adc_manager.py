"""ADC manager for ADS1115."""

from hardware.platform import is_raspberry_pi
from config.pins import ADC_ADDRESS, I2C_BUS


class ADCManager:
    """Simple ADC manager - real with hardware, mock otherwise."""
    
    def __init__(self):
        self.is_pi = is_raspberry_pi()
        self.adc = None
        
        if self.is_pi:
            self._init_pi()
    
    def _init_pi(self):
        """Initialize on Raspberry Pi."""
        try:
            import adafruit_ads1x15.ads1115 as ADS
            from adafruit_ads1x15.ads1x15 import Mode
            import board
            import busio
            
            # Use board.I2C() which automatically uses the correct I2C bus
            # On Pi, this uses I2C1 (pins 3/5) by default
            i2c = board.I2C()
            self.adc = ADS.ADS1115(i2c, address=ADC_ADDRESS)
            self.adc.mode = Mode.SINGLE
        except (ImportError, RuntimeError, ValueError, OSError, IOError) as e:
            # Hardware not available, library not installed, or I/O error
            # Log error but continue with mock data
            # This is normal if ADC isn't connected or on different bus
            print(f"ADC init error (using mock data): {e}")
            self.adc = None
    
    def read_channel(self, channel: int) -> float:
        """Read ADC channel (0-3)."""
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

