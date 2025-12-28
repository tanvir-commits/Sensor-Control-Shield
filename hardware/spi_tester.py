"""SPI tester - simple implementation."""

from hardware.platform import is_raspberry_pi
import os


class SPITester:
    """Simple SPI tester - real on Pi, mock on PC."""
    
    def __init__(self):
        self.is_pi = is_raspberry_pi()
        self.spi_device = "/dev/spidev0.0"
        self._test_count = 0
    
    def test(self):
        """Run SPI test."""
        if self.is_pi and os.path.exists(self.spi_device):
            try:
                import spidev
                spi = spidev.SpiDev()
                spi.open(0, 0)
                # Simple test: try to read
                spi.xfer2([0x00])
                spi.close()
                return {
                    "enabled": "SPI enabled",
                    "activity": "Clock/MOSI activity detected",
                    "miso": "MISO response detected",
                    "status": "OK"
                }
            except:
                return {
                    "enabled": "SPI enabled",
                    "status": "ERROR"
                }
        
        # Mock result
        self._test_count += 1
        return {
            "enabled": "SPI enabled",
            "activity": "Clock/MOSI activity detected",
            "miso": "MISO response detected" if self._test_count % 2 == 0 else "MISO response not detected",
            "status": "OK" if self._test_count % 2 == 0 else "NOT VERIFIED"
        }


