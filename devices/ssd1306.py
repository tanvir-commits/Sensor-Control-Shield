"""SSD1306 OLED display plugin."""

import os
from typing import Optional
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                               QPushButton, QTextEdit, QGroupBox, QFileDialog,
                               QListWidget, QListWidgetItem, QTabWidget)
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
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
        widget.setMinimumHeight(900)  # Make window taller
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(20, 15, 20, 20)
        
        # Title
        title = QLabel("SSD1306 OLED Display Test")
        title.setStyleSheet("font-size: 22pt; font-weight: bold; padding: 15px;")
        layout.addWidget(title)
        
        # Tab widget for different display modes
        tabs = QTabWidget()
        tabs.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #ddd;
                border-radius: 4px;
                background: white;
            }
            QTabBar::tab {
                padding: 12px 20px;
                margin-right: 2px;
                font-size: 14pt;
                font-weight: bold;
            }
            QTabBar::tab:selected {
                background: #007bff;
                color: white;
            }
        """)
        
        # Text display tab
        text_tab = self._create_text_tab()
        tabs.addTab(text_tab, "Text Display")
        
        # Image display tab
        image_tab = self._create_image_tab()
        tabs.addTab(image_tab, "Image Display")
        
        layout.addWidget(tabs)
        widget.setLayout(layout)
        
        return widget
    
    def _create_text_tab(self) -> QWidget:
        """Create the text display tab."""
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(20, 15, 20, 20)
        
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
    
    def _create_image_tab(self) -> QWidget:
        """Create the image display tab."""
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(20, 15, 20, 20)
        
        # Info
        info_label = QLabel(
            "Select an image file to display on the OLED screen.\n\n"
            "Image Requirements:\n"
            "• Format: PNG, JPG, or BMP\n"
            "• Recommended size: 128x64 pixels (or 128x32 for smaller displays)\n"
            "• Images will be automatically resized and converted to monochrome\n"
            "• Best results with high contrast images"
        )
        info_label.setWordWrap(True)
        info_label.setStyleSheet("padding: 15px; color: #666; font-size: 14pt; background-color: #f8f9fa; border-radius: 6px;")
        layout.addWidget(info_label)
        
        # Sample images group
        samples_group = QGroupBox("Sample Images")
        samples_group.setStyleSheet("font-size: 18pt; font-weight: bold; padding-top: 20px;")
        samples_layout = QVBoxLayout()
        
        # List of sample images
        sample_list = QListWidget()
        sample_list.setMaximumHeight(200)
        sample_list.setStyleSheet("""
            QListWidget {
                border: 2px solid #dee2e6;
                border-radius: 6px;
                font-size: 14pt;
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
        """)
        
        # Load sample images from devices/ssd1306_samples directory
        samples_dir = os.path.join(os.path.dirname(__file__), 'ssd1306_samples')
        if os.path.exists(samples_dir):
            for filename in sorted(os.listdir(samples_dir)):
                if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp')):
                    item = QListWidgetItem(filename)
                    sample_list.addItem(item)
        
        if sample_list.count() == 0:
            no_samples = QLabel("No sample images found.\nAdd images to devices/ssd1306_samples/")
            no_samples.setStyleSheet("padding: 10px; color: #666; font-size: 12pt;")
            samples_layout.addWidget(no_samples)
        else:
            samples_layout.addWidget(sample_list)
        
        samples_group.setLayout(samples_layout)
        layout.addWidget(samples_group)
        
        # File browser button
        browse_button = QPushButton("Browse for Image File...")
        browse_button.setMinimumHeight(50)
        browse_button.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #6c757d, stop:1 #5a6268);
                color: white;
                border: none;
                border-radius: 6px;
                padding: 12px;
                font-size: 14pt;
                font-weight: bold;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #5a6268, stop:1 #495057);
            }
        """)
        
        # Display button
        display_button = QPushButton("Display Image on Screen")
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
        status_label = QLabel("Ready - Select an image")
        status_label.setStyleSheet("padding: 10px; font-size: 14pt; color: #666;")
        
        # Selected image path
        selected_image_path = [None]  # Use list to allow modification in nested function
        
        def browse_image():
            """Open file dialog to select image."""
            # Get sample images directory path
            samples_dir = os.path.join(os.path.dirname(__file__), 'ssd1306_samples')
            # Use samples directory as starting location, fallback to home if it doesn't exist
            start_dir = samples_dir if os.path.exists(samples_dir) else os.path.expanduser("~")
            
            file_path, _ = QFileDialog.getOpenFileName(
                widget,
                "Select Image File",
                start_dir,
                "Image Files (*.png *.jpg *.jpeg *.bmp);;All Files (*)"
            )
            if file_path:
                selected_image_path[0] = file_path
                status_label.setText(f"Selected: {os.path.basename(file_path)}")
                status_label.setStyleSheet("padding: 10px; font-size: 14pt; color: #28a745; font-weight: bold;")
                display_button.setEnabled(True)
        
        def on_sample_selected(item: QListWidgetItem):
            """Handle sample image selection."""
            if item:
                filename = item.text()
                file_path = os.path.join(samples_dir, filename)
                if os.path.exists(file_path):
                    selected_image_path[0] = file_path
                    status_label.setText(f"Selected: {filename}")
                    status_label.setStyleSheet("padding: 10px; font-size: 14pt; color: #28a745; font-weight: bold;")
                    display_button.setEnabled(True)
        
        def display_image():
            """Display selected image on OLED screen."""
            image_path = selected_image_path[0]
            
            if not image_path or not os.path.exists(image_path):
                status_label.setText("⚠ Please select an image first")
                status_label.setStyleSheet("padding: 10px; font-size: 14pt; color: #ffc107; font-weight: bold;")
                return
            
            try:
                import board
                import adafruit_ssd1306
                from PIL import Image, ImageOps
                
                # Create I2C bus
                i2c = board.I2C()
                
                # Create SSD1306 display instance
                # Try 128x64 first, fallback to 128x32
                try:
                    display = adafruit_ssd1306.SSD1306_I2C(128, 64, i2c, addr=self.address)
                    display_width, display_height = 128, 64
                except:
                    display = adafruit_ssd1306.SSD1306_I2C(128, 32, i2c, addr=self.address)
                    display_width, display_height = 128, 32
                
                # Load and process image
                img = Image.open(image_path)
                original_size = f"{img.width}x{img.height}"
                
                # Convert to grayscale if needed
                if img.mode != 'L':
                    img = img.convert('L')
                
                # Resize to fit display (maintain aspect ratio, crop to fit)
                img.thumbnail((display_width, display_height), Image.Resampling.LANCZOS)
                resized_size = f"{img.width}x{img.height}"
                
                # Create a new image with exact display size
                display_img = Image.new('1', (display_width, display_height), 0)
                
                # Calculate position to center the image
                x_offset = (display_width - img.width) // 2
                y_offset = (display_height - img.height) // 2
                
                # Paste the resized image onto the display image
                # Convert to 1-bit using threshold (128)
                img_1bit = img.point(lambda x: 255 if x > 128 else 0, mode='1')
                display_img.paste(img_1bit, (x_offset, y_offset))
                
                # Display the image
                display.image(display_img)
                display.show()
                
                filename = os.path.basename(image_path)
                status_msg = f"✓ Image displayed successfully!\n"
                status_msg += f"Original: {original_size} → Display: {resized_size} ({display_width}x{display_height})"
                status_label.setText(status_msg)
                status_label.setStyleSheet("padding: 10px; font-size: 12pt; color: #28a745; font-weight: bold;")
                
            except ImportError as e:
                missing_lib = str(e).split("'")[1] if "'" in str(e) else "adafruit-ssd1306"
                status_label.setText(f"⚠ Library not installed: {missing_lib}\nInstall with: pip3 install adafruit-circuitpython-ssd1306 pillow")
                status_label.setStyleSheet("padding: 10px; font-size: 12pt; color: #ffc107; font-weight: bold;")
            except Exception as e:
                error_msg = str(e)[:50]
                status_label.setText(f"✗ Error: {error_msg}")
                status_label.setStyleSheet("padding: 10px; font-size: 14pt; color: #dc3545; font-weight: bold;")
                import traceback
                print(f"SSD1306 image display error: {e}", file=__import__('sys').stderr)
                traceback.print_exc()
        
        # Connect signals
        browse_button.clicked.connect(browse_image)
        sample_list.itemClicked.connect(on_sample_selected)
        display_button.clicked.connect(display_image)
        display_button.setEnabled(False)
        
        layout.addWidget(browse_button)
        layout.addWidget(display_button)
        layout.addWidget(status_label)
        layout.addStretch()
        widget.setLayout(layout)
        
        return widget

