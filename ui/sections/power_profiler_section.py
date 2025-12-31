"""Power profiler section for power measurement and test automation."""

from PySide6.QtWidgets import (QGroupBox, QVBoxLayout, QHBoxLayout, QPushButton,
                               QLabel, QTableWidget, QTableWidgetItem, QComboBox,
                               QSpinBox, QLineEdit, QTextEdit, QTabWidget, QWidget,
                               QHeaderView, QMessageBox)
from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtGui import QFont
from typing import Dict, List, Optional
import time


class PowerMeasurementWidget(QWidget):
    """Widget for displaying power measurements."""
    
    def __init__(self, profiler=None, parent=None):
        super().__init__(parent)
        self.profiler = profiler
        self.setup_ui()
        
        # Update timer for continuous measurement
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_measurements)
        self.measuring = False
    
    def setup_ui(self):
        """Set up the measurement UI."""
        layout = QVBoxLayout()
        layout.setSpacing(12)
        layout.setContentsMargins(15, 10, 15, 15)
        
        # Sensor management
        sensor_group = QGroupBox("Sensors")
        sensor_layout = QVBoxLayout()
        
        # Add sensor controls
        add_layout = QHBoxLayout()
        add_layout.addWidget(QLabel("Bus:"))
        self.bus_spinbox = QSpinBox()
        self.bus_spinbox.setMinimum(0)
        self.bus_spinbox.setMaximum(15)
        self.bus_spinbox.setValue(1)
        add_layout.addWidget(self.bus_spinbox)
        
        add_layout.addWidget(QLabel("Address:"))
        self.address_spinbox = QSpinBox()
        self.address_spinbox.setMinimum(0x40)
        self.address_spinbox.setMaximum(0x4F)
        self.address_spinbox.setValue(0x40)
        self.address_spinbox.setDisplayIntegerBase(16)
        add_layout.addWidget(self.address_spinbox)
        
        add_layout.addWidget(QLabel("Name:"))
        self.bus_name_edit = QLineEdit()
        self.bus_name_edit.setPlaceholderText("e.g., LCD, MCU, Motor")
        add_layout.addWidget(self.bus_name_edit)
        
        scan_button = QPushButton("Scan Bus")
        scan_button.clicked.connect(self.on_scan_bus)
        add_layout.addWidget(scan_button)
        
        add_button = QPushButton("Add Sensor")
        add_button.clicked.connect(self.on_add_sensor)
        add_layout.addWidget(add_button)
        
        sensor_layout.addLayout(add_layout)
        sensor_group.setLayout(sensor_layout)
        layout.addWidget(sensor_group)
        
        # Measurement display table
        self.measurement_table = QTableWidget()
        self.measurement_table.setColumnCount(5)
        self.measurement_table.setHorizontalHeaderLabels(["Bus", "Address", "Current (A)", "Voltage (V)", "Power (W)"])
        self.measurement_table.horizontalHeader().setStretchLastSection(True)
        self.measurement_table.setAlternatingRowColors(True)
        self.measurement_table.setStyleSheet("""
            QTableWidget {
                border: 2px solid #dee2e6;
                border-radius: 6px;
                background-color: white;
            }
            QTableWidget::item {
                padding: 8px;
            }
        """)
        layout.addWidget(self.measurement_table)
        
        # Control buttons
        control_layout = QHBoxLayout()
        
        self.start_button = QPushButton("Start Measurement")
        self.start_button.clicked.connect(self.on_start_measurement)
        control_layout.addWidget(self.start_button)
        
        self.stop_button = QPushButton("Stop Measurement")
        self.stop_button.clicked.connect(self.on_stop_measurement)
        self.stop_button.setEnabled(False)
        control_layout.addWidget(self.stop_button)
        
        self.single_button = QPushButton("Single Measurement")
        self.single_button.clicked.connect(self.on_single_measurement)
        control_layout.addWidget(self.single_button)
        
        layout.addLayout(control_layout)
        
        # Status label
        self.status_label = QLabel("Ready")
        self.status_label.setStyleSheet("""
            QLabel {
                color: #6c757d;
                padding: 8px;
                background-color: #f8f9fa;
                border-radius: 4px;
            }
        """)
        layout.addWidget(self.status_label)
        
        layout.addStretch()
        self.setLayout(layout)
    
    def on_scan_bus(self):
        """Scan bus for INA260 sensors."""
        if not self.profiler:
            return
        
        bus = self.bus_spinbox.value()
        addresses = self.profiler.scan_bus(bus)
        
        if addresses:
            msg = f"Found {len(addresses)} INA260 sensor(s) on bus {bus}: " + \
                  ", ".join([f"0x{addr:02X}" for addr in addresses])
            QMessageBox.information(self, "Scan Results", msg)
        else:
            QMessageBox.information(self, "Scan Results", f"No INA260 sensors found on bus {bus}")
    
    def on_add_sensor(self):
        """Add a sensor."""
        if not self.profiler:
            return
        
        bus = self.bus_spinbox.value()
        address = self.address_spinbox.value()
        bus_name = self.bus_name_edit.text().strip() or None
        
        if self.profiler.add_sensor(bus, address, bus_name):
            self.status_label.setText(f"Added sensor: Bus {bus}, Address 0x{address:02X}")
            self.update_measurements()
        else:
            QMessageBox.warning(self, "Error", f"Failed to add sensor on bus {bus}, address 0x{address:02X}")
    
    def on_start_measurement(self):
        """Start continuous measurement."""
        if not self.profiler:
            return
        
        self.profiler.start_continuous_measurement(interval=0.1)
        self.measuring = True
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        self.update_timer.start(100)  # Update every 100ms
        self.status_label.setText("Measuring...")
    
    def on_stop_measurement(self):
        """Stop continuous measurement."""
        if self.profiler:
            self.profiler.stop_continuous_measurement()
        self.measuring = False
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.update_timer.stop()
        self.status_label.setText("Stopped")
    
    def on_single_measurement(self):
        """Take a single measurement."""
        if not self.profiler:
            return
        
        self.profiler.take_measurement()
        self.update_measurements()
        self.status_label.setText("Single measurement taken")
    
    def update_measurements(self):
        """Update measurement display."""
        if not self.profiler:
            return
        
        measurements = self.profiler.get_all_measurements()
        
        self.measurement_table.setRowCount(len(measurements))
        
        for i, measurement in enumerate(measurements):
            bus_name = measurement.get('bus_name', f"Bus {measurement.get('bus', '?')}")
            address = measurement.get('address', 0)
            current = measurement.get('current', 0.0)
            voltage = measurement.get('voltage', 0.0)
            power = measurement.get('power', 0.0)
            
            self.measurement_table.setItem(i, 0, QTableWidgetItem(bus_name))
            self.measurement_table.setItem(i, 1, QTableWidgetItem(f"0x{address:02X}"))
            self.measurement_table.setItem(i, 2, QTableWidgetItem(f"{current:.6f}"))
            self.measurement_table.setItem(i, 3, QTableWidgetItem(f"{voltage:.3f}"))
            self.measurement_table.setItem(i, 4, QTableWidgetItem(f"{power:.6f}"))
        
        if measurements:
            self.status_label.setText(f"Showing {len(measurements)} sensor(s)")


class SequenceBuilderWidget(QWidget):
    """Widget for building test sequences."""
    
    def __init__(self, sequence_engine=None, parent=None):
        super().__init__(parent)
        self.sequence_engine = sequence_engine
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the sequence builder UI."""
        layout = QVBoxLayout()
        layout.setSpacing(12)
        layout.setContentsMargins(15, 10, 15, 15)
        
        # Sequence name
        name_layout = QHBoxLayout()
        name_layout.addWidget(QLabel("Sequence Name:"))
        self.sequence_name_edit = QLineEdit()
        self.sequence_name_edit.setPlaceholderText("Enter sequence name")
        name_layout.addWidget(self.sequence_name_edit)
        layout.addLayout(name_layout)
        
        # Action builder (simplified - can be expanded)
        action_group = QGroupBox("Add Action")
        action_layout = QVBoxLayout()
        
        action_type_layout = QHBoxLayout()
        action_type_layout.addWidget(QLabel("Action Type:"))
        self.action_type_combo = QComboBox()
        self.action_type_combo.addItems([
            "Delay",
            "GPIO Toggle",
            "ADC Read",
            "Power Measure",
            "UART Send",
            "UART Receive",
            "Conditional"
        ])
        action_type_layout.addWidget(self.action_type_combo)
        action_layout.addLayout(action_type_layout)
        
        add_action_button = QPushButton("Add Action")
        add_action_button.clicked.connect(self.on_add_action)
        action_layout.addWidget(add_action_button)
        
        action_group.setLayout(action_layout)
        layout.addWidget(action_group)
        
        # Sequence display
        self.sequence_text = QTextEdit()
        self.sequence_text.setReadOnly(True)
        self.sequence_text.setPlaceholderText("Sequence actions will appear here...")
        layout.addWidget(self.sequence_text)
        
        # Control buttons
        control_layout = QHBoxLayout()
        
        save_button = QPushButton("Save Sequence")
        save_button.clicked.connect(self.on_save_sequence)
        control_layout.addWidget(save_button)
        
        load_button = QPushButton("Load Sequence")
        load_button.clicked.connect(self.on_load_sequence)
        control_layout.addWidget(load_button)
        
        clear_button = QPushButton("Clear")
        clear_button.clicked.connect(self.on_clear_sequence)
        control_layout.addWidget(clear_button)
        
        layout.addLayout(control_layout)
        
        layout.addStretch()
        self.setLayout(layout)
    
    def on_add_action(self):
        """Add an action to the sequence."""
        # Simplified - would need full implementation
        action_type = self.action_type_combo.currentText()
        self.sequence_text.append(f"- {action_type}")
    
    def on_save_sequence(self):
        """Save sequence."""
        # TODO: Implement sequence saving
        QMessageBox.information(self, "Info", "Sequence saving not yet implemented")
    
    def on_load_sequence(self):
        """Load sequence."""
        # TODO: Implement sequence loading
        QMessageBox.information(self, "Info", "Sequence loading not yet implemented")
    
    def on_clear_sequence(self):
        """Clear sequence."""
        self.sequence_text.clear()


class PowerProfilerSection(QGroupBox):
    """Power profiler section with tabs for measurement and sequences."""
    
    def __init__(self, profiler=None, sequence_engine=None, parent=None):
        super().__init__("Power Profiler", parent)
        self.profiler = profiler
        self.sequence_engine = sequence_engine
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the power profiler UI."""
        layout = QVBoxLayout()
        layout.setSpacing(12)
        layout.setContentsMargins(15, 10, 15, 15)
        
        # Create tab widget
        self.tab_widget = QTabWidget()
        
        # Measurement tab
        self.measurement_widget = PowerMeasurementWidget(self.profiler)
        self.tab_widget.addTab(self.measurement_widget, "Measurements")
        
        # Sequence builder tab
        self.sequence_widget = SequenceBuilderWidget(self.sequence_engine)
        self.tab_widget.addTab(self.sequence_widget, "Sequences")
        
        layout.addWidget(self.tab_widget)
        self.setLayout(layout)
    
    def update_profiler(self, profiler):
        """Update profiler instance."""
        self.profiler = profiler
        if self.measurement_widget:
            self.measurement_widget.profiler = profiler
    
    def update_sequence_engine(self, sequence_engine):
        """Update sequence engine instance."""
        self.sequence_engine = sequence_engine
        if self.sequence_widget:
            self.sequence_widget.sequence_engine = sequence_engine

