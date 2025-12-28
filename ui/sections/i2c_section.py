"""I2C bus scanning section."""

from PySide6.QtWidgets import (QGroupBox, QVBoxLayout, QPushButton, 
                               QListWidget, QLabel, QListWidgetItem)
from PySide6.QtCore import Qt, Signal


class I2CSection(QGroupBox):
    """Section for I2C bus scanning."""
    
    # Signal emitted when scan is requested
    scan_requested = Signal()
    # Signal emitted when device is clicked (address, bus)
    device_clicked = Signal(int, int)
    
    def __init__(self, parent=None):
        super().__init__("I²C", parent)
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the UI layout."""
        layout = QVBoxLayout()
        layout.setSpacing(12)
        layout.setContentsMargins(15, 10, 15, 15)
        
        # Scan button
        scan_button = QPushButton("Scan I²C")
        scan_button.setMinimumHeight(45)
        font = scan_button.font()
        font.setPointSize(11)
        font.setBold(True)
        scan_button.setFont(font)
        scan_button.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #007bff, stop:1 #0056b3);
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #0056b3, stop:1 #004085);
            }
            QPushButton:pressed {
                background: #004085;
            }
        """)
        scan_button.clicked.connect(self._on_scan_clicked)
        self.scan_button = scan_button
        layout.addWidget(scan_button)
        
        # Bus selector (if multiple buses available)
        self.bus_label = QLabel("Bus: Auto")
        self.bus_label.setStyleSheet("""
            QLabel {
                color: #666;
                font-size: 9pt;
                padding: 4px;
            }
        """)
        layout.addWidget(self.bus_label)
        
        # Results list
        self.results_list = QListWidget()
        self.results_list.setMaximumHeight(180)  # Increased to accommodate larger font
        self.results_list.setAlternatingRowColors(True)
        # Set larger font for device addresses
        font = self.results_list.font()
        font.setPointSize(14)
        font.setBold(True)
        font.setFamily("Segoe UI, Arial, sans-serif")
        self.results_list.setFont(font)
        self.results_list.setStyleSheet("""
            QListWidget {
                border: 2px solid #dee2e6;
                border-radius: 6px;
                background-color: white;
                padding: 5px;
            }
            QListWidget::item {
                padding: 8px;
                border-radius: 4px;
            }
            QListWidget::item:selected {
                background-color: #007bff;
                color: white;
            }
            QListWidget::item:hover {
                background-color: #e3f2fd;
                cursor: pointer;
            }
        """)
        # Make items clickable (double-click to open device tab)
        self.results_list.itemDoubleClicked.connect(self.on_device_double_clicked)
        layout.addWidget(self.results_list)
        
        # Store current bus number for device clicks
        self.current_bus = None
        
        # Status message
        self.status_label = QLabel("Ready to scan")
        self.status_label.setWordWrap(True)
        self.status_label.setStyleSheet("""
            QLabel {
                color: #6c757d;
                padding: 8px;
                background-color: #f8f9fa;
                border-radius: 4px;
                font-size: 10pt;
            }
        """)
        layout.addWidget(self.status_label)
        
        layout.addStretch()
        self.setLayout(layout)
    
    def _on_scan_clicked(self):
        """Handle scan button click - provide visual feedback."""
        self.scan_button.setEnabled(False)
        self.scan_button.setText("Scanning...")
        self.status_label.setText("Scanning I²C bus...")
        self.results_list.clear()
        # Emit signal to trigger actual scan
        self.scan_requested.emit()
    
    def update_results(self, devices: list, status: str = "OK", bus_num: int = None):
        """Update I2C scan results.
        
        Args:
            devices: List of device addresses (integers)
            status: Status string ("OK", "NO_DEVICES", "ERROR")
            bus_num: I2C bus number used for scan
        """
        # Re-enable scan button
        self.scan_button.setEnabled(True)
        self.scan_button.setText("Scan I²C")
        
        # Update bus label
        if bus_num is not None:
            self.bus_label.setText(f"Bus: {bus_num}")
            self.current_bus = bus_num
        
        self.results_list.clear()
        
        if status == "ERROR":
            self.status_label.setText("Bus error (check wiring/power/pull-ups)")
            self.status_label.setStyleSheet("""
                QLabel {
                    color: #dc3545;
                    padding: 8px;
                    background-color: #f8d7da;
                    border: 1px solid #f5c6cb;
                    border-radius: 4px;
                    font-weight: bold;
                    font-size: 10pt;
                }
            """)
        elif not devices:
            self.status_label.setText("No devices found")
            self.status_label.setStyleSheet("""
                QLabel {
                    color: #856404;
                    padding: 8px;
                    background-color: #fff3cd;
                    border: 1px solid #ffeaa7;
                    border-radius: 4px;
                    font-size: 10pt;
                }
            """)
        else:
            count = len(devices)
            self.status_label.setText(f"Found {count} device(s)")
            self.status_label.setStyleSheet("""
                QLabel {
                    color: #155724;
                    padding: 8px;
                    background-color: #d4edda;
                    border: 1px solid #c3e6cb;
                    border-radius: 4px;
                    font-weight: bold;
                    font-size: 10pt;
                }
            """)
            
            # Add devices to list with suggestions
            try:
                from devices.registry import get_registry
                registry = get_registry()
                for addr in devices:
                    suggestions = registry.lookup(addr)
                    if suggestions:
                        device_name = suggestions[0][0]
                        if device_name == "Unknown Device":
                            text = f"0x{addr:02X}"
                        else:
                            text = f"0x{addr:02X} - {device_name}"
                    else:
                        text = f"0x{addr:02X}"
                    item = QListWidgetItem(text)
                    item.setData(Qt.ItemDataRole.UserRole, addr)  # Store address
                    self.results_list.addItem(item)
            except Exception as e:
                # Fallback if device system not available - still use QListWidgetItem
                import sys
                print(f"Warning: Device registry not available: {e}", file=sys.stderr)
                for addr in devices:
                    item = QListWidgetItem(f"0x{addr:02X}")
                    item.setData(Qt.ItemDataRole.UserRole, addr)  # Store address for double-click
                    self.results_list.addItem(item)
    
    def on_device_double_clicked(self, item: QListWidgetItem):
        """Handle device double-click to open device tab."""
        import sys
        print(f"DEBUG: Device double-clicked: {item.text()}", file=sys.stderr)
        
        if self.current_bus is None:
            print(f"DEBUG: current_bus is None, cannot open device tab", file=sys.stderr)
            return
        
        address = item.data(Qt.ItemDataRole.UserRole)
        print(f"DEBUG: Address from item data: {address}, bus: {self.current_bus}", file=sys.stderr)
        
        if address is not None:
            print(f"DEBUG: Emitting device_clicked signal: address=0x{address:02X}, bus={self.current_bus}", file=sys.stderr)
            self.device_clicked.emit(address, self.current_bus)
        else:
            print(f"DEBUG: Address is None, cannot emit signal", file=sys.stderr)

