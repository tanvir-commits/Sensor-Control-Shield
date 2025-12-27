"""Analog voltage readout section."""

from PySide6.QtWidgets import QGroupBox, QVBoxLayout, QLabel
from PySide6.QtCore import Qt
from typing import Dict, Optional


class AnalogSection(QGroupBox):
    """Section displaying 4 analog voltage channels."""
    
    def __init__(self, parent=None):
        super().__init__("Analog Voltages", parent)
        self.channel_labels = {}
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the UI layout."""
        layout = QVBoxLayout()
        layout.setSpacing(12)
        layout.setContentsMargins(15, 10, 15, 15)
        
        # Create labels for each ADC channel
        for channel in range(4):
            label = QLabel(f"ADC{channel}: --.-- V")
            label.setMinimumHeight(50)
            label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            
            # Modern typography
            font = label.font()
            font.setPointSize(14)
            font.setBold(True)
            font.setFamily("Segoe UI, Arial, sans-serif")
            label.setFont(font)
            
            # Modern card-style design
            label.setStyleSheet("""
                QLabel {
                    background-color: #f8f9fa;
                    border: 2px solid #e9ecef;
                    border-radius: 6px;
                    padding: 12px 16px;
                    color: #495057;
                }
            """)
            
            self.channel_labels[channel] = label
            layout.addWidget(label)
        
        layout.addStretch()
        self.setLayout(layout)
    
    def update_readings(self, readings: Dict[int, Optional[float]]):
        """Update voltage readings for all channels.
        
        Args:
            readings: Dictionary mapping channel (0-3) to voltage value or None
        """
        for channel, voltage in readings.items():
            if channel not in self.channel_labels:
                continue
            
            label = self.channel_labels[channel]
            
            if voltage is None:
                label.setText(f"ADC{channel}: --.-- V")
                label.setStyleSheet("""
                    QLabel {
                        background-color: #f8f9fa;
                        border: 2px solid #e9ecef;
                        border-radius: 6px;
                        padding: 12px 16px;
                        color: #adb5bd;
                    }
                """)
            else:
                label.setText(f"ADC{channel}: {voltage:.3f} V")
                # Color based on voltage level
                if voltage > 4.0:
                    bg_color = "#d4edda"
                    border_color = "#28a745"
                    text_color = "#155724"
                elif voltage > 2.0:
                    bg_color = "#d1ecf1"
                    border_color = "#17a2b8"
                    text_color = "#0c5460"
                else:
                    bg_color = "#fff3cd"
                    border_color = "#ffc107"
                    text_color = "#856404"
                
                label.setStyleSheet(f"""
                    QLabel {{
                        background-color: {bg_color};
                        border: 2px solid {border_color};
                        border-radius: 6px;
                        padding: 12px 16px;
                        color: {text_color};
                        font-weight: bold;
                    }}
                """)

