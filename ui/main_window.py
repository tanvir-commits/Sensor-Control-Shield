"""Main window for Device Panel application."""

import sys
from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                               QApplication)
from PySide6.QtCore import QTimer, Qt

from .status_bar import StatusBar
from .sections.analog_section import AnalogSection
from .sections.led_section import LEDSection
from .sections.button_section import ButtonSection
from .sections.i2c_section import I2CSection
from .sections.spi_section import SPISection


class MainWindow(QMainWindow):
    """Main application window."""
    
    def __init__(self, mock_hardware=None, parent=None):
        super().__init__(parent)
        self.mock_hardware = mock_hardware
        
        self.setWindowTitle("Device Panel")
        self.setMinimumSize(900, 700)
        self.resize(1000, 750)
        
        # Apply modern styling
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f8f9fa;
            }
            QGroupBox {
                font-weight: 600;
                font-size: 13pt;
                color: #2c3e50;
                border: 2px solid #e0e0e0;
                border-radius: 8px;
                margin-top: 12px;
                padding-top: 15px;
                background-color: white;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 8px 0 8px;
                color: #34495e;
            }
        """)
        
        # Setup UI
        self.setup_ui()
        
        # Setup update timer (10Hz = 100ms)
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_all)
        
        # Initial update (after UI is set up)
        QTimer.singleShot(100, self.update_all)  # Delay first update
        
        # Start timer after a short delay to ensure window is ready
        QTimer.singleShot(200, lambda: self.update_timer.start(100))
    
    def setup_ui(self):
        """Set up the main UI layout."""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout()
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(20, 15, 20, 20)
        
        # Status bar at top
        self.status_bar = StatusBar()
        main_layout.addWidget(self.status_bar)
        
        # Content area
        content_layout = QVBoxLayout()
        content_layout.setSpacing(20)
        
        # Analog section (full width)
        self.analog_section = AnalogSection()
        content_layout.addWidget(self.analog_section)
        
        # Digital section row (LEDs and Buttons side by side)
        digital_row = QHBoxLayout()
        digital_row.setSpacing(15)
        
        self.led_section = LEDSection()
        self.led_section.led_changed.connect(self.on_led_changed)
        digital_row.addWidget(self.led_section)
        
        self.button_section = ButtonSection()
        digital_row.addWidget(self.button_section)
        
        content_layout.addLayout(digital_row)
        
        # Bus tools row (I2C and SPI side by side)
        bus_row = QHBoxLayout()
        bus_row.setSpacing(15)
        
        self.i2c_section = I2CSection()
        self.i2c_section.scan_requested.connect(self.on_i2c_scan)
        bus_row.addWidget(self.i2c_section)
        
        self.spi_section = SPISection()
        self.spi_section.test_requested.connect(self.on_spi_test)
        bus_row.addWidget(self.spi_section)
        
        content_layout.addLayout(bus_row)
        
        content_layout.addStretch()
        
        main_layout.addLayout(content_layout)
        central_widget.setLayout(main_layout)
    
    def update_all(self):
        """Update all UI elements with current hardware state."""
        try:
            if not self.mock_hardware:
                return
            
            # Update analog readings
            if hasattr(self.mock_hardware, 'adc'):
                readings = self.mock_hardware.adc.read_all_channels()
                self.analog_section.update_readings(readings)
            
            # Update button states
            if hasattr(self.mock_hardware, 'gpio'):
                button_states = {
                    1: self.mock_hardware.gpio.get_button(1),
                    2: self.mock_hardware.gpio.get_button(2)
                }
                self.button_section.update_states(button_states)
            
            # Update LED states (sync UI with hardware state)
            if hasattr(self.mock_hardware, 'gpio'):
                for led_id in [1, 2, 3, 4]:
                    state = self.mock_hardware.gpio.get_led(led_id)
                    self.led_section.set_led_state(led_id, state)
            
            # Update status bar
            if hasattr(self.mock_hardware, 'power'):
                power_state = "ON" if self.mock_hardware.power.get_power() else "OFF"
                color = "#4CAF50" if self.mock_hardware.power.get_power() else "#666"
                self.status_bar.update_status("Sensor Power", power_state, color)
            
            if hasattr(self.mock_hardware, 'i2c'):
                i2c_status = self.mock_hardware.i2c.get_status()
                color = "#4CAF50" if i2c_status == "OK" else "#666"
                self.status_bar.update_status("I²C", i2c_status, color)
        except Exception as e:
            # Log error but don't crash - just skip this update cycle
            import traceback
            print(f"Error in update_all: {e}", file=sys.stderr)
            traceback.print_exc()
    
    def on_led_changed(self, led_id: int, state: bool):
        """Handle LED state change from UI."""
        if self.mock_hardware and hasattr(self.mock_hardware, 'gpio'):
            self.mock_hardware.gpio.set_led(led_id, state)
    
    def on_i2c_scan(self):
        """Handle I2C scan request."""
        if self.mock_hardware and hasattr(self.mock_hardware, 'i2c'):
            devices = self.mock_hardware.i2c.scan()
            status = "OK" if devices else "NO_DEVICES"
            self.i2c_section.update_results(devices, status)
            
            # Update status bar
            if devices:
                self.status_bar.update_status("I²C", f"OK ({len(devices)} devices)", "#4CAF50")
            else:
                self.status_bar.update_status("I²C", "NO DEVICES", "#ff9800")
    
    def on_spi_test(self):
        """Handle SPI test request."""
        if self.mock_hardware and hasattr(self.mock_hardware, 'spi'):
            results = self.mock_hardware.spi.test()
            self.spi_section.update_results(results)
            
            # Update status bar
            status = results.get("status", "NOT VERIFIED")
            if status == "OK":
                self.status_bar.update_status("SPI", "OK", "#4CAF50")
            elif status == "NOT VERIFIED":
                self.status_bar.update_status("SPI", "NOT VERIFIED", "#ff9800")
            else:
                self.status_bar.update_status("SPI", "ERROR", "#f44336")

