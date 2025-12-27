"""Button input indicator section."""

from PySide6.QtWidgets import QGroupBox, QVBoxLayout, QLabel
from PySide6.QtCore import Qt
from typing import Dict


class ButtonSection(QGroupBox):
    """Section displaying 2 button input states."""
    
    def __init__(self, parent=None):
        super().__init__("Buttons", parent)
        self.button_labels = {}
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the UI layout."""
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(15, 10, 15, 15)
        
        # Create indicators for 2 buttons
        for button_id in [1, 2]:
            label = QLabel(f"BTN{button_id}: RELEASED")
            label.setMinimumHeight(70)
            label.setAlignment(Qt.AlignCenter)
            
            # Modern typography
            font = label.font()
            font.setPointSize(13)
            font.setBold(True)
            font.setFamily("Segoe UI, Arial, sans-serif")
            label.setFont(font)
            
            # Initial style (released/grey)
            label.setStyleSheet(self._get_label_style(False))
            
            self.button_labels[button_id] = label
            layout.addWidget(label)
        
        layout.addStretch()
        self.setLayout(layout)
    
    def _get_label_style(self, is_pressed: bool) -> str:
        """Get label style based on button state."""
        if is_pressed:
            return """
                QLabel {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #4CAF50, stop:1 #45a049);
                    color: white;
                    border: none;
                    border-radius: 8px;
                    padding: 12px;
                }
            """
        else:
            return """
                QLabel {
                    background-color: #f8f9fa;
                    color: #6c757d;
                    border: 2px solid #dee2e6;
                    border-radius: 8px;
                    padding: 12px;
                }
            """
    
    def update_states(self, states: Dict[int, bool]):
        """Update button states.
        
        Args:
            states: Dictionary mapping button_id to pressed state
        """
        for button_id, is_pressed in states.items():
            if button_id not in self.button_labels:
                continue
            
            label = self.button_labels[button_id]
            state_text = "PRESSED" if is_pressed else "RELEASED"
            label.setText(f"BTN{button_id}: {state_text}")
            label.setStyleSheet(self._get_label_style(is_pressed))

