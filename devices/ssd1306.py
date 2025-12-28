"""SSD1306 OLED display plugin."""

from typing import Optional
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                               QPushButton, QLineEdit, QTextEdit, QGroupBox)
from .base import DevicePlugin


class SSD1306Plugin(DevicePlugin):
    """Plugin for SSD1306/SSD1309/SH1106 OLED displays."""
    
    addresses = [0x3C, 0x3D]
    name = "SSD1306"
    manufacturer = "Solomon Systech"
    description = "128x64 or 128x32 OLED display"
    
    def detect(self) -> bool:
        """Detect if SSD1306 is present."""
        try:
            import smbus2
            bus = smbus2.SMBus(self.bus)
            # Try to read from device (simple detection)
            bus.write_quick(self.address)
            bus.close()
            return True
        except Exception:
            return False
    
    def get_info(self) -> dict:
        """Get device information."""
        info = super().get_info()
        info.update({
            "resolution": "128x64 or 128x32 pixels",
            "interface": "I2C",
            "color": "Monochrome (white/blue)",
            "datasheet": "https://cdn-shop.adafruit.com/datasheets/SSD1306.pdf",
        })
        return info
    
    def get_test_ui(self) -> Optional[QWidget]:
        """Get test interface for SSD1306."""
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(20, 15, 20, 20)
        
        # Title
        title = QLabel("SSD1306 OLED Display Test")
        title.setStyleSheet("font-size: 22pt; font-weight: bold; padding: 15px;")
        layout.addWidget(title)
        
        # Info
        info_label = QLabel(
            "Type text below and click 'Display on Screen' to show it on the OLED display.\n"
            "The text will be displayed in real-time."
        )
        info_label.setWordWrap(True)
        info_label.setStyleSheet("padding: 15px; color: #666; font-size: 16pt;")
        layout.addWidget(info_label)
        
        # Text input group
        input_group = QGroupBox("Text Input")
        input_group.setStyleSheet("font-size: 18pt; font-weight: bold; padding-top: 20px;")
        input_layout = QVBoxLayout()
        input_layout.setSpacing(10)
        
        # Multi-line text input
        text_input = QTextEdit()
        text_input.setPlaceholderText("Enter text to display on the OLED screen...\n\nSupports multiple lines.\nText will be wrapped automatically.")
        text_input.setMinimumHeight(150)
        text_input.setStyleSheet("""
            QTextEdit {
                font-size: 14pt;
                padding: 10px;
                border: 2px solid #dee2e6;
                border-radius: 6px;
            }
        """)
        input_layout.addWidget(text_input)
        
        input_group.setLayout(input_layout)
        layout.addWidget(input_group)
        
        # Display button
        display_button = QPushButton("Display on Screen")
        display_button.setMinimumHeight(60)
        display_button.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #007bff, stop:1 #0056b3);
                color: white;
                border: none;
                border-radius: 6px;
                padding: 15px;
                font-size: 18pt;
                font-weight: bold;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #0056b3, stop:1 #004085);
            }
            QPushButton:pressed {
                background: #004085;
            }
        """)
        
        # Status label
        status_label = QLabel("Ready")
        status_label.setStyleSheet("padding: 10px; font-size: 14pt; color: #666;")
        layout.addWidget(status_label)
        
        # Connect button to display function
        def display_text():
            """Display text on the OLED screen."""
            text = text_input.toPlainText().strip()
            
            if not text:
                status_label.setText("⚠ Please enter some text first")
                status_label.setStyleSheet("padding: 10px; font-size: 14pt; color: #ffc107; font-weight: bold;")
                return
            
            try:
                # Import required libraries
                import board
                import adafruit_ssd1306
                from PIL import Image, ImageDraw, ImageFont
                
                # Create I2C bus
                i2c = board.I2C()
                
                # Create SSD1306 display instance
                # Try 128x64 first, fallback to 128x32
                try:
                    display = adafruit_ssd1306.SSD1306_I2C(128, 64, i2c, addr=self.address)
                except:
                    display = adafruit_ssd1306.SSD1306_I2C(128, 32, i2c, addr=self.address)
                
                # Clear display
                display.fill(0)
                display.show()
                
                # Create image and draw text
                width = display.width
                height = display.height
                image = Image.new('1', (width, height))
                draw = ImageDraw.Draw(image)
                
                # Try to load a font, fallback to default
                try:
                    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 12)
                except:
                    font = ImageFont.load_default()
                
                # Split text into lines and draw
                lines = text.split('\n')
                y_offset = 0
                line_height = 12
                
                for line in lines:
                    if y_offset + line_height > height:
                        break
                    # Wrap long lines
                    words = line.split(' ')
                    current_line = ""
                    for word in words:
                        test_line = current_line + (" " if current_line else "") + word
                        bbox = draw.textbbox((0, 0), test_line, font=font)
                        if bbox[2] - bbox[0] <= width:
                            current_line = test_line
                        else:
                            if current_line:
                                draw.text((0, y_offset), current_line, font=font, fill=255)
                                y_offset += line_height
                                if y_offset + line_height > height:
                                    break
                            current_line = word
                    if current_line and y_offset + line_height <= height:
                        draw.text((0, y_offset), current_line, font=font, fill=255)
                        y_offset += line_height
                
                # Display the image
                display.image(image)
                display.show()
                
                status_label.setText(f"✓ Text displayed successfully!")
                status_label.setStyleSheet("padding: 10px; font-size: 14pt; color: #28a745; font-weight: bold;")
                
            except ImportError as e:
                # Library not available - provide detailed error
                import sys
                error_details = str(e)
                missing_lib = "adafruit-ssd1306"
                if "adafruit" in error_details.lower():
                    missing_lib = "adafruit-circuitpython-ssd1306"
                elif "PIL" in error_details or "Image" in error_details:
                    missing_lib = "pillow"
                
                error_msg = f"⚠ Library not found: {missing_lib}\n\n"
                error_msg += f"Error: {error_details}\n\n"
                error_msg += f"Install with:\n"
                error_msg += f"pip3 install --break-system-packages {missing_lib}"
                if missing_lib == "adafruit-circuitpython-ssd1306":
                    error_msg += " pillow"
                
                status_label.setText(error_msg)
                status_label.setStyleSheet("padding: 10px; font-size: 12pt; color: #ffc107; font-weight: bold;")
                print(f"SSD1306 import error: {e}", file=sys.stderr)
                import traceback
                traceback.print_exc(file=sys.stderr)
            except Exception as e:
                # Error displaying
                error_msg = str(e)[:50]
                status_label.setText(f"✗ Error: {error_msg}")
                status_label.setStyleSheet("padding: 10px; font-size: 14pt; color: #dc3545; font-weight: bold;")
                import traceback
                print(f"SSD1306 display error: {e}", file=__import__('sys').stderr)
                traceback.print_exc()
        
        display_button.clicked.connect(display_text)
        layout.addWidget(display_button)
        layout.addWidget(status_label)
        
        layout.addStretch()
        widget.setLayout(layout)
        
        return widget

