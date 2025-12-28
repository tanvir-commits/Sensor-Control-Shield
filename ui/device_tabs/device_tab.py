"""Device tab for individual I2C devices."""

from typing import Optional, List, Tuple
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                               QPushButton, QComboBox, QTabWidget, QTextEdit,
                               QLineEdit, QGroupBox)
from PySide6.QtCore import Qt
from devices.base import DevicePlugin
from devices.registry import get_registry
from devices.loader import get_loader


class DeviceTab(QWidget):
    """Tab widget for a single I2C device."""
    
    def __init__(self, bus: int, address: int, parent=None):
        super().__init__(parent)
        self.bus = bus
        self.address = address
        self.registry = get_registry()
        self.loader = get_loader()
        self.device: Optional[DevicePlugin] = None
        self.selected_plugin_name: Optional[str] = None
        
        self.setup_ui()
        self.load_suggestions()
    
    def setup_ui(self):
        """Set up the UI layout."""
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(20, 15, 20, 20)
        
        # Header
        header = QHBoxLayout()
        title = QLabel(f"Device: 0x{self.address:02X}")
        title.setStyleSheet("font-size: 16pt; font-weight: bold;")
        header.addWidget(title)
        header.addStretch()
        layout.addLayout(header)
        
        # Device selection (if multiple suggestions)
        self.device_combo = QComboBox()
        self.device_combo.currentTextChanged.connect(self.on_device_selected)
        layout.addWidget(self.device_combo)
        
        # Tab widget for device sections
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #ddd;
                border-radius: 4px;
                background: white;
            }
            QTabBar::tab {
                padding: 8px 16px;
                margin-right: 2px;
            }
            QTabBar::tab:selected {
                background: #007bff;
                color: white;
            }
        """)
        
        # Info tab
        self.info_widget = QWidget()
        self.info_layout = QVBoxLayout()
        self.info_widget.setLayout(self.info_layout)
        self.tabs.addTab(self.info_widget, "Info")
        
        # Test tab
        self.test_widget = QWidget()
        self.test_layout = QVBoxLayout()
        self.test_widget.setLayout(self.test_layout)
        self.tabs.addTab(self.test_widget, "Test")
        
        layout.addWidget(self.tabs)
        self.setLayout(layout)
    
    def load_suggestions(self):
        """Load device suggestions for this address."""
        suggestions = self.registry.lookup(self.address)
        
        self.device_combo.clear()
        for device_name, plugin_name in suggestions:
            display_text = device_name
            if plugin_name:
                display_text += " (Plugin available)"
            self.device_combo.addItem(display_text, plugin_name)
        
        # Auto-select first suggestion and load plugin
        if suggestions:
            self.on_device_selected(0)
    
    def on_device_selected(self, index: int):
        """Handle device selection."""
        plugin_name = self.device_combo.itemData(index)
        self.selected_plugin_name = plugin_name
        
        # Clear existing content
        self.clear_tabs()
        
        if plugin_name:
            # Try to load plugin
            self.device = self.loader.create_device(self.bus, self.address, plugin_name)
            if self.device:
                self.load_device_info()
                self.load_device_test()
            else:
                self.show_no_plugin()
        else:
            self.show_unknown_device()
    
    def clear_tabs(self):
        """Clear tab content."""
        # Clear info tab
        while self.info_layout.count():
            item = self.info_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        # Clear test tab
        while self.test_layout.count():
            item = self.test_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
    
    def load_device_info(self):
        """Load device information."""
        if not self.device:
            return
        
        info = self.device.get_info()
        
        # Create info display
        info_group = QGroupBox("Device Information")
        info_layout = QVBoxLayout()
        
        for key, value in info.items():
            row = QHBoxLayout()
            label = QLabel(f"{key.replace('_', ' ').title()}:")
            label.setStyleSheet("font-weight: bold; min-width: 120px;")
            value_label = QLabel(str(value))
            row.addWidget(label)
            row.addWidget(value_label)
            row.addStretch()
            info_layout.addLayout(row)
        
        info_group.setLayout(info_layout)
        self.info_layout.addWidget(info_group)
        self.info_layout.addStretch()
    
    def load_device_test(self):
        """Load device test interface."""
        if not self.device:
            return
        
        try:
            test_ui = self.device.get_test_ui()
            if test_ui:
                self.test_layout.addWidget(test_ui)
            else:
                self.show_no_test_interface()
        except Exception as e:
            error_label = QLabel(f"Error loading test interface: {e}")
            error_label.setStyleSheet("color: red; padding: 10px;")
            self.test_layout.addWidget(error_label)
        
        self.test_layout.addStretch()
    
    def show_no_plugin(self):
        """Show message when no plugin available."""
        label = QLabel(
            "No plugin available for this device.\n\n"
            "You can:\n"
            "• Create a custom plugin\n"
            "• Load a plugin file\n"
            "• Check for community plugins"
        )
        label.setWordWrap(True)
        label.setStyleSheet("padding: 20px; color: #666;")
        self.info_layout.addWidget(label)
        self.info_layout.addStretch()
    
    def show_unknown_device(self):
        """Show message for unknown device."""
        label = QLabel(
            f"Unknown device at address 0x{self.address:02X}.\n\n"
            "This device is not in the registry.\n"
            "You can create a custom plugin to support it."
        )
        label.setWordWrap(True)
        label.setStyleSheet("padding: 20px; color: #666;")
        self.info_layout.addWidget(label)
        self.info_layout.addStretch()
    
    def show_no_test_interface(self):
        """Show message when device has no test interface."""
        label = QLabel("This device does not provide a test interface.")
        label.setStyleSheet("padding: 20px; color: #666;")
        self.test_layout.addWidget(label)

