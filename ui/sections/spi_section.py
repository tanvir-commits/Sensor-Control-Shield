"""SPI bus testing section."""

from PySide6.QtWidgets import QGroupBox, QVBoxLayout, QPushButton, QTextEdit
from PySide6.QtCore import Signal


class SPISection(QGroupBox):
    """Section for SPI bus testing."""
    
    # Signal emitted when test is requested
    test_requested = Signal()
    
    def __init__(self, parent=None):
        super().__init__("SPI", parent)
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the UI layout."""
        layout = QVBoxLayout()
        layout.setSpacing(12)
        layout.setContentsMargins(15, 10, 15, 15)
        
        # Test button
        test_button = QPushButton("Run SPI Test")
        test_button.setMinimumHeight(45)
        font = test_button.font()
        font.setPointSize(11)
        font.setBold(True)
        test_button.setFont(font)
        test_button.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #6f42c1, stop:1 #5a32a3);
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #5a32a3, stop:1 #4a2789);
            }
            QPushButton:pressed {
                background: #4a2789;
            }
        """)
        test_button.clicked.connect(self.test_requested.emit)
        layout.addWidget(test_button)
        
        # Result panel
        self.result_panel = QTextEdit()
        self.result_panel.setReadOnly(True)
        self.result_panel.setMaximumHeight(120)
        self.result_panel.setPlaceholderText("Click 'Run SPI Test' to verify SPI bus...")
        self.result_panel.setStyleSheet("""
            QTextEdit {
                border: 2px solid #dee2e6;
                border-radius: 6px;
                background-color: white;
                padding: 8px;
                font-family: 'Courier New', monospace;
                font-size: 10pt;
            }
        """)
        layout.addWidget(self.result_panel)
        
        layout.addStretch()
        self.setLayout(layout)
    
    def update_results(self, results: dict):
        """Update SPI test results.
        
        Args:
            results: Dictionary with keys like 'enabled', 'activity', 'miso', 'status'
        """
        lines = []
        
        if results.get("enabled"):
            lines.append(f"✓ {results['enabled']}")
        
        if results.get("activity"):
            lines.append(f"  {results['activity']}")
        
        if results.get("miso"):
            status_icon = "✓" if "detected" in results.get("miso", "").lower() else "✗"
            lines.append(f"{status_icon} {results['miso']}")
        
        if results.get("status"):
            status = results['status']
            if status == "OK":
                lines.append(f"\n✓ Status: {status}")
            elif status == "NOT VERIFIED":
                lines.append(f"\n⚠ Status: {status}")
            else:
                lines.append(f"\n✗ Status: {status}")
        
        self.result_panel.setText("\n".join(lines) if lines else "Not verified")

