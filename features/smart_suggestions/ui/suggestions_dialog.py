"""Suggestions dialog - UI for displaying and launching app suggestions."""

import sys
from typing import Optional, Dict, List
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QListWidget, QListWidgetItem, QGroupBox, QTextEdit, QWidget
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

from ..device_detector import DeviceDetector, DeviceInfo
from ..suggestion_engine import SuggestionEngine, Suggestion


class SuggestionsDialog(QDialog):
    """Dialog for displaying device suggestions and launching apps."""
    
    def __init__(self, hardware, parent=None):
        super().__init__(parent)
        self.hardware = hardware
        self.detector = DeviceDetector()
        self.engine = SuggestionEngine()
        self.running_apps: Dict[str, object] = {}  # app_class -> app instance
        
        self.setWindowTitle("App Suggestions")
        self.setMinimumSize(700, 600)
        self.resize(800, 700)
        
        self.setup_ui()
        self.scan_devices()
    
    def setup_ui(self):
        """Set up the UI layout."""
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(20, 15, 20, 20)
        
        # Title
        title = QLabel("App Suggestions")
        title_font = QFont()
        title_font.setPointSize(18)
        title_font.setBold(True)
        title.setFont(title_font)
        layout.addWidget(title)
        
        # Detected devices section
        devices_group = QGroupBox("Detected Devices")
        devices_layout = QVBoxLayout()
        self.devices_list = QListWidget()
        self.devices_list.setMaximumHeight(150)
        devices_layout.addWidget(self.devices_list)
        devices_group.setLayout(devices_layout)
        layout.addWidget(devices_group)
        
        # Suggestions section
        suggestions_group = QGroupBox("Suggested Apps")
        suggestions_layout = QVBoxLayout()
        self.suggestions_list = QListWidget()
        self.suggestions_list.setMinimumHeight(300)
        suggestions_layout.addWidget(self.suggestions_list)
        suggestions_group.setLayout(suggestions_layout)
        layout.addWidget(suggestions_group)
        
        # Running apps section
        running_group = QGroupBox("Running Apps")
        running_layout = QVBoxLayout()
        self.running_list = QListWidget()
        self.running_list.setMaximumHeight(100)
        running_layout.addWidget(self.running_list)
        running_group.setLayout(running_layout)
        layout.addWidget(running_group)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        refresh_button = QPushButton("Refresh")
        refresh_button.clicked.connect(self.scan_devices)
        button_layout.addWidget(refresh_button)
        
        close_button = QPushButton("Close")
        close_button.clicked.connect(self.accept)
        button_layout.addWidget(close_button)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
    def scan_devices(self):
        """Scan for devices and generate suggestions."""
        try:
            # Clear lists
            self.devices_list.clear()
            self.suggestions_list.clear()
            
            # Scan devices
            devices = self.detector.scan_all_devices(self.hardware)
            
            # Display devices
            if not devices:
                item = QListWidgetItem("No devices detected. Connect I2C devices and try again.")
                item.setForeground(Qt.GlobalColor.gray)
                self.devices_list.addItem(item)
            else:
                for device in devices:
                    category_str = f" [{device.category}]" if device.category else ""
                    text = f"0x{device.address:02X} - {device.device_name}{category_str} (Bus {device.bus})"
                    item = QListWidgetItem(text)
                    self.devices_list.addItem(item)
            
            # Generate suggestions
            suggestions = self.engine.generate_suggestions(devices)
            
            # Display suggestions
            if not suggestions:
                item = QListWidgetItem("No app suggestions available for detected devices.")
                item.setForeground(Qt.GlobalColor.gray)
                self.suggestions_list.addItem(item)
            else:
                for suggestion in suggestions:
                    # Create widget for suggestion
                    widget = self._create_suggestion_widget(suggestion, devices)
                    item = QListWidgetItem()
                    item.setSizeHint(widget.sizeHint())
                    self.suggestions_list.addItem(item)
                    self.suggestions_list.setItemWidget(item, widget)
        
        except Exception as e:
            print(f"Error scanning devices: {e}", file=sys.stderr)
            import traceback
            traceback.print_exc()
            
            error_item = QListWidgetItem(f"Error scanning devices: {e}")
            error_item.setForeground(Qt.GlobalColor.red)
            self.devices_list.addItem(error_item)
    
    def _create_suggestion_widget(self, suggestion: Suggestion, devices: List[DeviceInfo]) -> QWidget:
        """Create a widget for displaying a suggestion."""
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 5, 10, 5)
        
        # App name and description
        name_label = QLabel(f"<b>{suggestion.app_name}</b>")
        name_font = QFont()
        name_font.setPointSize(12)
        name_font.setBold(True)
        name_label.setFont(name_font)
        layout.addWidget(name_label)
        
        desc_label = QLabel(suggestion.description)
        desc_label.setWordWrap(True)
        layout.addWidget(desc_label)
        
        # Required devices
        req_text = "Requires: " + ", ".join(suggestion.required_devices)
        req_label = QLabel(req_text)
        req_label.setStyleSheet("color: #666; font-size: 10pt;")
        layout.addWidget(req_label)
        
        # Launch button
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        if suggestion.app_class in self.running_apps:
            stop_button = QPushButton("Stop")
            stop_button.clicked.connect(lambda: self.stop_app(suggestion.app_class))
            button_layout.addWidget(stop_button)
        else:
            launch_button = QPushButton("Launch")
            launch_button.clicked.connect(lambda: self.launch_app(suggestion.app_class, devices))
            button_layout.addWidget(launch_button)
        
        layout.addLayout(button_layout)
        
        widget.setLayout(layout)
        return widget
    
    def launch_app(self, app_class_name: str, devices: List[DeviceInfo]):
        """Launch an app."""
        try:
            # Import app class
            if app_class_name == "TiltGameApp":
                from ..apps.tilt_game import TiltGameApp
                app_class = TiltGameApp
            else:
                print(f"Unknown app class: {app_class_name}")
                return
            
            # Create app instance
            app = app_class()
            
            # Start app
            if app.start(self.hardware, devices):
                self.running_apps[app_class_name] = app
                self.update_running_apps()
                self.scan_devices()  # Refresh to show "Stop" button
                print(f"Launched app: {app_class_name}")
            else:
                print(f"Failed to start app: {app_class_name}")
        
        except Exception as e:
            print(f"Error launching app {app_class_name}: {e}", file=sys.stderr)
            import traceback
            traceback.print_exc()
    
    def stop_app(self, app_class_name: str):
        """Stop a running app."""
        try:
            if app_class_name in self.running_apps:
                app = self.running_apps[app_class_name]
                app.stop()
                del self.running_apps[app_class_name]
                self.update_running_apps()
                self.scan_devices()  # Refresh to show "Launch" button
                print(f"Stopped app: {app_class_name}")
        
        except Exception as e:
            print(f"Error stopping app {app_class_name}: {e}", file=sys.stderr)
    
    def update_running_apps(self):
        """Update the running apps list."""
        self.running_list.clear()
        
        if not self.running_apps:
            item = QListWidgetItem("No apps running")
            item.setForeground(Qt.GlobalColor.gray)
            self.running_list.addItem(item)
        else:
            for app_class_name in self.running_apps.keys():
                item = QListWidgetItem(app_class_name)
                self.running_list.addItem(item)
    
    def closeEvent(self, event):
        """Stop all apps when dialog closes."""
        try:
            for app in list(self.running_apps.values()):
                app.stop()
            self.running_apps.clear()
        except Exception as e:
            print(f"Error stopping apps on close: {e}")
        
        event.accept()

