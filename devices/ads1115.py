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
        
        # Connect button to read function
        def read_channels():
            """Read all ADC channels and update display."""
            # Try to use hardware manager's ADC first (more reliable)
            if self.hardware and hasattr(self.hardware, 'adc') and self.hardware.adc and self.hardware.adc.adc:
                try:
                    # Use existing ADC manager
                    readings = self.hardware.adc.read_all_channels()
                    for ch in range(4):
                        voltage = readings.get(ch, 0.0)
                        channel_labels[ch].setText(f"{voltage:.4f} V")
                        channel_labels[ch].setStyleSheet("font-size: 18pt; font-weight: bold; color: #28a745; min-width: 200px;")
                    return
                except Exception as e:
                    # Fall through to direct I2C method
                    pass
            
            # Fallback: Try direct I2C access
            try:
                from adafruit_ads1x15.ads1115 import ADS1115
                import board
                
                # Create I2C bus
                i2c = board.I2C()
                ads = ADS1115(i2c, address=self.address)
                
                # Read all channels
                for ch in range(4):
                    try:
                        # Read voltage (ADS1115 returns 16-bit signed value)
                        raw = ads.read(ch)
                        voltage = raw * 4.096 / 32768.0  # Convert to volts
                        channel_labels[ch].setText(f"{voltage:.4f} V")
                        channel_labels[ch].setStyleSheet("font-size: 18pt; font-weight: bold; color: #28a745; min-width: 200px;")
                    except Exception as e:
                        channel_labels[ch].setText(f"Error")
                        channel_labels[ch].setStyleSheet("font-size: 18pt; font-weight: bold; color: #dc3545; min-width: 200px;")
                        
            except ImportError:
                # Library not available - show mock data
                import random
                for ch in range(4):
                    mock_value = random.uniform(0, 3.3)
                    channel_labels[ch].setText(f"{mock_value:.4f} V (mock)")
                    channel_labels[ch].setStyleSheet("font-size: 18pt; font-weight: bold; color: #ffc107; min-width: 200px;")
            except Exception as e:
                # Error reading - show error
                error_msg = str(e)[:50]
                for ch in range(4):
                    channel_labels[ch].setText(f"Error: {error_msg}")
                    channel_labels[ch].setStyleSheet("font-size: 18pt; font-weight: bold; color: #dc3545; min-width: 200px;")
        
        test_button.clicked.connect(read_channels)
        layout.addWidget(test_button)
        
        layout.addStretch()
        widget.setLayout(layout)
        
        return widget

