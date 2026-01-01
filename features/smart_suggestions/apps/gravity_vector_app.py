"""Gravity Vector Display app - MPU6050 + LCD display.

Shows gravity direction as an arrow pointing toward the ground.
Perfect for desk demos - just tilt the device slightly to see the arrow move.
"""

import math
from typing import Optional
from ..app_framework import BaseApp
from ..device_detector import DeviceInfo
from ..display.display_factory import DisplayFactory
from ..display.display_interface import DisplayInterface


class GravityVectorApp(BaseApp):
    """Gravity Vector Display - shows gravity direction as arrow."""
    
    def __init__(self):
        super().__init__()
        self.update_interval = 50  # 20 Hz for smooth updates
        self.mpu6050_device: Optional[DeviceInfo] = None
        self.lcd_device: Optional[DeviceInfo] = None
        self.mpu6050 = None
        self.display: Optional[DisplayInterface] = None
        
        # Display dimensions (will be set from display)
        self.display_width = 128
        self.display_height = 64
        self.center_x = 64
        self.center_y = 32
    
    def _initialize(self) -> bool:
        """Initialize MPU6050 and LCD."""
        try:
            # Find devices
            self.mpu6050_device = self.find_device("IMU")
            self.lcd_device = self.find_device("DISPLAY")
            
            if not self.mpu6050_device:
                print("GravityVectorApp: MPU6050 not found")
                return False
            
            if not self.lcd_device:
                print("GravityVectorApp: LCD display not found")
                return False
            
            # Initialize MPU6050
            if not self._init_mpu6050():
                print("GravityVectorApp: Failed to initialize MPU6050")
                return False
            
            # Initialize LCD
            if not self._init_lcd():
                print("GravityVectorApp: Failed to initialize LCD")
                return False
            
            # Draw initial display
            self._draw_gravity_vector()
            
            return True
        
        except Exception as e:
            print(f"GravityVectorApp initialization error: {e}")
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
            print(f"GravityVectorApp: MPU6050 init error: {e}")
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
            print(f"GravityVectorApp: Basic MPU6050 init error: {e}")
            return False
    
    def _read_mpu6050_accel(self) -> tuple:
        """Read accelerometer data from MPU6050.
        
        Returns:
            (x, y, z) accelerometer values in g
        """
        try:
            if hasattr(self.mpu6050, 'acceleration'):
                # adafruit library
                accel = self.mpu6050.acceleration
                # Convert m/s^2 to g (1g = 9.8 m/s^2)
                return (accel[0] / 9.8, accel[1] / 9.8, accel[2] / 9.8)
            
            elif hasattr(self.mpu6050, 'get_accel_data'):
                # mpu6050-raspberrypi library
                accel = self.mpu6050.get_accel_data()
                return (accel['x'], accel['y'], accel['z'])
            
            else:
                # Basic I2C read
                return self._read_mpu6050_accel_basic()
        
        except Exception as e:
            print(f"GravityVectorApp: Error reading MPU6050: {e}")
            return (0.0, 0.0, 1.0)  # Default: gravity down
    
    def _read_mpu6050_accel_basic(self) -> tuple:
        """Basic I2C accelerometer read."""
        try:
            # MPU6050 accelerometer registers start at 0x3B
            data = self.mpu6050_bus.read_i2c_block_data(self.mpu6050_addr, 0x3B, 6)
            
            # Convert to signed integers (16-bit, two's complement)
            accel_x = (data[0] << 8 | data[1])
            if accel_x > 32767:
                accel_x -= 65536
            accel_x = accel_x / 16384.0  # Convert to g (FS_SEL=0, ±2g range)
            
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
            print(f"GravityVectorApp: Basic MPU6050 read error: {e}")
            return (0.0, 0.0, 1.0)  # Return 1g down when flat
    
    def _init_lcd(self) -> bool:
        """Initialize LCD display using display abstraction layer."""
        try:
            from PIL import Image, ImageDraw, ImageFont
            
            # Create display using factory
            self.display = DisplayFactory.create_display(self.lcd_device)
            if not self.display:
                print("GravityVectorApp: Failed to create display adapter")
                return False
            
            # Get display dimensions
            self.display_width, self.display_height = self.display.get_size()
            self.center_x = self.display_width // 2
            self.center_y = self.display_height // 2
            
            # Create image and draw context
            self.image = Image.new('1', (self.display_width, self.display_height))
            self.draw = ImageDraw.Draw(self.image)
            
            # Try to load font
            try:
                self.font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 10)
            except:
                try:
                    self.font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 10)
                except:
                    self.font = ImageFont.load_default()
            
            # Clear display
            self.display.clear()
            
            return True
        
        except Exception as e:
            print(f"GravityVectorApp: LCD init error: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def update(self) -> None:
        """Update gravity vector display."""
        if not self.running:
            return
        
        try:
            # Read accelerometer
            accel_x, accel_y, accel_z = self._read_mpu6050_accel()
            
            # Draw gravity vector
            self._draw_gravity_vector(accel_x, accel_y, accel_z)
        
        except Exception as e:
            print(f"GravityVectorApp update error: {e}")
    
    def _draw_gravity_vector(self, accel_x=0.0, accel_y=0.0, accel_z=1.0):
        """Draw gravity vector as arrow pointing toward ground."""
        try:
            # Clear image
            self.draw.rectangle(
                (0, 0, self.display_width, self.display_height),
                fill=0
            )
            
            # Calculate gravity vector direction
            # Gravity points opposite to acceleration when stationary
            # When flat: accel = (0, 0, 1g) → gravity = (0, 0, -1g) → points down
            # We'll use the accelerometer reading directly (it already points opposite to gravity)
            gravity_x = -accel_x
            gravity_y = -accel_y
            gravity_z = -accel_z
            
            # Calculate magnitude
            magnitude = math.sqrt(gravity_x**2 + gravity_y**2 + gravity_z**2)
            if magnitude < 0.1:
                magnitude = 0.1  # Avoid division by zero
            
            # Normalize for display (use X and Y components, Z is depth)
            # Project onto X-Y plane
            norm_x = gravity_x / magnitude
            norm_y = gravity_y / magnitude
            
            # Calculate arrow length (scale to fit display)
            arrow_length = min(self.display_width, self.display_height) * 0.35
            
            # Calculate arrow endpoint
            arrow_x = self.center_x + norm_x * arrow_length
            arrow_y = self.center_y + norm_y * arrow_length
            
            # Draw center point
            center_radius = 2
            self.draw.ellipse(
                (
                    self.center_x - center_radius,
                    self.center_y - center_radius,
                    self.center_x + center_radius,
                    self.center_y + center_radius
                ),
                fill=1
            )
            
            # Draw arrow line
            self.draw.line(
                (self.center_x, self.center_y, arrow_x, arrow_y),
                fill=1,
                width=2
            )
            
            # Draw arrowhead
            # Calculate angle
            angle = math.atan2(norm_y, norm_x)
            arrowhead_size = 6
            
            # Arrowhead points
            head_x1 = arrow_x - arrowhead_size * math.cos(angle - math.pi/6)
            head_y1 = arrow_y - arrowhead_size * math.sin(angle - math.pi/6)
            head_x2 = arrow_x - arrowhead_size * math.cos(angle + math.pi/6)
            head_y2 = arrow_y - arrowhead_size * math.sin(angle + math.pi/6)
            
            # Draw arrowhead triangle
            self.draw.polygon(
                [(arrow_x, arrow_y), (head_x1, head_y1), (head_x2, head_y2)],
                fill=1
            )
            
            # Draw acceleration values
            text_y = 2
            self.draw.text((2, text_y), f"X:{accel_x:+.2f}g", font=self.font, fill=1)
            text_y += 12
            self.draw.text((2, text_y), f"Y:{accel_y:+.2f}g", font=self.font, fill=1)
            text_y += 12
            self.draw.text((2, text_y), f"Z:{accel_z:+.2f}g", font=self.font, fill=1)
            
            # Draw magnitude
            text_y += 12
            self.draw.text((2, text_y), f"Mag:{magnitude:.2f}g", font=self.font, fill=1)
            
            # Update display
            self.display.show_image(self.image)
        
        except Exception as e:
            print(f"GravityVectorApp draw error: {e}")
    
    def _cleanup(self) -> None:
        """Cleanup resources."""
        try:
            # Clear display using abstraction layer
            if self.display:
                self.display.clear()
                self.display.cleanup()
                self.display = None
            
            # Close I2C bus if using basic access
            if hasattr(self, 'mpu6050_bus'):
                try:
                    self.mpu6050_bus.close()
                except:
                    pass
        
        except Exception as e:
            print(f"GravityVectorApp cleanup error: {e}")


