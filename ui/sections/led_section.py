"""LED output control section."""

from PySide6.QtWidgets import QGroupBox, QGridLayout, QPushButton
from PySide6.QtCore import Qt, Signal
from typing import Optional


class LEDSection(QGroupBox):
    """Section for controlling 4 LED outputs."""
    
    # Signal emitted when LED state changes: (led_id, state)
    led_changed = Signal(int, bool)
    
    def __init__(self, parent=None):
        super().__init__("LED Outputs", parent)
        self.led_buttons = {}
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the UI layout."""
        layout = QGridLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(15, 10, 15, 15)
        
        # Create toggle buttons for 4 LEDs in a 2x2 grid
        for i, led_id in enumerate([1, 2, 3, 4]):
            row = i // 2
            col = i % 2
            
            button = QPushButton(f"LED{led_id}")
            button.setCheckable(True)
            button.setMinimumSize(100, 70)
            
            # Modern font
            font = button.font()
            font.setPointSize(12)
            font.setBold(True)
            font.setFamily("Segoe UI, Arial, sans-serif")
            button.setFont(font)
            
            button.setStyleSheet(self._get_button_style(False))
            button.toggled.connect(lambda checked, lid=led_id: self._on_led_toggled(lid, checked))
            
            self.led_buttons[led_id] = button
            layout.addWidget(button, row, col)
        
        self.setLayout(layout)
    
    def _get_button_style(self, is_on: bool) -> str:
        """Get button style based on state."""
        if is_on:
            return """
                QPushButton {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #4CAF50, stop:1 #45a049);
                    color: white;
                    border: none;
                    border-radius: 8px;
                    font-weight: bold;
                    padding: 8px;
                }
                QPushButton:hover {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #5CBF60, stop:1 #4CAF50);
                }
                QPushButton:pressed {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #3d8f41, stop:1 #357a38);
                }
            """
        else:
            return """
                QPushButton {
                    background-color: #e9ecef;
                    color: #6c757d;
                    border: 2px solid #dee2e6;
                    border-radius: 8px;
                    font-weight: bold;
                    padding: 8px;
                }
                QPushButton:hover {
                    background-color: #dee2e6;
                    border-color: #adb5bd;
                }
                QPushButton:pressed {
                    background-color: #ced4da;
                }
            """
    
    def _on_led_toggled(self, led_id: int, state: bool):
        """Handle LED toggle."""
        button = self.led_buttons[led_id]
        button.setStyleSheet(self._get_button_style(state))
        self.led_changed.emit(led_id, state)
    
    def set_led_state(self, led_id: int, state: bool):
        """Set LED state programmatically (without emitting signal)."""
        if led_id in self.led_buttons:
            button = self.led_buttons[led_id]
            button.blockSignals(True)
            button.setChecked(state)
            button.setStyleSheet(self._get_button_style(state))
            button.blockSignals(False)

