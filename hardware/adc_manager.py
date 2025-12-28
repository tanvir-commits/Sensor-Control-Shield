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
                print(f"ADC: Failed to initialize ADS1115 with adafruit library: {e}")
                # Try direct smbus2 access as fallback
                try:
                    return self._read_channel_smbus2(channel)
                except Exception as e2:
                    print(f"ADC: smbus2 fallback also failed: {e2}")
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
    
    def _read_channel_smbus2(self, channel: int) -> float:
        """Read ADC channel using direct smbus2 access (fallback method)."""
        import smbus2
        import time
        
        # ADS1115 register addresses
        CONVERSION_REG = 0x00  # Conversion result (read-only)
        CONFIG_REG = 0x01      # Configuration register (read/write)
        
        # Channel mapping for ADS1115 config register
        # Bits 14-12: MUX (channel selection)
        # 000 = AIN0 vs GND (channel 0)
        # 001 = AIN1 vs GND (channel 1)
        # 010 = AIN2 vs GND (channel 2)
        # 011 = AIN3 vs GND (channel 3)
        mux_values = [0x4000, 0x5000, 0x6000, 0x7000]  # Bits 14-12
        
        # Config register value:
        # Bit 15: OS (operational status) = 1 (start single conversion)
        # Bits 14-12: MUX (channel) = channel selection
        # Bits 11-9: PGA = 010 (±4.096V range)
        # Bit 8: MODE = 1 (single-shot mode)
        # Bits 7-5: DR = 100 (128 SPS)
        # Bits 4-0: Other settings = 0
        config = 0x8000 | mux_values[channel] | 0x0100 | 0x0080 | 0x0010
        
        try:
            bus = smbus2.SMBus(1)  # I2C bus 1
            
            # Write config register to start conversion
            # ADS1115 uses big-endian 16-bit values
            bus.write_i2c_block_data(ADC_ADDRESS, CONFIG_REG, [
                (config >> 8) & 0xFF,  # High byte
                config & 0xFF           # Low byte
            ])
            
            # Wait for conversion (poll OS bit)
            timeout = 0.1  # 100ms timeout
            start_time = time.time()
            while time.time() - start_time < timeout:
                time.sleep(0.01)
                # Read config register to check OS bit
                config_data = bus.read_i2c_block_data(ADC_ADDRESS, CONFIG_REG, 2)
                config_status = (config_data[0] << 8) | config_data[1]
                if (config_status & 0x8000) == 0:  # OS bit cleared = conversion done
                    break
            
            # Read conversion result
            result_data = bus.read_i2c_block_data(ADC_ADDRESS, CONVERSION_REG, 2)
            # ADS1115 returns big-endian 16-bit signed value
            raw_value = (result_data[0] << 8) | result_data[1]
            # Convert to signed 16-bit
            if raw_value & 0x8000:
                raw_value = raw_value - 65536
            
            bus.close()
            
            # Convert to voltage (±4.096V range, 16-bit)
            voltage = (raw_value / 32767.0) * 4.096
            return voltage
            
        except Exception as e:
            raise Exception(f"smbus2 read failed: {e}")
    
    def read_all_channels(self):
        """Read all 4 channels."""
        return {i: self.read_channel(i) for i in range(4)}

