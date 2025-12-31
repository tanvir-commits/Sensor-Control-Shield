"""Top status bar widget."""

from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel
from PySide6.QtCore import Qt
import socket


class StatusBar(QWidget):
    """Status bar showing system health indicators."""
    
    def __init__(self, branch=None, parent=None):
        super().__init__(parent)
        self.status_labels = {}
        self.branch = branch or "unknown"
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the UI layout."""
        layout = QHBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(10, 5, 10, 5)
        
        # Sensor Power status
        self.add_status_item(layout, "Sensor Power", "OFF", self.status_labels)
        
        # I2C status
        self.add_status_item(layout, "I²C", "NOT VERIFIED", self.status_labels)
        
        # SPI status
        self.add_status_item(layout, "SPI", "NOT VERIFIED", self.status_labels)
        
        # UART status (optional)
        self.add_status_item(layout, "UART", "NOT CONFIGURED", self.status_labels)
        
        # Spacer
        layout.addStretch()
        
        # Branch indicator (color-coded by branch type)
        branch_color = self.get_branch_color(self.branch)
        branch_label = QLabel(f"Branch: {self.branch}")
        branch_font = branch_label.font()
        branch_font.setPointSize(10)
        branch_font.setBold(True)
        branch_label.setFont(branch_font)
        branch_label.setStyleSheet(f"""
            QLabel {{
                color: {branch_color};
                padding: 6px 12px;
                background-color: #e3f2fd;
                border: 1px solid #90caf9;
                border-radius: 4px;
                font-weight: bold;
            }}
        """)
        layout.addWidget(branch_label)
        self.status_labels["Branch"] = branch_label
        
        # IP Address
        ip_label = QLabel(f"IP: {self.get_ip_address()}")
        font = ip_label.font()
        font.setPointSize(10)
        font.setBold(True)
        ip_label.setFont(font)
        ip_label.setStyleSheet("""
            QLabel {
                color: #495057;
                padding: 6px 12px;
                background-color: #e9ecef;
                border-radius: 4px;
            }
        """)
        layout.addWidget(ip_label)
        self.status_labels["IP"] = ip_label
        
        self.setLayout(layout)
        self.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #ffffff, stop:1 #f8f9fa);
                border-bottom: 2px solid #dee2e6;
            }
        """)
    
    def add_status_item(self, layout, name, initial_value, labels_dict):
        """Add a status indicator to the layout."""
        label = QLabel(f"{name}: {initial_value}")
        font = label.font()
        font.setPointSize(10)
        font.setBold(True)
        label.setFont(font)
        label.setStyleSheet("""
            QLabel {
                color: #495057;
                padding: 6px 12px;
                background-color: #e9ecef;
                border-radius: 4px;
            }
        """)
        layout.addWidget(label)
        labels_dict[name] = label
    
    def update_status(self, name: str, value: str, color: str = "#495057"):
        """Update a status indicator.
        
        Args:
            name: Status name (e.g., "Sensor Power", "I²C")
            value: Status value (e.g., "ON", "OK", "ERROR")
            color: Text color (default: gray)
        """
        if name in self.status_labels:
            label = self.status_labels[name]
            name_part = name
            label.setText(f"{name_part}: {value}")
            
            # Determine background color based on status
            if color == "#4CAF50" or "OK" in value.upper() or "ON" in value.upper():
                bg_color = "#d4edda"
                border_color = "#c3e6cb"
            elif "#ff9800" in color or "NOT" in value.upper():
                bg_color = "#fff3cd"
                border_color = "#ffeaa7"
            elif "#f44336" in color or "ERROR" in value.upper():
                bg_color = "#f8d7da"
                border_color = "#f5c6cb"
            else:
                bg_color = "#e9ecef"
                border_color = "#dee2e6"
            
            label.setStyleSheet(f"""
                QLabel {{
                    color: {color};
                    padding: 6px 12px;
                    background-color: {bg_color};
                    border: 1px solid {border_color};
                    border-radius: 4px;
                    font-weight: bold;
                }}
            """)
    
    def get_branch_color(self, branch: str) -> str:
        """Get color for branch indicator based on branch type.
        
        Args:
            branch: Branch name
            
        Returns:
            str: Color hex code
        """
        branch_lower = branch.lower()
        if branch_lower == "prod" or branch_lower.startswith("prod"):
            return "#d32f2f"  # Red for production
        elif branch_lower == "dev" or branch_lower.startswith("dev"):
            return "#f57c00"  # Orange for development
        elif branch_lower.startswith("feature/"):
            return "#1976d2"  # Blue for features
        else:
            return "#616161"  # Gray for unknown/other
    
    def get_ip_address(self) -> str:
        """Get the primary IP address of the system."""
        try:
            # Connect to a remote address to determine local IP
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.settimeout(0.1)  # Add timeout to prevent blocking
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except Exception:
            return "N/A"

