"""ADS1115/ADS1015 ADC plugin."""

from typing import Optional
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton
from .base import DevicePlugin


class ADS1115Plugin(DevicePlugin):
    """Plugin for ADS1115/ADS1015 ADC devices."""
    
    addresses = [0x48, 0x49, 0x4A, 0x4B]
    name = "ADS1115"
    manufacturer = "Texas Instruments"
    description = "16-bit/12-bit ADC with 4 channels"
    
    def detect(self) -> bool:
        """Detect if ADS1115 is present."""
        try:
            import smbus2
            bus = smbus2.SMBus(self.bus)
            # Try to read from device (simple detection)
            bus.write_quick(self.address)
            bus.close()
            return True
        except Exception:
            return False
    
    def get_info(self) -> dict:
        """Get device information."""
        info = super().get_info()
        info.update({
            "resolution": "16-bit (ADS1115) or 12-bit (ADS1015)",
            "channels": 4,
            "interface": "I2C",
            "datasheet": "https://www.ti.com/product/ADS1115",
        })
        return info
    
    def get_test_ui(self) -> Optional[QWidget]:
        """Get test interface for ADS1115."""
        from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QGroupBox
        
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(20, 15, 20, 20)
        
        # Title
        title = QLabel("ADS1115 ADC Test Interface")
        title.setStyleSheet("font-size: 22pt; font-weight: bold; padding: 15px;")
        layout.addWidget(title)
        
        # Info
        info_label = QLabel(
            "This ADC is already integrated into the Analog section.\n"
            "Click the button below to read all 4 channels directly from the device."
        )
        info_label.setWordWrap(True)
        info_label.setStyleSheet("padding: 15px; color: #666; font-size: 16pt;")
        layout.addWidget(info_label)
        
        # Test readings group
        readings_group = QGroupBox("Current ADC Readings")
        readings_group.setStyleSheet("font-size: 18pt; font-weight: bold; padding-top: 20px;")
        readings_layout = QVBoxLayout()
        readings_layout.setSpacing(15)
        
        channel_labels = {}
        for ch in range(4):
            row = QHBoxLayout()
            label = QLabel(f"Channel {ch}:")
            label.setStyleSheet("font-weight: bold; min-width: 150px; font-size: 16pt;")
            value_label = QLabel("--")
            value_label.setStyleSheet("font-size: 18pt; font-weight: bold; color: #007bff; min-width: 200px;")
            channel_labels[ch] = value_label
            row.addWidget(label)
            row.addWidget(value_label)
            row.addStretch()
            readings_layout.addLayout(row)
        
        readings_group.setLayout(readings_layout)
        layout.addWidget(readings_group)
        
        # Test button
        test_button = QPushButton("Read All Channels")
        test_button.setMinimumHeight(60)
        test_button.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #28a745, stop:1 #1e7e34);
                color: white;
                border: none;
                border-radius: 6px;
                padding: 15px;
                font-size: 18pt;
                font-weight: bold;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #1e7e34, stop:1 #155724);
            }
            QPushButton:pressed {
                background: #155724;
            }
        """)
        
        # Connect button - use method reference to ensure proper scope
        test_button.clicked.connect(lambda checked=False: self._read_adc_channels(channel_labels))
        layout.addWidget(test_button)
        
        layout.addStretch()
        widget.setLayout(layout)
        
        return widget
    
    def _read_adc_channels(self, channel_labels):
        """Read all ADC channels and update display."""
        import sys
        
        # Try using adafruit library's AnalogIn (most reliable)
        try:
            import board
            from adafruit_ads1x15.ads1115 import ADS1115
            from adafruit_ads1x15.analog_in import AnalogIn
            
            i2c = board.I2C()
            ads = ADS1115(i2c, address=self.address)
            ads.gain = 1  # ±4.096V range
            
            # Create AnalogIn objects for each channel
            channels = [
                AnalogIn(ads, ADS1115.P0),  # AIN0
                AnalogIn(ads, ADS1115.P1),  # AIN1
                AnalogIn(ads, ADS1115.P2),  # AIN2
                AnalogIn(ads, ADS1115.P3),  # AIN3
            ]
            
            for ch in range(4):
                try:
                    voltage = channels[ch].voltage
                    channel_labels[ch].setText(f"{voltage:.4f} V")
                    channel_labels[ch].setStyleSheet("font-size: 18pt; font-weight: bold; color: #28a745; min-width: 200px;")
                except Exception as e:
                    channel_labels[ch].setText(f"Error")
                    channel_labels[ch].setStyleSheet("font-size: 18pt; font-weight: bold; color: #dc3545; min-width: 200px;")
                    print(f"DEBUG: Error reading channel {ch}: {e}", file=sys.stderr)
            
            return
            
        except Exception as e:
            print(f"DEBUG: adafruit library failed: {e}, trying smbus2", file=sys.stderr)
            # Fallback to smbus2
            pass
        
        # Fallback: Use smbus2 directly
        try:
            import smbus2
            import time
            
            bus = smbus2.SMBus(self.bus)
            
            # MUX values for single-ended channels (bits 14-12 of config register)
            # 0x4000 = AIN0 vs GND (channel 0)
            # 0x5000 = AIN1 vs GND (channel 1)
            # 0x6000 = AIN2 vs GND (channel 2)
            # 0x7000 = AIN3 vs GND (channel 3)
            mux_values = [0x4000, 0x5000, 0x6000, 0x7000]
            
            # Read all 4 channels
            for ch in range(4):
                try:
                    # Configure ADC for this channel and start conversion
                    # Bit 15: OS = 1 (start single conversion)
                    # Bits 14-12: MUX = channel selection
                    # Bits 11-9: PGA = 010 (±4.096V range)
                    # Bit 8: MODE = 1 (single-shot mode)
                    # Bits 7-5: DR = 100 (128 SPS)
                    config_val = 0x8000 | mux_values[ch] | 0x0100 | 0x0080 | 0x0010
                    
                    # Try to write config
                    try:
                        bus.write_i2c_block_data(self.address, 0x01, [
                            (config_val >> 8) & 0xFF,
                            config_val & 0xFF
                        ])
                        time.sleep(0.15)  # Wait for conversion
                    except Exception as write_err:
                        # If write fails, try reading anyway (might be in continuous mode)
                        print(f"DEBUG: Write failed for channel {ch}: {write_err}", file=sys.stderr)
                        time.sleep(0.05)
                    
                    # Read conversion result
                    result_data = bus.read_i2c_block_data(self.address, 0x00, 2)
                    raw_value = (result_data[0] << 8) | result_data[1]
                    # Convert to signed 16-bit
                    if raw_value & 0x8000:
                        raw_value = raw_value - 65536
                    # Convert to voltage (±4.096V range for ADS1115)
                    voltage = (raw_value / 32767.0) * 4.096
                    
                    channel_labels[ch].setText(f"{voltage:.4f} V")
                    channel_labels[ch].setStyleSheet("font-size: 18pt; font-weight: bold; color: #28a745; min-width: 200px;")
                    
                except Exception as e:
                    channel_labels[ch].setText(f"Error")
                    channel_labels[ch].setStyleSheet("font-size: 18pt; font-weight: bold; color: #dc3545; min-width: 200px;")
                    print(f"DEBUG: Error reading channel {ch}: {e}", file=sys.stderr)
            
            bus.close()
            
        except Exception as e:
            # Error accessing I2C bus
            error_msg = str(e)[:80]
            for ch in range(4):
                channel_labels[ch].setText(f"I2C Error")
                channel_labels[ch].setStyleSheet("font-size: 18pt; font-weight: bold; color: #dc3545; min-width: 200px;")
            print(f"DEBUG: I2C error: {e}", file=sys.stderr)

