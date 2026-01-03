"""Main window for Device Panel application."""

import sys
from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                               QApplication, QTabWidget, QMenuBar, QMenu)
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

# Optional test sequences feature
try:
    from config.feature_flags import ENABLE_TEST_SEQUENCES
    if ENABLE_TEST_SEQUENCES:
        try:
            from .sections.qa_test_sequences_section import QATestSequencesSection
            TEST_SEQUENCES_AVAILABLE = True
        except Exception as e:
            print(f"Test sequences UI not available: {e}")
            TEST_SEQUENCES_AVAILABLE = False
    else:
        TEST_SEQUENCES_AVAILABLE = False
except Exception as e:
    TEST_SEQUENCES_AVAILABLE = False

# Optional smart suggestions feature
try:
    from config.feature_flags import ENABLE_SMART_SUGGESTIONS
    if ENABLE_SMART_SUGGESTIONS:
        try:
            from features.smart_suggestions.ui.suggestions_dialog import SuggestionsDialog
            SMART_SUGGESTIONS_AVAILABLE = True
        except Exception as e:
            print(f"Smart suggestions UI not available: {e}")
            SMART_SUGGESTIONS_AVAILABLE = False
    else:
        SMART_SUGGESTIONS_AVAILABLE = False
except Exception as e:
    SMART_SUGGESTIONS_AVAILABLE = False


class MainWindow(QMainWindow):
    """Main application window."""
    
    def __init__(self, mock_hardware=None, branch=None, parent=None):
        super().__init__(parent)
        self.mock_hardware = mock_hardware
        self.hardware = mock_hardware  # Alias for clarity
        self.device_tabs = {}  # Track open device tabs: (bus, address) -> tab
        self.branch = branch or "unknown"  # Current git branch
        
        # Set window title with branch name
        title = f"DeviceOps [{self.branch}]"
        self.setWindowTitle(title)
        self.setMinimumSize(900, 850)
        
        # Set initial size, but respect screen bounds
        initial_width = 1000
        initial_height = 1100
        
        # If screen is available, constrain to screen size
        if QApplication.instance() and QApplication.instance().primaryScreen():
            screen_geometry = QApplication.instance().primaryScreen().availableGeometry()
            max_width = screen_geometry.width()
            max_height = screen_geometry.height()
            # Use smaller of desired size or available screen space
            initial_width = min(initial_width, max_width - 50)  # Leave 50px margin
            initial_height = min(initial_height, max_height - 50)  # Leave 50px margin
        
        self.resize(initial_width, initial_height)
        
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
        
        # Setup menu bar
        self.setup_menu_bar()
        
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
        
        # Create tab widget if device system or test sequences available
        if DEVICE_SYSTEM_AVAILABLE or TEST_SEQUENCES_AVAILABLE:
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
            
            # Add test sequences tab if available
            if TEST_SEQUENCES_AVAILABLE:
                try:
                    qa_engine = getattr(self.mock_hardware, 'qa_engine', None)
                    profile_manager = getattr(self.mock_hardware, 'dut_profile_manager', None)
                    sequence_builder = getattr(self.mock_hardware, 'sequence_builder', None)
                    results_manager = getattr(self.mock_hardware, 'results_manager', None)
                    self.qa_test_sequences_section = QATestSequencesSection(
                        qa_engine=qa_engine,
                        profile_manager=profile_manager,
                        sequence_builder=sequence_builder,
                        results_manager=results_manager
                    )
                    self.tab_widget.addTab(self.qa_test_sequences_section, "QA Test Sequences")
                except Exception as e:
                    print(f"Failed to create test sequences tab: {e}", file=sys.stderr)
            
            self.tab_widget.setTabsClosable(True)
            self.tab_widget.tabCloseRequested.connect(self.on_tab_close_requested)
            
            # Set size policy on tab widget to prevent vertical overflow
            from PySide6.QtWidgets import QSizePolicy
            self.tab_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Maximum)
            
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
        
        # Add stretch at the end for proper spacing, but limit widget height
        content_layout.addStretch()
        
        main_layout.addLayout(content_layout)
        widget.setLayout(main_layout)
        
        # Set size policy to prevent vertical expansion beyond screen
        from PySide6.QtWidgets import QSizePolicy
        widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Maximum)
        
        # Calculate maximum height based on screen size
        # This prevents overflow while allowing proper spacing
        if self.screen():
            try:
                screen_height = self.screen().availableGeometry().height()
                # Reserve space for window chrome, menu bar, status bar, etc. (about 150px)
                max_height = screen_height - 150
                widget.setMaximumHeight(max_height)
            except:
                # Fallback if screen info not available
                widget.setMaximumHeight(800)
        else:
            # Fallback if screen not yet available
            widget.setMaximumHeight(800)
        
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
        
        # Don't allow closing the QA Test Sequences tab
        if TEST_SEQUENCES_AVAILABLE and hasattr(self, 'qa_test_sequences_section'):
            if widget == self.qa_test_sequences_section:
                return
            return
        
        # Remove from device_tabs dict
        for key, tab in list(self.device_tabs.items()):
            if tab == widget:
                del self.device_tabs[key]
                break
        
        # Remove tab
        self.tab_widget.removeTab(index)
    
    def setup_menu_bar(self):
        """Set up the menu bar."""
        menu_bar = QMenuBar(self)
        self.setMenuBar(menu_bar)
        
        # Tools menu
        if SMART_SUGGESTIONS_AVAILABLE:
            tools_menu = menu_bar.addMenu("Tools")
            show_suggestions_action = tools_menu.addAction("Show App Suggestions...")
            show_suggestions_action.triggered.connect(self.show_app_suggestions)
    
    def show_app_suggestions(self):
        """Show the app suggestions dialog."""
        if not SMART_SUGGESTIONS_AVAILABLE:
            return
        
        try:
            dialog = SuggestionsDialog(self.hardware, parent=self)
            dialog.exec()
        except Exception as e:
            import traceback
            print(f"Error showing app suggestions: {e}", file=sys.stderr)
            traceback.print_exc(file=sys.stderr)

