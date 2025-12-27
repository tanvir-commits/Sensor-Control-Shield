"""I2C bus scanning section."""

from PySide6.QtWidgets import (QGroupBox, QVBoxLayout, QPushButton, 
                               QListWidget, QLabel)
from PySide6.QtCore import Qt, Signal


class I2CSection(QGroupBox):
    """Section for I2C bus scanning."""
    
    # Signal emitted when scan is requested
    scan_requested = Signal()
    
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
        scan_button.clicked.connect(self.scan_requested.emit)
        layout.addWidget(scan_button)
        
        # Results list
        self.results_list = QListWidget()
        self.results_list.setMaximumHeight(120)
        self.results_list.setAlternatingRowColors(True)
        self.results_list.setStyleSheet("""
            QListWidget {
                border: 2px solid #dee2e6;
                border-radius: 6px;
                background-color: white;
                padding: 5px;
            }
            QListWidget::item {
                padding: 6px;
                border-radius: 4px;
            }
            QListWidget::item:selected {
                background-color: #007bff;
                color: white;
            }
        """)
        layout.addWidget(self.results_list)
        
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
    
    def update_results(self, devices: list, status: str = "OK"):
        """Update I2C scan results.
        
        Args:
            devices: List of device addresses (integers)
            status: Status string ("OK", "NO_DEVICES", "ERROR")
        """
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
            
            # Add devices to list
            for addr in devices:
                self.results_list.addItem(f"0x{addr:02X}")

