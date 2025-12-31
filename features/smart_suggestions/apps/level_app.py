"""Level App - MPU6050 tilt sensor + LCD display.

A digital level/bubble level that shows tilt angle on the LCD.
"""

import math
from typing import Optional
from ..app_framework import BaseApp
from ..device_detector import DeviceInfo


class LevelApp(BaseApp):
    """Digital level - shows tilt angle on LCD."""
    
    def __init__(self):
        super().__init__()
        self.update_interval = 100  # 10 Hz for level (smooth but not too fast)
        self.mpu6050_device: Optional[DeviceInfo] = None
        self.lcd_device: Optional[DeviceInfo] = None
        self.mpu6050 = None
        self.display = None
    
    def _initialize(self) -> bool:
        """Initialize MPU6050 and LCD."""
        try:
            # Find devices
            self.mpu6050_device = self.find_device("IMU")
            self.lcd_device = self.find_device("DISPLAY")
            
            if not self.mpu6050_device:
                print("LevelApp: MPU6050 not found")
                return False
            
            if not self.lcd_device:
                print("LevelApp: LCD display not found")
                return False
            
            # Initialize MPU6050
            if not self._init_mpu6050():
                print("LevelApp: Failed to initialize MPU6050")
                return False
            
            # Initialize LCD
            if not self._init_lcd():
                print("LevelApp: Failed to initialize LCD")
                return False
            
            # Draw initial level
            self._draw_level()
            
            return True
        
        except Exception as e:
            print(f"LevelApp initialization error: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def _init_mpu6050(self) -> bool:
        """Initialize MPU6050 sensor."""
        try:
            # Try to use adafruit-circuitpython-mpu6050
            try:
                import board
                import adafruit_mpu6050
                
                i2c = board.I2C()
                self.mpu6050 = adafruit_mpu6050.MPU6050(i2c)
                return True
            
            except ImportError:
                # Fallback: Try mpu6050-raspberrypi
                try:
                    from mpu6050 import mpu6050
                    self.mpu6050 = mpu6050(0x68)
                    return True
                
                except ImportError:
                    # Fallback: Direct I2C access
                    return self._init_mpu6050_basic()
        
        except Exception as e:
            print(f"LevelApp: MPU6050 init error: {e}")
            return False
    
    def _init_mpu6050_basic(self) -> bool:
        """Basic MPU6050 initialization via direct I2C."""
        try:
            import smbus2
            import time
            self.mpu6050_bus = smbus2.SMBus(self.mpu6050_device.bus)
            self.mpu6050_addr = self.mpu6050_device.address
            
            # Wake up MPU6050 (set PWR_MGMT_1 register to 0)
            self.mpu6050_bus.write_byte_data(self.mpu6050_addr, 0x6B, 0)
            time.sleep(0.1)
            
            return True
        except Exception as e:
            print(f"LevelApp: Basic MPU6050 init error: {e}")
            return False
    
    def _read_mpu6050_accel(self) -> tuple:
        """Read accelerometer data from MPU6050."""
        try:
            if hasattr(self.mpu6050, 'acceleration'):
                accel = self.mpu6050.acceleration
                return (accel[0], accel[1], accel[2])
            
            elif hasattr(self.mpu6050, 'get_accel_data'):
                accel = self.mpu6050.get_accel_data()
                return (accel['x'], accel['y'], accel['z'])
            
            else:
                return self._read_mpu6050_accel_basic()
        
        except Exception as e:
            print(f"LevelApp: Error reading MPU6050: {e}")
            return (0.0, 0.0, 9.8)
    
    def _read_mpu6050_accel_basic(self) -> tuple:
        """Basic I2C accelerometer read."""
        try:
            import smbus2
            data = self.mpu6050_bus.read_i2c_block_data(self.mpu6050_addr, 0x3B, 6)
            
            accel_x = (data[0] << 8 | data[1])
            if accel_x > 32767:
                accel_x -= 65536
            accel_x = accel_x / 16384.0
            
            accel_y = (data[2] << 8 | data[3])
            if accel_y > 32767:
                accel_y -= 65536
            accel_y = accel_y / 16384.0
            
            accel_z = (data[4] << 8 | data[5])
            if accel_z > 32767:
                accel_z -= 65536
            accel_z = accel_z / 16384.0
            
            return (accel_x, accel_y, accel_z)
        
        except Exception as e:
            print(f"LevelApp: Basic MPU6050 read error: {e}")
            return (0.0, 0.0, 9.8)
    
    def _init_lcd(self) -> bool:
        """Initialize LCD display."""
        try:
            import board
            import adafruit_ssd1306
            from PIL import Image, ImageDraw, ImageFont
            
            i2c = board.I2C()
            
            try:
                self.display = adafruit_ssd1306.SSD1306_I2C(
                    128, 64, i2c, addr=self.lcd_device.address
                )
                self.display_width = 128
                self.display_height = 64
            except:
                self.display = adafruit_ssd1306.SSD1306_I2C(
                    128, 32, i2c, addr=self.lcd_device.address
                )
                self.display_width = 128
                self.display_height = 32
            
            self.image = Image.new('1', (self.display_width, self.display_height))
            self.draw = ImageDraw.Draw(self.image)
            
            # Try to load font
            try:
                self.font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 12)
            except:
                try:
                    self.font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 12)
                except:
                    self.font = ImageFont.load_default()
            
            self.display.fill(0)
            self.display.show()
            
            return True
        
        except Exception as e:
            print(f"LevelApp: LCD init error: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def update(self) -> None:
        """Update level display."""
        if not self.running:
            return
        
        try:
            # Read accelerometer
            accel_x, accel_y, accel_z = self._read_mpu6050_accel()
            
            # Calculate tilt angles (in degrees)
            # Using atan2 for accurate angle calculation
            tilt_x_deg = math.degrees(math.atan2(accel_x, accel_z))
            tilt_y_deg = math.degrees(math.atan2(accel_y, accel_z))
            
            # Draw level
            self._draw_level(tilt_x_deg, tilt_y_deg)
        
        except Exception as e:
            print(f"LevelApp update error: {e}")
    
    def _draw_level(self, tilt_x=0.0, tilt_y=0.0):
        """Draw level display with tilt angles."""
        try:
            # Clear image
            self.draw.rectangle(
                (0, 0, self.display_width, self.display_height),
                fill=0
            )
            
            # Draw crosshair in center
            center_x = self.display_width // 2
            center_y = self.display_height // 2
            
            # Horizontal line
            self.draw.line(
                (0, center_y, self.display_width, center_y),
                fill=1,
                width=1
            )
            
            # Vertical line
            self.draw.line(
                (center_x, 0, center_x, self.display_height),
                fill=1,
                width=1
            )
            
            # Draw bubble (moves based on tilt)
            # Scale tilt to pixel movement (max ±30 degrees = ±30 pixels)
            bubble_x = center_x + int(tilt_y * 1.0)  # Y tilt moves bubble X
            bubble_y = center_y + int(tilt_x * 1.0)  # X tilt moves bubble Y
            
            # Clamp to display bounds
            bubble_x = max(5, min(self.display_width - 5, bubble_x))
            bubble_y = max(5, min(self.display_height - 5, bubble_y))
            
            # Draw bubble circle
            bubble_radius = 4
            self.draw.ellipse(
                (
                    bubble_x - bubble_radius,
                    bubble_y - bubble_radius,
                    bubble_x + bubble_radius,
                    bubble_y + bubble_radius
                ),
                fill=1
            )
            
            # Draw tilt angle text
            text_x = f"X: {tilt_x:+.1f}°"
            text_y = f"Y: {tilt_y:+.1f}°"
            
            # Get text size
            bbox_x = self.draw.textbbox((0, 0), text_x, font=self.font)
            bbox_y = self.draw.textbbox((0, 0), text_y, font=self.font)
            
            # Draw text at top
            self.draw.text((5, 2), text_x, font=self.font, fill=1)
            self.draw.text((5, 2 + (bbox_x[3] - bbox_x[1]) + 2), text_y, font=self.font, fill=1)
            
            # Update display
            self.display.image(self.image)
            self.display.show()
        
        except Exception as e:
            print(f"LevelApp draw error: {e}")
    
    def _cleanup(self) -> None:
        """Cleanup resources."""
        try:
            if self.display:
                self.display.fill(0)
                self.display.show()
            
            if hasattr(self, 'mpu6050_bus'):
                try:
                    self.mpu6050_bus.close()
                except:
                    pass
        
        except Exception as e:
            print(f"LevelApp cleanup error: {e}")

