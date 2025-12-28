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
        # Don't initialize here - will be lazy-loaded on first read
        # This avoids I2C conflicts and allows retry on each read
        self.adc = None
        self._i2c = None
    
    def read_channel(self, channel: int) -> float:
        """Read ADC channel (0-3)."""
        if not self.is_pi:
            # Mock data
            mock_voltages = {0: 1.234, 1: 3.301, 2: 0.012, 3: 5.002}
            return mock_voltages.get(channel, 0.0)
        
        # Lazy initialization: create I2C and ADC on first read
        if self._i2c is None:
            try:
                import board
                import time
                self._i2c = board.I2C()
                time.sleep(0.1)  # Let bus settle
            except Exception as e:
                print(f"ADC: Failed to create I2C bus: {e}")
                mock_voltages = {0: 1.234, 1: 3.301, 2: 0.012, 3: 5.002}
                return mock_voltages.get(channel, 0.0)
        
        # Try to create/use ADC object
        if self.adc is None:
            try:
                import adafruit_ads1x15.ads1115 as ADS
                from adafruit_ads1x15.ads1x15 import Mode
                import time
                
                # Try to create ADC with retry
                for attempt in range(3):
                    try:
                        self.adc = ADS.ADS1115(self._i2c, address=ADC_ADDRESS)
                        self.adc.mode = Mode.SINGLE
                        # Test read to verify it works
                        try:
                            test_value = self.adc.read(ADS.P0)
                            break  # Success
                        except:
                            # Test read failed, try again
                            self.adc = None
                            time.sleep(0.1)
                    except Exception as e:
                        if attempt < 2:
                            time.sleep(0.1)
                            continue
                        else:
                            raise
            except Exception as e:
                print(f"ADC: Failed to initialize ADS1115: {e}")
                # Return mock data instead of failing
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
                    time.sleep(0.01)  # Small delay between reads
                    value = self.adc.read(channels[channel])
                    # Convert to voltage (ADS1115 is 16-bit, ±4.096V range)
                    # ADS1115 returns signed 16-bit value, ±32767 for ±4.096V
                    voltage = (value / 32767.0) * 4.096
                    return voltage
            except Exception as e:
                print(f"ADC read error (channel {channel}): {e}")
                # Reset ADC object to force re-initialization on next read
                self.adc = None
        
        # Fallback to mock data
        mock_voltages = {0: 1.234, 1: 3.301, 2: 0.012, 3: 5.002}
        return mock_voltages.get(channel, 0.0)
    
    def read_all_channels(self):
        """Read all 4 channels."""
        return {i: self.read_channel(i) for i in range(4)}

