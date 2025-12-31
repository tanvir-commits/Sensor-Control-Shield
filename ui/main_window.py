"""Main window for Device Panel application."""

import sys
from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                               QApplication, QTabWidget)
from PySide6.QtCore import QTimer, Qt

from .status_bar import StatusBar
from .sections.analog_section import AnalogSection
from .sections.led_section import LEDSection
from .sections.button_section import ButtonSection
from .sections.i2c_section import I2CSection
from .sections.spi_section import SPISection

# Optional device system
try:
    from config.device_config import ENABLE_DEVICE_SYSTEM
    if ENABLE_DEVICE_SYSTEM:
        try:
            from .device_tabs.device_tab import DeviceTab
            DEVICE_SYSTEM_AVAILABLE = True
        except Exception as e:
            print(f"Device system UI not available: {e}")
            DEVICE_SYSTEM_AVAILABLE = False
    else:
        DEVICE_SYSTEM_AVAILABLE = False
except Exception as e:
    # Config file doesn't exist or other error - try to load anyway
    try:
        from .device_tabs.device_tab import DeviceTab
        DEVICE_SYSTEM_AVAILABLE = True
    except Exception:
        DEVICE_SYSTEM_AVAILABLE = False


class MainWindow(QMainWindow):
    """Main application window."""
    
    def __init__(self, mock_hardware=None, branch=None, parent=None):
        super().__init__(parent)
        self.mock_hardware = mock_hardware
        self.hardware = mock_hardware  # Alias for clarity
        self.device_tabs = {}  # Track open device tabs: (bus, address) -> tab
        self.branch = branch or "unknown"  # Current git branch
        
        # Set window title with branch name
        title = f"Device Panel [{self.branch}]"
        self.setWindowTitle(title)
        self.setMinimumSize(900, 850)
        self.resize(1000, 1100)  # Start taller - increased height
        
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
        # Create hardware widget (existing functionality)
        hardware_widget = self.create_hardware_widget()
        
        # Create tab widget if device system available
        if DEVICE_SYSTEM_AVAILABLE:
            self.tab_widget = QTabWidget()
            # Set larger font for main tabs
            tab_font = self.tab_widget.font()
            tab_font.setPointSize(11)
            tab_font.setBold(True)
            self.tab_widget.setFont(tab_font)
            self.tab_widget.setStyleSheet("""
                QTabWidget::pane {
                    border: 1px solid #ddd;
                    border-radius: 4px;
                }
                QTabBar::tab {
                    padding: 10px 20px;
                    margin-right: 2px;
                    font-size: 11pt;
                    font-weight: bold;
                    min-width: 100px;
                }
                QTabBar::tab:selected {
                    background: #007bff;
                    color: white;
                }
                QTabBar::tab:hover {
                    background: #e3f2fd;
                }
            """)
            self.tab_widget.addTab(hardware_widget, "Hardware")
            self.tab_widget.setTabsClosable(True)
            self.tab_widget.tabCloseRequested.connect(self.on_tab_close_requested)
            self.setCentralWidget(self.tab_widget)
        else:
            # No device system - use single widget (backward compatible)
            self.setCentralWidget(hardware_widget)
    
    def create_hardware_widget(self):
        """Create the hardware control widget (existing functionality)."""
        widget = QWidget()
        main_layout = QVBoxLayout()
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(20, 15, 20, 20)
        
        # Status bar at top (pass branch for display)
        self.status_bar = StatusBar(branch=self.branch)
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
        # Connect device_clicked signal (handler checks if system available)
        self.i2c_section.device_clicked.connect(self.on_device_clicked)
        print(f"DEBUG: Connected device_clicked signal, DEVICE_SYSTEM_AVAILABLE={DEVICE_SYSTEM_AVAILABLE}", file=sys.stderr)
        bus_row.addWidget(self.i2c_section)
        
        self.spi_section = SPISection()
        self.spi_section.test_requested.connect(self.on_spi_test)
        bus_row.addWidget(self.spi_section)
        
        content_layout.addLayout(bus_row)
        
        content_layout.addStretch()
        
        main_layout.addLayout(content_layout)
        widget.setLayout(main_layout)
        return widget
    
    def update_all(self):
        """Update all UI elements with current hardware state."""
        try:
            if not self.mock_hardware:
                return
            
            # Update analog readings (skip if slow to avoid blocking buttons/LEDs)
            # ADC can take 1+ seconds, so we skip it in the main update loop
            # TODO: Move ADC to separate slower timer if needed
            # if hasattr(self.mock_hardware, 'adc'):
            #     try:
            #         readings = self.mock_hardware.adc.read_all_channels()
            #         self.analog_section.update_readings(readings)
            #     except:
            #         pass
            
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
                try:
                    i2c_status = self.mock_hardware.i2c.get_status()
                    color = "#4CAF50" if i2c_status == "OK" else "#666"
                    self.status_bar.update_status("I²C", i2c_status, color)
                except:
                    self.status_bar.update_status("I²C", "NOT VERIFIED", "#666")
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
            try:
                # Perform actual I2C scan
                devices = self.mock_hardware.i2c.scan()
                bus_num = self.mock_hardware.i2c.bus
                status = "OK" if devices else "NO_DEVICES"
                self.i2c_section.update_results(devices, status, bus_num)
                
                # Dynamically resize window if devices are found and window is too small
                if devices and len(devices) > 0:
                    current_height = self.height()
                    # If window is less than 900px tall, grow it to accommodate devices
                    if current_height < 900:
                        new_height = max(900, current_height + 50)
                        self.resize(self.width(), new_height)
                
                # Update status bar
                if devices:
                    self.status_bar.update_status("I²C", f"OK ({len(devices)} devices)", "#4CAF50")
                else:
                    self.status_bar.update_status("I²C", "NO DEVICES", "#ff9800")
            except RuntimeError as e:
                # Specific error message from scanner
                error_msg = str(e)
                self.i2c_section.update_results([], "ERROR")
                self.status_bar.update_status("I²C", "ERROR", "#f44336")
                print(f"I2C scan error: {error_msg}", file=sys.stderr)
            except Exception as e:
                # Generic error
                self.i2c_section.update_results([], "ERROR")
                self.status_bar.update_status("I²C", "ERROR", "#f44336")
                print(f"I2C scan error: {e}", file=sys.stderr)
    
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
    
    def on_device_clicked(self, address: int, bus: int):
        """Handle device click - open device tab."""
        print(f"DEBUG: on_device_clicked called with address=0x{address:02X}, bus={bus}", file=sys.stderr)
        
        if not DEVICE_SYSTEM_AVAILABLE:
            print("DEBUG: Device system not available", file=sys.stderr)
            return
        
        # Check if tab widget exists
        if not hasattr(self, 'tab_widget'):
            print("DEBUG: No tab_widget found", file=sys.stderr)
            return
        
        # Check if tab already exists
        tab_key = (bus, address)
        if tab_key in self.device_tabs:
            # Tab exists - switch to it
            print(f"DEBUG: Tab already exists, switching to it", file=sys.stderr)
            for i in range(self.tab_widget.count()):
                if self.tab_widget.widget(i) == self.device_tabs[tab_key]:
                    self.tab_widget.setCurrentIndex(i)
                    break
            return
        
        # Create new device tab
        try:
            print(f"DEBUG: Creating new device tab", file=sys.stderr)
            device_tab = DeviceTab(bus, address, hardware=self.hardware)
            tab_title = f"Device: 0x{address:02X}"
            
            index = self.tab_widget.addTab(device_tab, tab_title)
            self.tab_widget.setCurrentIndex(index)
            self.device_tabs[tab_key] = device_tab
            print(f"DEBUG: Device tab created successfully at index {index}", file=sys.stderr)
        except Exception as e:
            import traceback
            print(f"ERROR: Error opening device tab: {e}", file=sys.stderr)
            traceback.print_exc(file=sys.stderr)
    
    def on_tab_close_requested(self, index: int):
        """Handle tab close request."""
        if not hasattr(self, 'tab_widget'):
            return
        
        widget = self.tab_widget.widget(index)
        if widget is None:
            return
        
        # Don't allow closing the Hardware tab (index 0)
        if index == 0:
            return
        
        # Remove from device_tabs dict
        for key, tab in list(self.device_tabs.items()):
            if tab == widget:
                del self.device_tabs[key]
                break
        
        # Remove tab
        self.tab_widget.removeTab(index)

